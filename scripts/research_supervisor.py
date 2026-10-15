#!/usr/bin/env python3
"""Bounded, resumable launcher for explicit Codex research-worker runs."""
from __future__ import annotations
import argparse, datetime as dt, fcntl, hashlib, json, os, re, shutil, signal, subprocess, sys, tempfile, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE, QUEUE = Path("research/state.json"), Path("research/task_queue.json")
EVENTS = Path("research/supervisor_events.jsonl")
TASK_CANDIDATES = Path("research/task_candidates.json")
SUPERVISOR_STATE = Path("research/supervisor_state.json")
TRACK_ROOT = Path("research/tracks")
TRACKS = ("forecasting", "experiments")

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        if os.path.exists(name): os.unlink(name)

def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush(); os.fsync(f.fileno())

def task_track(task: dict[str, Any]) -> str:
    """Assign every shared-queue task to exactly one logical research lane."""
    explicit = task.get("track")
    if explicit in TRACKS:
        return explicit
    task_id = str(task.get("task_id", ""))
    forecast_prefixes = ("FORECAST", "BROAD-CS", "HISTORICAL", "PAPER3")
    return "forecasting" if task_id.startswith(forecast_prefixes) else "experiments"

def default_supervisor_state(campaign_id: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "status": "ACTIVE",
        "stop_requested": False,
        "created_at": now(),
        "updated_at": now(),
        "quota": {
            "state": "AVAILABLE",
            "source": "not_checked",
            "last_failure_class": None,
            "last_failure_at": None,
            "next_check_at": None,
            "official_reset_at": None,
            "consecutive_quota_failures": 0,
        },
        "usage": {"date_utc": now()[:10], "conservative_worker_seconds": 0.0,
                  "track_worker_seconds": {track: 0.0 for track in TRACKS}},
        "active_workers": [],
        "activation": {
            "id": None,
            "started_at": None,
            "worker_invocations": 0,
            "max_worker_invocations": 1,
            "renewal_count": 0,
        },
        "last_event": None,
    }

def load_supervisor_state(root: Path, campaign_id: str) -> dict[str, Any]:
    path = root / SUPERVISOR_STATE
    if path.is_file():
        value = read_json(path)
        value.setdefault("quota", default_supervisor_state(campaign_id)["quota"])
        value.setdefault("usage", default_supervisor_state(campaign_id)["usage"])
        value.setdefault("active_workers", [])
        value.setdefault("activation", default_supervisor_state(campaign_id)["activation"])
        value.setdefault("stop_requested", False)
        value.setdefault("status", "ACTIVE")
        return value
    value = default_supervisor_state(campaign_id)
    atomic_json(path, value)
    return value

def begin_activation(root: Path, state: dict[str, Any], supervisor: dict[str, Any], max_workers: int) -> dict[str, Any]:
    """Renew only the bounded per-process allowance; lifetime counters never reset."""
    budget = state.setdefault("budget_consumption", {})
    budget.setdefault("activations_started", 0)
    budget["activations_started"] += 1
    activation_id = f"{now()}-pid{os.getpid()}"
    activation = supervisor.setdefault("activation", {})
    activation.update({
        "id": activation_id,
        "started_at": now(),
        "worker_invocations": 0,
        "max_worker_invocations": max(1, int(max_workers)),
        "renewal_count": int(activation.get("renewal_count", 0)) + 1,
    })
    state["last_activation_id"] = activation_id
    append_jsonl(root / EVENTS, {
        "event": "supervisor_activation_started",
        "activation_id": activation_id,
        "activation_worker_limit": activation["max_worker_invocations"],
        "lifetime_worker_invocations": budget.get("worker_invocations_started", 0),
        "timestamp": now(),
    })
    return activation

def sync_track_checkpoints(root: Path, state: dict[str, Any], queue: dict[str, Any], supervisor: dict[str, Any]) -> None:
    """Write derived lane checkpoints; the shared queue remains the source of truth."""
    completed = set(state.get("completed_tasks", []))
    for track in TRACKS:
        tasks = [dict(task, track=task_track(task)) for task in queue.get("tasks", []) if task_track(task) == track]
        track_dir = root / TRACK_ROOT / track
        atomic_json(track_dir / "task_queue.json", {"schema_version": 1, "track": track, "tasks": tasks})
        active = [task["task_id"] for task in tasks if task.get("status") == "running"]
        track_state = {
            "schema_version": 1,
            "track": track,
            "campaign_id": state.get("campaign_id"),
            "status": "RUNNING" if active else ("BLOCKED" if any(task.get("status") == "blocked" for task in tasks) else "IDLE"),
            "active_task_ids": active,
            "completed_task_ids": [task["task_id"] for task in tasks if task["task_id"] in completed or task.get("status") == "completed"],
            "pending_task_ids": [task["task_id"] for task in tasks if task.get("status") in {"pending", "failed"}],
            "blocked_task_ids": [task["task_id"] for task in tasks if task.get("status") == "blocked"],
            "checkpoint_time": state.get("checkpoint_time"),
            "last_supervisor_status": supervisor.get("status"),
        }
        atomic_json(track_dir / "state.json", track_state)

def write_supervisor_state(root: Path, supervisor: dict[str, Any]) -> None:
    supervisor["updated_at"] = now()
    atomic_json(root / SUPERVISOR_STATE, supervisor)

def parse_structured_events(raw: str) -> list[dict[str, Any]]:
    records = []
    for line in raw.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records

def classify_failure(raw: str) -> tuple[str, int | None, str | None]:
    """Return (class, retry-after-seconds, official-reset timestamp) conservatively."""
    records = parse_structured_events(raw)
    structured_errors = []
    for record in records:
        kind = str(record.get("type", ""))
        if kind not in {"error", "turn.failed", "turn.completed"} and not any(k in record for k in ("error", "retry_after_seconds", "reset_at", "rate_limit_reset_at")):
            continue
        if kind == "turn.completed" and not any(k in record for k in ("error", "retry_after_seconds", "reset_at", "rate_limit_reset_at")):
            continue
        if "error" in record:
            structured_errors.append(record.get("error"))
        for key in ("code", "message", "retry_after_seconds", "retry_after", "reset_at", "resets_at", "rate_limit_reset_at"):
            if key in record:
                structured_errors.append(record[key])
    structured = json.dumps(structured_errors, ensure_ascii=False).lower()
    text = raw.lower()
    quota_terms = ("usage_limit", "usage limit", "rate_limit_exceeded", "rate limit exceeded", "too many requests", "quota exceeded")
    # Do not classify policy prose such as "do not bypass rate limits" as a
    # service response. Plain text is accepted only for explicit error wording
    # or HTTP 429; structured provider errors remain the preferred signal.
    explicit_plain_quota = re.search(r"\b(?:429|rate[ _-]?limit(?:ed)?\s+exceeded|quota\s+exceeded|usage\s+limit(?:ed)?\s+reached|too\s+many\s+requests)\b", text)
    auth_terms = ("authentication", "unauthorized", "invalid api key", "login required", "forbidden")
    network_terms = ("connection refused", "network error", "timed out", "dns", "temporarily unavailable")
    if any(term in structured for term in quota_terms) or explicit_plain_quota:
        retry_after = None
        reset_at = None
        for record in records:
            for key in ("retry_after_seconds", "retry_after"):
                value = record.get(key)
                if isinstance(value, (int, float)):
                    retry_after = max(0, int(value)); break
            for key in ("reset_at", "resets_at", "rate_limit_reset_at"):
                value = record.get(key)
                if isinstance(value, (int, float, str)):
                    reset_at = str(value); break
        return "quota", retry_after, reset_at
    combined = structured + " " + text
    if any(term in combined for term in auth_terms):
        return "authentication", None, None
    if any(term in combined for term in network_terms):
        return "network", None, None
    return "worker", None, None

def scientific_validation(task: dict[str, Any], artifact: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Separate a bounded JSON artifact from satisfaction of scientific criteria."""
    mode = task.get("scientific_completion")
    task_id = str(task.get("task_id", ""))
    if mode is None and task_id.startswith("HISTORICAL-OUTCOME"):
        mode = "outcome_label"
    if mode is None:
        # Legacy infrastructure tasks predate the explicit gate. They still
        # require the worker artifact schema, while new tasks must opt into a
        # stricter mode in task_queue.json.
        mode = "legacy_artifact_schema"
    common = ("evidence_tier", "sources_and_data", "method", "uncertainty", "next_falsifiable_action")
    missing = [key for key in common if key not in artifact]
    if mode == "trajectory_audit":
        if "cohort" in artifact and "sources_and_data" in missing:
            missing.remove("sources_and_data")
        if "input_artifacts" in artifact and "sources_and_data" in missing:
            missing.remove("sources_and_data")
        if "selection_provenance" in artifact and "sources_and_data" in missing:
            missing.remove("sources_and_data")
        if "sources_data" in artifact and "sources_and_data" in missing:
            missing.remove("sources_and_data")
        if "protocol" in artifact and "method" in missing:
            missing.remove("method")
        if "frozen_protocol" in artifact and "method" in missing:
            missing.remove("method")
    if mode == "experiment_review" and "uncertainty_and_scope" in artifact and "uncertainty" in missing:
        missing.remove("uncertainty")
    if mode == "diagnostic_audit" and "sources_data" in artifact and "sources_and_data" in missing:
        missing.remove("sources_and_data")
    if mode == "feasibility_decision" and "sources_data" in artifact and "sources_and_data" in missing:
        missing.remove("sources_and_data")
    if mode == "legacy_artifact_schema":
        ok = "evidence_tier" in artifact and ("result" in artifact or "observed_result_or_blocker" in artifact)
    elif mode == "outcome_label":
        gate = artifact.get("paper3_gate", {}) if isinstance(artifact.get("paper3_gate"), dict) else {}
        snapshot = artifact.get("original_13_label_snapshot", {}) if isinstance(artifact.get("original_13_label_snapshot"), dict) else {}
        direct = int(snapshot.get("direct_labels", 0) or 0)
        explicit = int(snapshot.get("explicitly_unresolved_labels", 0) or 0)
        ok = direct > 0 or explicit > 0
        missing = missing + (["observed_result_or_blocker"] if "observed_result_or_blocker" not in artifact else [])
        missing = missing + (["direct_or_explicit_unresolved_label"] if not ok else [])
        if gate.get("status") == "not_eligible_for_comparison":
            ok = False
    elif mode in {"feasibility_decision", "trajectory_audit"}:
        decision = artifact.get("decision")
        observed = artifact.get("observed_result_or_blocker", artifact.get("observed_result"))
        if decision is None and isinstance(observed, dict):
            decision = observed.get("decision")
        trajectory_shape = (
            bool(artifact.get("cohort"))
            or all(key in artifact for key in ("input_artifacts", "protocol", "rows"))
            or all(key in artifact for key in ("selection_provenance", "frozen_protocol", "rows"))
            or all(key in artifact for key in ("source_screen", "followup_audit", "stop_gate"))
        )
        paper3_gate = artifact.get("paper3_gate")
        if paper3_gate is None and isinstance(artifact.get("frozen_protocol"), dict):
            paper3_gate = artifact["frozen_protocol"].get("paper3_gate")
        if paper3_gate is None:
            paper3_gate = artifact.get("stop_gate")
        ok = bool(observed is not None and (decision is not None or mode == "trajectory_audit"))
        if mode == "trajectory_audit":
            ok = ok and trajectory_shape and bool(paper3_gate)
        missing = missing + (["observed_result_or_blocker_or_observed_result"] if observed is None else [])
        missing = missing + (["trajectory_audit_structure"] if mode == "trajectory_audit" and not trajectory_shape else [])
        missing = missing + (["paper3_gate"] if mode == "trajectory_audit" and not paper3_gate else [])
        missing = missing + (["decision_or_observed_result"] if not ok else [])
    elif mode == "planning_audit":
        result = artifact.get("result") if isinstance(artifact.get("result"), dict) else {}
        ok = bool(result.get("provenance_reconciled") and result.get("observed_go_no_go_outcomes_coded"))
        missing = missing + (["audited_provenance_and_outcome_coding"] if not ok else [])
    elif mode == "experiment_result":
        required = ("experiment_id", "hypothesis", "configuration", "summary", "falsification_gate")
        missing = missing + [key for key in required if key not in artifact]
        if "limitations" not in artifact and "uncertainty" in artifact:
            # Bounded experiment reports may use the stronger uncertainty block
            # as their limitations record; do not require duplicate prose.
            pass
        gate = artifact.get("falsification_gate")
        observed = artifact.get("observed_result_or_blocker", artifact.get("observed_result"))
        ok = (all(key in artifact for key in required) and isinstance(gate, dict)
              and bool(gate.get("status")) and observed is not None
              and ("metrics" in artifact or isinstance(artifact.get("summary"), dict)))
        missing = missing + (["observed_result_or_blocker_or_observed_result"] if observed is None else [])
        if not ok and "objective_experiment_result" not in missing:
            missing.append("objective_experiment_result")
    elif mode == "experiment_review":
        method = artifact.get("method") if isinstance(artifact.get("method"), dict) else {}
        checks = method.get("checks") if isinstance(method.get("checks"), dict) else {}
        observed = artifact.get("observed_result_or_blocker")
        ok = bool(observed) and bool(artifact.get("review_conclusion")) and bool(checks) and all(value is True for value in checks.values())
        missing = missing + (["independent_checks_and_review_conclusion"] if not ok else [])
    elif mode == "experiment_reanalysis":
        method = artifact.get("method") if isinstance(artifact.get("method"), dict) else {}
        verification = method.get("verification") if isinstance(method.get("verification"), dict) else {}
        observed = artifact.get("observed_result_or_blocker")
        required_true = ("raw_rows", "recomputed_rows", "all_graph_indices_retained", "raw_recomputation_matches")
        ok = (bool(artifact.get("experiment_id")) and bool(artifact.get("hypothesis")) and bool(observed)
              and all(bool(verification.get(key)) for key in required_true)
              and verification.get("parameter_tuning_after_pilot") is False)
        missing = missing + (["independent_reanalysis_verification"] if not ok else [])
    elif mode == "diagnostic_audit":
        counts = artifact.get("cross_round_counts") if isinstance(artifact.get("cross_round_counts"), dict) else {}
        boundaries = artifact.get("frozen_cohort_boundaries") if isinstance(artifact.get("frozen_cohort_boundaries"), dict) else {}
        causes = artifact.get("cause_comparison")
        selection_rule = artifact.get("next_cohort_selection_rule") if isinstance(artifact.get("next_cohort_selection_rule"), dict) else {}
        direct_positive = counts.get("unique_direct_positive")
        direct_negative = counts.get("unique_direct_negative")
        ok = (bool(boundaries) and isinstance(causes, list) and len(causes) >= 3
              and bool(artifact.get("observed_result_or_blocker"))
              and bool(selection_rule.get("selection_steps"))
              and direct_positive == 0 and direct_negative == 0
              and "not_estimable" in str(counts.get("paper3_score", "")))
        missing = missing + (["cross_round_diagnostic_structure"] if not ok else [])
    else:
        ok = False
        missing.append("recognized_scientific_completion_mode")
    return ok, {"mode": mode, "scientific_success": ok, "missing_or_failed": missing,
                "reason": "scientific criteria satisfied" if ok else "valid artifact does not satisfy scientific success criteria"}

def artifact_summary(task: dict[str, Any], artifact: dict[str, Any], scientific_ok: bool, validation: dict[str, Any]) -> dict[str, Any]:
    observed = artifact.get("observed_result_or_blocker")
    if observed is None:
        observed = artifact.get("observed_result", artifact.get("decision", artifact.get("result")))
    return {
        "artifact": task.get("artifact"),
        "task_id": task.get("task_id"),
        "evidence_level": artifact.get("evidence_level", artifact.get("evidence_tier")),
        "scientific_success": scientific_ok,
        "scientific_validation": validation,
        "observed_result_or_blocker": observed,
        "uncertainty": artifact.get("uncertainty"),
        "next_falsifiable_action": artifact.get("next_falsifiable_action"),
        "timestamp": now(),
    }

def update_scientific_checkpoint(root: Path, state: dict[str, Any], task: dict[str, Any], artifact: dict[str, Any], scientific_ok: bool, validation: dict[str, Any]) -> None:
    summary = artifact_summary(task, artifact, scientific_ok, validation)
    audits = state.setdefault("scientific_artifact_audits", [])
    audits[:] = [row for row in audits if row.get("task_id") != task.get("task_id")]
    audits.append(summary)
    actual = {
        "artifact": task.get("artifact"),
        "evidence_level": artifact.get("evidence_level", artifact.get("evidence_tier", 0)),
        "experiment_id": task.get("experiment_id", f"AUDIT-{task.get('task_id')}"),
        "limitation": "; ".join(validation.get("missing_or_failed", [])) or str(artifact.get("uncertainty", ""))[:500],
        "result": str(summary.get("observed_result_or_blocker"))[:1000],
    }
    results = state.setdefault("actual_experiment_results", [])
    results[:] = [row for row in results if row.get("artifact") != task.get("artifact")]
    results.append(actual)
    state["latest_scientific_increment"] = {
        "kind": "supervisor_validated_worker_checkpoint",
        "task_id": task.get("task_id"),
        "scientific_success": scientific_ok,
        "evidence_level": artifact.get("evidence_level", artifact.get("evidence_tier", 0)),
        "decision": artifact.get("decision"),
        "next_falsifiable_action": artifact.get("next_falsifiable_action"),
    }
    pending = [t for t in read_json(root / QUEUE).get("tasks", []) if t.get("status") in {"pending", "failed"}]
    state["opportunity_ranking"] = [
        {"task_id": t["task_id"], "track": task_track(t),
         "score": round(float(t.get("priority", 0)) * float(t.get("expected_information_gain", 0)) / max(float(t.get("cost_estimate", 1)), .01), 4),
         "scientific_completion": t.get("scientific_completion", "legacy_artifact_schema")}
        for t in sorted(pending, key=lambda x: (-(float(x.get("priority", 0)) * float(x.get("expected_information_gain", 0)) / max(float(x.get("cost_estimate", 1)), .01)), x["task_id"]))
    ]
    state["next_action"] = artifact.get("next_falsifiable_action") or task.get("objective")
    state["pending_tasks"] = [t["task_id"] for t in pending]

def update_human_status(root: Path, task: dict[str, Any], artifact: dict[str, Any], scientific_ok: bool, validation: dict[str, Any]) -> None:
    """Keep a compact, replace-in-place human checkpoint after every worker."""
    path = root / "RESEARCH_STATUS.md"
    if not path.is_file():
        return
    start, end = "<!-- supervisor-auto-checkpoint:start -->", "<!-- supervisor-auto-checkpoint:end -->"
    def readable(value: Any, limit: int = 700) -> str:
        if isinstance(value, dict):
            value = value.get("action") or value.get("summary") or json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value).replace("\n", " ")[:limit]
    observed = artifact.get("observed_result_or_blocker", artifact.get("decision", artifact.get("result")))
    next_action = artifact.get("next_falsifiable_action", "")
    block = (f"{start}\n**Supervisor auto-checkpoint ({now()}):** `{task.get('task_id')}` produced a bounded artifact. "
             f"Scientific success: **{str(scientific_ok).lower()}**; evidence tier: `{artifact.get('evidence_tier', artifact.get('evidence_level', 'unknown'))}`. "
             f"Observed result/blocker: {readable(observed)}  \n"
             f"Next falsifiable action: {readable(next_action)}\n{end}")
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before + block + after, encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")

def reconcile_scientific_completions(root: Path, state: dict[str, Any], queue: dict[str, Any]) -> bool:
    changed = False
    for task in queue.get("tasks", []):
        if task.get("status") not in {"completed", "artifact_only"} or not task.get("scientific_completion"):
            continue
        artifact_path = root / task.get("artifact", "")
        try:
            artifact = read_json(artifact_path)
        except (OSError, ValueError):
            continue
        ok, validation = scientific_validation(task, artifact)
        task["scientific_validation"] = validation
        if ok:
            task.setdefault("last_result", {})["scientific_success"] = True
            task.pop("failure_note", None)
            task.pop("artifact_only", None)
            artifact_only = state.setdefault("artifact_only_tasks", [])
            if task["task_id"] in artifact_only:
                artifact_only.remove(task["task_id"])
            update_scientific_checkpoint(root, state, task, artifact, True, validation)
            changed = True
            if task.get("status") == "artifact_only":
                task["status"] = "completed"
                task["scientific_status"] = "scientifically_completed"
                if task["task_id"] not in state.setdefault("completed_tasks", []):
                    state["completed_tasks"].append(task["task_id"])
                state["current_research_round"] = state.get("current_research_round", 0) + 1
                append_jsonl(root / EVENTS, {"event": "artifact_only_promoted_scientific_validation", "task_id": task["task_id"], "timestamp": now(), "validation": validation})
        elif not ok and task.get("status") == "completed":
            task["status"] = "artifact_only"
            task["scientific_status"] = "artifact_only"
            state.setdefault("artifact_only_tasks", [])
            if task["task_id"] not in state["artifact_only_tasks"]:
                state["artifact_only_tasks"].append(task["task_id"])
            if task["task_id"] in state.get("completed_tasks", []):
                state["completed_tasks"].remove(task["task_id"])
            append_jsonl(root / EVENTS, {"event": "artifact_only_scientific_validation", "task_id": task["task_id"], "timestamp": now(), "validation": validation})
            changed = True
    state["pending_tasks"] = [t["task_id"] for t in queue.get("tasks", []) if t.get("status") in {"pending", "failed"}]
    return changed

def quota_waiting(supervisor: dict[str, Any]) -> bool:
    quota = supervisor.setdefault("quota", {})
    if supervisor.get("status") not in {"QUOTA_PAUSED", "WAITING_FOR_RESET"}:
        return False
    next_check = quota.get("next_check_at")
    if not next_check:
        return False
    try:
        return dt.datetime.fromisoformat(next_check.replace("Z", "+00:00")).timestamp() > time.time()
    except ValueError:
        return False

def next_quota_check(supervisor: dict[str, Any], result: dict[str, Any], attempt: int) -> str:
    quota = supervisor.setdefault("quota", {})
    retry = result.get("retry_after_seconds")
    if retry is None:
        failures = int(quota.get("consecutive_quota_failures", 0))
        retry = min(3600, 300 * (2 ** min(failures, 4)))
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=max(1, int(retry)))).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def eligible_tasks(queue: dict[str, Any], completed: set[str], at: float | None = None) -> list[dict[str, Any]]:
    at = time.time() if at is None else at
    out = []
    for task in queue["tasks"]:
        if task.get("status") not in {"pending", "failed"} or task.get("attempts", 0) >= task.get("max_attempts", 1): continue
        if not set(task.get("dependencies", [])).issubset(completed): continue
        if task.get("retry_after") and dt.datetime.fromisoformat(task["retry_after"].replace("Z", "+00:00")).timestamp() > at: continue
        out.append(task)
    return sorted(out, key=lambda t: (-(t.get("priority", 0) * t.get("expected_information_gain", 0) /
                                        max(t.get("cost_estimate", 1), 0.01)), t["task_id"]))

def proposed_continuations(root: Path, queue: dict[str, Any]) -> list[dict[str, Any]]:
    """Only evidence-gated, nonduplicate, informative tasks may enter the queue."""
    path = root / TASK_CANDIDATES
    if not path.is_file(): return []
    entries = read_json(path).get("candidates", [])
    ids = {t["task_id"] for t in queue["tasks"]}
    keys = {t.get("research_key") for t in queue["tasks"] if t.get("research_key")}
    objectives = {" ".join(t["objective"].lower().split()) for t in queue["tasks"]}
    artifacts = {t.get("artifact") for t in queue["tasks"]}
    proposed = []
    for entry in entries:
        task = entry["task"]
        key = task.get("research_key")
        objective = " ".join(task["objective"].lower().split())
        if not key or task["task_id"] in ids or key in keys or objective in objectives: continue
        if task.get("status") != "pending" or not set(task.get("dependencies", [])).issubset(ids): continue
        if task.get("expected_information_gain", 0) / max(task.get("cost_estimate", 1), .01) < .5: continue
        artifact = Path(task.get("artifact", ""))
        if artifact.is_absolute() or ".." in artifact.parts or (root / artifact).exists() or str(artifact) in artifacts: continue
        gates = entry.get("evidence_artifacts", [])
        if not gates or any(Path(g).is_absolute() or ".." in Path(g).parts or not (root / g).is_file() for g in gates): continue
        condition = entry.get("gate_json_equals")
        if condition:
            gate_path = Path(condition["path"])
            if gate_path.is_absolute() or ".." in gate_path.parts or not (root / gate_path).is_file(): continue
            try:
                gate_value: Any = read_json(root / gate_path)
                for part in str(condition["field"]).split("."):
                    if not isinstance(gate_value, dict):
                        gate_value = None
                        break
                    gate_value = gate_value.get(part)
            except (OSError, ValueError): continue
            if gate_value != condition["value"]: continue
        proposed.append(task)
        ids.add(task["task_id"]); keys.add(key); objectives.add(objective); artifacts.add(str(artifact))
    return proposed

def enqueue_continuations(root: Path, state: dict[str, Any], queue: dict[str, Any]) -> int:
    # Generate before the last ready task is consumed, without starting a worker here.
    active = sum(t.get("status") in {"pending", "failed", "running"} for t in queue["tasks"])
    if active > 3: return 0
    proposed = proposed_continuations(root, queue)
    if not proposed: return 0
    queue["tasks"].extend(proposed)
    state.setdefault("pending_tasks", []).extend(t["task_id"] for t in proposed)
    pending = [t for t in queue["tasks"] if t.get("status") in {"pending", "failed"}]
    state["opportunity_ranking"] = [
        {"task_id": t["task_id"], "track": task_track(t),
         "score": round(float(t.get("priority", 0)) * float(t.get("expected_information_gain", 0)) / max(float(t.get("cost_estimate", 1)), .01), 4),
         "scientific_completion": t.get("scientific_completion", "legacy_artifact_schema")}
        for t in sorted(pending, key=lambda x: (-(float(x.get("priority", 0)) * float(x.get("expected_information_gain", 0)) / max(float(x.get("cost_estimate", 1)), .01)), x["task_id"]))
    ]
    for task in proposed:
        append_jsonl(root / EVENTS, {"event": "evidence_gated_task_enqueued", "task_id": task["task_id"], "timestamp": now(),
                                      "research_key": task["research_key"]})
    atomic_json(root / QUEUE, queue); atomic_json(root / STATE, state)
    return len(proposed)

def git_snapshot(root: Path) -> dict[str, str]:
    p = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=root,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    if p.returncode: return {}
    snapshot = {}
    for item in p.stdout.decode("utf-8", "replace").split("\0"):
        if not item: continue
        name = item[3:] if len(item) > 3 else item
        path = root / name
        try:
            if path.is_file(): snapshot[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            elif path.is_symlink(): snapshot[name] = "symlink:" + os.readlink(path)
            else: snapshot[name] = "non-file"
        except OSError: snapshot[name] = "unreadable"
    return snapshot

def parse_session_id(path: Path) -> str | None:
    try:
        for line in path.read_text(errors="replace").splitlines():
            obj = json.loads(line)
            sid = obj.get("session_id") or obj.get("thread_id")
            if sid: return str(sid)
    except (OSError, json.JSONDecodeError): pass
    return None

def worker_prompt(task: dict[str, Any], output_rel: str, attempt: int) -> str:
    return ("You are a bounded scientific research worker. Read AGENTS.md and the current state. Perform only this task; do not publish, commit, change production OpenFindings, modify unrelated files, or claim evidence you did not inspect. Preserve null/negative results. Write one machine-readable JSON artifact at the declared output path, including evidence tier, sources/data, method, observed result or blocker, uncertainty, and next falsifiable action. Do not edit state, queue, ledger, status, or other artifacts; the supervisor owns checkpoints.\n\n"
            f"Task {task['task_id']} (attempt {attempt}/{task.get('max_attempts', 1)}):\nObjective: {task['objective']}\n"
            f"Dependencies: {json.dumps(task.get('dependencies', []))}\n"
            f"Planning-only information-gain estimate: {task.get('expected_information_gain')}\n"
            f"Requirements: {json.dumps(task.get('execution_requirements', []), ensure_ascii=False)}\n"
            f"Success criteria: {json.dumps(task.get('success_criteria', []), ensure_ascii=False)}\nWrite only: {output_rel}\n")

def run_worker(root: Path, task: dict[str, Any], attempt: int, timeout: int, artifact_limit: int, worker_dir: Path, on_start=None) -> dict[str, Any]:
    codex = os.environ.get("RESEARCH_SUPERVISOR_CODEX_BIN") or shutil.which("codex")
    if not codex: return {"exit_code": 127, "error": "codex executable not found", "timed_out": False}
    output_rel = task["artifact"]
    artifact = (root / output_rel).resolve()
    if root.resolve() not in artifact.parents: return {"exit_code": 2, "error": "artifact outside repository", "timed_out": False}
    artifact.parent.mkdir(parents=True, exist_ok=True)
    raw, stderr, final = worker_dir / "events.jsonl", worker_dir / "stderr.txt", worker_dir / "final.txt"
    command = [codex, "exec", "--json", "--approve-for-me", "-C", str(root), "-o", str(final), "-"]
    started = time.monotonic(); timed_out = False
    prior_artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else None
    child_env = os.environ.copy()
    secret_markers = ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY", "PRIVATE_KEY")
    for name in list(child_env):
        if any(marker in name.upper() for marker in secret_markers): child_env.pop(name, None)
    with raw.open("wb") as out, stderr.open("wb") as err:
        proc = subprocess.Popen(command, cwd=root, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True, env=child_env)
        if on_start: on_start(proc.pid)
        # The callback records worker_pid in the supervisor-owned queue. Take
        # the worker-diff baseline after that write, otherwise a supervisor
        # bookkeeping change is misattributed to the child.
        before = git_snapshot(root)
        try: proc.communicate(worker_prompt(task, output_rel, attempt).encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True; os.killpg(proc.pid, signal.SIGTERM)
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(proc.pid, signal.SIGKILL); proc.wait()
    elapsed = round(time.monotonic() - started, 3)
    sizes = {p.name: p.stat().st_size for p in (raw, stderr, final) if p.exists()}
    after = git_snapshot(root)
    changed = {name for name in set(before) | set(after) if before.get(name) != after.get(name)}
    supervisor_paths = {str(p.relative_to(root)) for p in worker_dir.iterdir()}
    # Lane checkpoints are derived supervisor artifacts. Workers may run the
    # mandated dry-run status check, which refreshes these files without
    # changing the canonical queue/state owned by the supervisor.
    supervisor_paths.update({f"research/tracks/{track}/{name}"
                             for track in TRACKS for name in ("state.json", "task_queue.json")})
    # launchd writes these two streams independently of the worker. A
    # concurrent bounded activation must not turn that expected append into a
    # worker-write conflict; canonical state and queue paths remain protected.
    supervisor_paths.update({"research/logs/launchd.out.log", "research/logs/launchd.err.log"})
    unexpected = sorted(changed - {output_rel} - supervisor_paths)
    artifact_ok = artifact.is_file() and artifact.stat().st_size <= artifact_limit
    if artifact_ok and prior_artifact_hash == hashlib.sha256(artifact.read_bytes()).hexdigest():
        artifact_ok = False
    if artifact_ok:
        try:
            json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            artifact_ok = False
    if unexpected: error = "worker changed paths outside declared artifact: " + ", ".join(unexpected[:20])
    elif sum(sizes.values()) > artifact_limit: error = "worker logs exceeded size limit"
    elif not artifact_ok and proc.returncode == 0: error = "worker exited zero but did not produce a new or changed bounded artifact"
    else: error = None
    # Command-execution aggregates can echo AGENTS.md policy text containing
    # words such as "rate limits". Only structured error events, stderr and
    # the final message are valid fallback evidence for quota classification.
    event_errors = []
    for line in raw.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (event.get("type") in {"error", "turn.failed"}
                or "error" in event or "retry_after_seconds" in event
                or "reset_at" in event or "rate_limit_reset_at" in event):
            event_errors.append(json.dumps(event, ensure_ascii=False))
    combined = "\n".join(event_errors) + "\n" + stderr.read_text(errors="replace")[-2000:] + "\n" + (final.read_text(errors="replace") if final.exists() else "")
    failure_class, retry_after_seconds, official_reset_at = classify_failure(combined)
    limited = failure_class == "quota"
    return {"exit_code": proc.returncode, "timed_out": timed_out, "elapsed_seconds": elapsed, "artifact_valid": artifact_ok,
            "artifact_bytes": artifact.stat().st_size if artifact_ok else None, "log_bytes": sizes,
            "session_id": parse_session_id(raw), "error": error, "rate_limited": limited,
            "failure_class": failure_class, "retry_after_seconds": retry_after_seconds,
            "official_reset_at": official_reset_at,
            "command": [Path(codex).name, "exec", "--json", "--approve-for-me"],
            "raw_output_sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="schedule only; never invoke Codex")
    mode.add_argument("--start", action="store_true", help="explicitly authorize bounded workers")
    mode.add_argument("--stop", action="store_true", help="persist a user STOP request; do not start workers")
    mode.add_argument("--resume", action="store_true", help="clear a user STOP request and allow the next bounded run")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--max-rounds", type=int)
    ap.add_argument("--timeout-seconds", type=int)
    args = ap.parse_args(); root = args.repo_root.resolve()
    sp, qp = root / STATE, root / QUEUE
    state, queue = read_json(sp), read_json(qp)
    if args.start and reconcile_scientific_completions(root, state, queue):
        state["checkpoint_time"] = now()
        atomic_json(qp, queue); atomic_json(sp, state)
    supervisor = load_supervisor_state(root, state.get("campaign_id", "research"))
    sync_track_checkpoints(root, state, queue, supervisor)
    if args.stop:
        supervisor["stop_requested"] = True
        supervisor["status"] = "STOPPED_BY_USER"
        supervisor["last_event"] = {"event": "stop_requested", "timestamp": now()}
        state["campaign_status"] = "stopped_by_user"
        state["checkpoint_time"] = now()
        write_supervisor_state(root, supervisor); atomic_json(sp, state)
        sync_track_checkpoints(root, state, queue, supervisor)
        print(json.dumps({"campaign_status": state["campaign_status"], "supervisor_status": supervisor["status"]}, indent=2)); return 0
    if args.resume:
        supervisor["stop_requested"] = False
        supervisor["status"] = "RESUME_CHECK"
        supervisor["last_event"] = {"event": "resume_requested", "timestamp": now()}
        state["campaign_status"] = "active"
        state["checkpoint_time"] = now()
        write_supervisor_state(root, supervisor); atomic_json(sp, state)
        sync_track_checkpoints(root, state, queue, supervisor)
        print(json.dumps({"campaign_status": state["campaign_status"], "supervisor_status": supervisor["status"]}, indent=2)); return 0
    if supervisor.get("stop_requested"):
        supervisor["status"] = "STOPPED_BY_USER"
        state["campaign_status"] = "stopped_by_user"; state["checkpoint_time"] = now()
        write_supervisor_state(root, supervisor); atomic_json(sp, state); sync_track_checkpoints(root, state, queue, supervisor)
        print(json.dumps({"campaign_status": state["campaign_status"], "supervisor_status": supervisor["status"]}, indent=2)); return 0
    if args.start and quota_waiting(supervisor):
        supervisor["status"] = "WAITING_FOR_RESET"
        state["campaign_status"] = "waiting_for_quota_reset"; state["checkpoint_time"] = now()
        write_supervisor_state(root, supervisor); atomic_json(sp, state); sync_track_checkpoints(root, state, queue, supervisor)
        print(json.dumps({"campaign_status": state["campaign_status"], "supervisor_status": supervisor["status"],
                          "next_check_at": supervisor.get("quota", {}).get("next_check_at")}, indent=2)); return 0
    done = set(state.get("completed_tasks", [])) | {t["task_id"] for t in queue["tasks"] if t.get("status") == "completed"}
    ready = eligible_tasks(queue, done)
    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "campaign_status": state.get("campaign_status"), "next_task": ready[0] if ready else None,
                          "scheduled_count": len(ready), "proposed_continuations": [t["task_id"] for t in proposed_continuations(root, queue)],
                          "supervisor_status": supervisor.get("status"), "quota": supervisor.get("quota"),
                          "tracks": {track: sum(task_track(t) == track for t in queue["tasks"]) for track in TRACKS},
                          "worker_invocations": 0}, ensure_ascii=False, indent=2)); return 0
    limits = state.get("budget_consumption", {})
    rounds = args.max_rounds or limits.get("configured_max_rounds", 1)
    max_workers = limits.get("configured_max_worker_invocations", 1)
    activation_worker_limit = limits.get("configured_max_worker_invocations_per_activation", 1)
    timeout = args.timeout_seconds or min(1800, limits.get("configured_max_wall_seconds", 1800))
    max_bytes = int(limits.get("configured_max_artifact_mib", 50) * 1024 * 1024)
    min_free = int(limits.get("minimum_disk_free_mib", 2048) * 1024 * 1024)
    operational = state.setdefault("operational_limits", {})
    # Preserve the legacy per-start worker limit for migrated/test states.
    # max_active_workers is a concurrency invariant; the loop is sequential,
    # so it must not silently reduce the separately configured per-start cap.
    operational.setdefault("max_active_workers", max_workers)
    operational.setdefault("max_daily_worker_seconds", 4 * 60 * 60)
    operational.setdefault("max_track_worker_seconds", 2 * 60 * 60)
    operational.setdefault("max_task_retries", 2)
    operational.setdefault("cooling_off_seconds", 300)
    if not 1 <= rounds <= min(100, limits.get("configured_max_rounds", 1)):
        ap.error("round count exceeds configured campaign limit")
    if not 1 <= timeout <= min(7200, limits.get("configured_max_wall_seconds", 7200)):
        ap.error("timeout exceeds configured campaign limit")
    rdir = root / "research"
    with (rdir / ".supervisor.lock").open("a+") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: print("another supervisor holds the campaign lock", file=sys.stderr); return 3
        # Recover an interrupted manager without discarding its partial artifact.
        state, queue = read_json(sp), read_json(qp)
        if reconcile_scientific_completions(root, state, queue):
            state["checkpoint_time"] = now()
            atomic_json(qp, queue); atomic_json(sp, state)
        recovered = False
        for task in queue["tasks"]:
            if task.get("status") != "running": continue
            pid = task.pop("worker_pid", None)
            if isinstance(pid, int) and pid > 1:
                try:
                    probe = subprocess.run(["ps", "-p", str(pid), "-o", "command="], stdout=subprocess.PIPE,
                                           stderr=subprocess.DEVNULL, text=True, check=False)
                except OSError:
                    probe = None
                if probe and "codex" in probe.stdout.lower():
                    try: os.killpg(pid, signal.SIGTERM)
                    except ProcessLookupError: pass
            task["status"] = "failed" if task.get("attempts", 0) < task.get("max_attempts", 1) else "blocked"
            task["interrupted_at"] = now()
            task["failure_note"] = "supervisor restarted during worker; prior artifact/output preserved for inspection"
            task["retry_after"] = now()
            append_jsonl(root / EVENTS, {"task_id": task["task_id"], "attempt": task.get("attempts"),
                                         "timestamp": now(), "event": "recovered_interrupted_worker", "worker_pid": pid})
            recovered = True
        if recovered:
            state["campaign_status"] = "active"
            state["checkpoint_time"] = now()
            atomic_json(qp, queue); atomic_json(sp, state)
        state, queue = read_json(sp), read_json(qp)
        supervisor = load_supervisor_state(root, state.get("campaign_id", "research"))
        activation_worker_limit = int(state.setdefault("budget_consumption", {}).setdefault(
            "configured_max_worker_invocations_per_activation", activation_worker_limit))
        activation = begin_activation(root, state, supervisor, activation_worker_limit)
        if state.get("campaign_status") in {"paused_worker_budget", "waiting_for_next_activation"}:
            state["campaign_status"] = "active"
        supervisor["status"] = "ACTIVE"
        state["checkpoint_time"] = now()
        atomic_json(sp, state); write_supervisor_state(root, supervisor)
        enqueue_continuations(root, state, queue)
        supervisor = load_supervisor_state(root, state.get("campaign_id", "research"))
        activation = supervisor.setdefault("activation", activation)
        sync_track_checkpoints(root, state, queue, supervisor)
        started, invocations = time.monotonic(), 0
        for _ in range(rounds):
            state, queue = read_json(sp), read_json(qp)
            supervisor = load_supervisor_state(root, state.get("campaign_id", "research"))
            if supervisor.get("stop_requested"):
                supervisor["status"] = "STOPPED_BY_USER"; state["campaign_status"] = "stopped_by_user"; state["checkpoint_time"] = now()
                write_supervisor_state(root, supervisor); atomic_json(sp, state); sync_track_checkpoints(root, state, queue, supervisor); break
            if quota_waiting(supervisor):
                supervisor["status"] = "WAITING_FOR_RESET"; state["campaign_status"] = "waiting_for_quota_reset"; state["checkpoint_time"] = now()
                write_supervisor_state(root, supervisor); atomic_json(sp, state); sync_track_checkpoints(root, state, queue, supervisor); break
            enqueue_continuations(root, state, queue)
            state, queue = read_json(sp), read_json(qp)
            supervisor = load_supervisor_state(root, state.get("campaign_id", "research"))
            done = set(state.get("completed_tasks", [])) | {t["task_id"] for t in queue["tasks"] if t.get("status") == "completed"}
            ready = eligible_tasks(queue, done)
            if not ready:
                state["campaign_status"] = "waiting_for_eligible_task"
                state["next_action"] = "Add or unblock a scientifically justified task; do not invent outcomes."
                supervisor["status"] = "ACTIVE"; state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor); break
            task = ready[0]
            budget = state.setdefault("budget_consumption", {})
            if activation.get("worker_invocations", 0) >= int(activation.get("max_worker_invocations", activation_worker_limit)):
                state["campaign_status"] = "waiting_for_next_activation"
                state["next_action"] = "Wait for the next bounded supervisor activation; lifetime worker history is preserved."
                supervisor["status"] = "ACTIVE"; state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor); break
            if task.get("counts_as_experiment") and budget.get("experiments_started", 0) >= limits.get("configured_max_experiments", 0):
                state["campaign_status"] = "paused_experiment_budget"
                supervisor["status"] = "WAITING_FOR_RESET"; state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor); break
            if invocations >= int(activation.get("max_worker_invocations", activation_worker_limit)) or time.monotonic()-started+limits.get("final_reporting_reserve_seconds", 300) >= limits.get("configured_max_wall_seconds", 7200): break
            usage = supervisor.setdefault("usage", {})
            utc_date = now()[:10]
            if usage.get("date_utc") != utc_date:
                usage.update({"date_utc": utc_date, "conservative_worker_seconds": 0.0,
                              "track_worker_seconds": {track: 0.0 for track in TRACKS}})
            track = task_track(task)
            if usage.get("conservative_worker_seconds", 0.0) >= float(operational["max_daily_worker_seconds"]):
                state["campaign_status"] = "paused_daily_local_budget"; supervisor["status"] = "WAITING_FOR_RESET"; state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor); break
            if usage.get("track_worker_seconds", {}).get(track, 0.0) >= float(operational["max_track_worker_seconds"]):
                state["campaign_status"] = "paused_track_local_budget"; supervisor["status"] = "WAITING_FOR_RESET"; state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor); break
            if shutil.disk_usage(root).free < min_free:
                state["campaign_status"] = "paused_disk_reserve"; supervisor["status"] = "WAITING_FOR_RESET"; state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor); break
            task["status"] = "running"; task["attempts"] = task.get("attempts", 0)+1; task["started_at"] = now()
            if task.get("counts_as_experiment"):
                state["budget_consumption"]["experiments_started"] = state["budget_consumption"].get("experiments_started", 0)+1
            state["budget_consumption"]["worker_invocations_started"] = state["budget_consumption"].get("worker_invocations_started", 0)+1
            activation["worker_invocations"] = int(activation.get("worker_invocations", 0)) + 1
            supervisor["activation"] = activation
            state["campaign_status"] = "running"; state["current_phase"] = task["task_id"].lower()
            state["next_action"] = task["objective"]; state["checkpoint_time"] = now()
            supervisor["status"] = "RUNNING"; supervisor["active_workers"] = [{"task_id": task["task_id"], "track": track, "attempt": task["attempts"]}]
            atomic_json(qp, queue); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor)
            wdir = rdir / "worker_runs" / task["task_id"] / f"attempt-{task['attempts']}"; wdir.mkdir(parents=True, exist_ok=True)
            def record_pid(pid: int) -> None:
                task["worker_pid"] = pid
                atomic_json(qp, queue)
            result = run_worker(root, task, task["attempts"], timeout, max_bytes, wdir, record_pid); invocations += 1
            task.pop("worker_pid", None)
            task["finished_at"] = now()
            fields = ("exit_code", "timed_out", "elapsed_seconds", "artifact_valid", "artifact_bytes", "session_id", "error", "rate_limited", "failure_class", "retry_after_seconds", "official_reset_at", "raw_output_sha256")
            task["last_result"] = {k: result.get(k) for k in fields}
            elapsed = float(result.get("elapsed_seconds") or 0.0)
            usage["conservative_worker_seconds"] = float(usage.get("conservative_worker_seconds", 0.0)) + elapsed
            usage.setdefault("track_worker_seconds", {})[track] = float(usage.get("track_worker_seconds", {}).get(track, 0.0)) + elapsed
            supervisor["usage"] = usage; supervisor["active_workers"] = []
            append_jsonl(root / EVENTS, {"task_id": task["task_id"], "attempt": task["attempts"], "timestamp": now(), **task["last_result"]})
            artifact_scientific_ok = False
            validation = {"scientific_success": False, "reason": "artifact was not valid"}
            artifact_value = None
            if result.get("exit_code") == 0 and result.get("artifact_valid") and not result.get("error"):
                artifact_value = read_json(root / task["artifact"])
                artifact_scientific_ok, validation = scientific_validation(task, artifact_value)
                result["scientific_success"] = artifact_scientific_ok
                task["last_result"]["scientific_success"] = artifact_scientific_ok
                task["scientific_validation"] = validation
                update_scientific_checkpoint(root, state, task, artifact_value, artifact_scientific_ok, validation)
                update_human_status(root, task, artifact_value, artifact_scientific_ok, validation)
            success = result.get("exit_code") == 0 and result.get("artifact_valid") and not result.get("error") and artifact_scientific_ok
            experiment_id = task.get("experiment_id")
            if success and experiment_id:
                ledger_path = root / "research/experiment_ledger.jsonl"
                prior = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
                if any(row.get("experiment_id") == experiment_id for row in prior):
                    success = False
                    task["failure_note"] = f"duplicate experiment_id {experiment_id}; ledger left unchanged"
                    task["last_result"]["error"] = task["failure_note"]
            if success:
                if experiment_id:
                    artifact_value = artifact_value or read_json(root / task["artifact"])
                    ledger_path = root / "research/experiment_ledger.jsonl"
                    append_jsonl(ledger_path, {"experiment_id": experiment_id, "hypothesis_id": task.get("hypothesis_id"),
                                                   "domain": task.get("domain"), "question": task["objective"],
                                                   "prior_evidence": task.get("prior_evidence"), "methodology": task.get("methodology"),
                                                   "dataset_version": task.get("dataset_version"), "execution_command": task.get("execution_command"),
                                                   "configuration": task.get("configuration"), "actual_result": artifact_value,
                                                   "uncertainty": artifact_value.get("uncertainty"), "falsification_outcome": artifact_value.get("falsification_outcome"),
                                                   "decision": artifact_value.get("decision"), "timestamp": now(),
                                                   "reproducibility_artifact": task["artifact"], "exit_code": result.get("exit_code")})
                task["status"] = "completed"
                if task["task_id"] not in state.setdefault("completed_tasks", []): state["completed_tasks"].append(task["task_id"])
                state["current_research_round"] = state.get("current_research_round", 0)+1
            elif artifact_value is not None and not artifact_scientific_ok and not result.get("rate_limited"):
                task["status"] = "artifact_only"
                task["scientific_status"] = "artifact_only"
                task["failure_note"] = validation.get("reason")
                state.setdefault("artifact_only_tasks", [])
                if task["task_id"] not in state["artifact_only_tasks"]:
                    state["artifact_only_tasks"].append(task["task_id"])
                append_jsonl(root / EVENTS, {"event": "artifact_only_scientific_validation", "task_id": task["task_id"], "attempt": task["attempts"], "timestamp": now(), "validation": validation})
            elif result.get("rate_limited"):
                task["status"] = "pending"
                quota = supervisor.setdefault("quota", {})
                quota["state"] = "PAUSED"; quota["source"] = "codex_cli_structured_or_bounded_fallback"
                quota["last_failure_class"] = "quota"; quota["last_failure_at"] = now()
                quota["consecutive_quota_failures"] = int(quota.get("consecutive_quota_failures", 0)) + 1
                quota["next_check_at"] = next_quota_check(supervisor, result, task["attempts"])
                quota["official_reset_at"] = result.get("official_reset_at")
                supervisor["status"] = "QUOTA_PAUSED"
                task["retry_after"] = quota["next_check_at"]
                state["campaign_status"] = "paused_quota_or_rate_limit"
            elif task["attempts"] >= task.get("max_attempts", 1):
                task["status"] = "blocked"; task["failure_note"] = result.get("error") or f"worker exit {result.get('exit_code')}"
                if task["task_id"] not in state.setdefault("blocked_tasks", []): state["blocked_tasks"].append(task["task_id"])
            else:
                task["status"] = "failed"; delay = min(3600, 30 * (2 ** (task["attempts"]-1)))
                task["retry_after"] = (dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=delay)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                supervisor["status"] = "ACTIVE"; supervisor["quota"]["state"] = "AVAILABLE"
            if success:
                supervisor["status"] = "ACTIVE"; supervisor["quota"]["state"] = "AVAILABLE"; supervisor["quota"]["consecutive_quota_failures"] = 0; supervisor["quota"]["next_check_at"] = None
            state["checkpoint_time"] = now(); atomic_json(qp, queue); atomic_json(sp, state); write_supervisor_state(root, supervisor); sync_track_checkpoints(root, state, queue, supervisor)
            if state.get("campaign_status", "").startswith("paused"): break
        state = read_json(sp)
        if state.get("campaign_status") == "running": state["campaign_status"] = "active"
        supervisor = load_supervisor_state(root, state.get("campaign_id", "research"))
        if supervisor.get("status") == "RUNNING": supervisor["status"] = "ACTIVE"
        state["checkpoint_time"] = now(); atomic_json(sp, state); write_supervisor_state(root, supervisor)
        sync_track_checkpoints(root, state, queue, supervisor)
    print(json.dumps({"campaign_status": state.get("campaign_status"), "completed_tasks": state.get("completed_tasks", []),
                      "blocked_tasks": state.get("blocked_tasks", []), "worker_invocations_this_run": invocations,
                      "lifetime_worker_invocations": state.get("budget_consumption", {}).get("worker_invocations_started", 0),
                      "activation_worker_invocations": supervisor.get("activation", {}).get("worker_invocations", 0),
                      "activation_worker_limit": supervisor.get("activation", {}).get("max_worker_invocations"),
                      "supervisor_status": supervisor.get("status"), "next_check_at": supervisor.get("quota", {}).get("next_check_at"),
                      "next_action": state.get("next_action")}, ensure_ascii=False, indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
