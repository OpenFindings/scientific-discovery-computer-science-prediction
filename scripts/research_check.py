#!/usr/bin/env python3
"""Validate persistent campaign state, queue, append-only ledger and artifacts."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
state = json.loads((ROOT / "research/state.json").read_text())
queue = json.loads((ROOT / "research/task_queue.json").read_text())
ids = [t.get("task_id") for t in queue.get("tasks", [])]
if len(ids) != len(set(ids)): errors.append("duplicate task_id")
all_ids = set(ids)
for task in queue.get("tasks", []):
    if not set(task.get("dependencies", [])).issubset(all_ids): errors.append(f"unknown dependency: {task.get('task_id')}")
    p = Path(task.get("artifact", ""))
    if p.is_absolute() or ".." in p.parts: errors.append(f"unsafe artifact path: {task.get('task_id')}")
    if task.get("status") == "completed" and not (ROOT / p).is_file(): errors.append(f"completed artifact missing: {task.get('task_id')}")
if state.get("schema_version") != 1: errors.append("unsupported state schema")
if len(state.get("completed_tasks", [])) != len(set(state.get("completed_tasks", []))): errors.append("duplicate completed task")
supervisor_path = ROOT / "research/supervisor_state.json"
if supervisor_path.is_file():
    try:
        supervisor = json.loads(supervisor_path.read_text())
        if supervisor.get("schema_version") != 1: errors.append("unsupported supervisor state schema")
        if supervisor.get("status") not in {"ACTIVE", "RUNNING", "QUOTA_PAUSED", "WAITING_FOR_RESET", "RESUME_CHECK", "BLOCKED", "STOPPED_BY_USER", "NOT_INITIALIZED"}:
            errors.append("invalid supervisor status")
        if supervisor.get("quota", {}).get("state") not in {"AVAILABLE", "PAUSED"}:
            errors.append("invalid supervisor quota state")
        global_ids = set(ids)
        seen_track_ids = set()
        for track in ("forecasting", "experiments", "theory"):
            lane_path = ROOT / "research/tracks" / track / "task_queue.json"
            if not lane_path.is_file():
                errors.append(f"missing track queue: {track}")
                continue
            lane_ids = {task.get("task_id") for task in json.loads(lane_path.read_text()).get("tasks", [])}
            if not lane_ids.issubset(global_ids): errors.append(f"track queue contains unknown task: {track}")
            if seen_track_ids & lane_ids: errors.append("task appears in multiple track queues")
            seen_track_ids |= lane_ids
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid supervisor state: {exc}")
ledger = ROOT / "research/experiment_ledger.jsonl"
if not ledger.is_file(): errors.append("experiment ledger missing")
experiment_ids = set()
for n, line in enumerate(ledger.read_text().splitlines(), 1):
    if not line.strip(): continue
    try: row = json.loads(line)
    except json.JSONDecodeError as e: errors.append(f"invalid ledger line {n}: {e}"); continue
    exp = row.get("experiment_id")
    if not exp: errors.append(f"ledger line {n} lacks experiment_id")
    elif exp in experiment_ids: errors.append(f"duplicate experiment_id: {exp}")
    experiment_ids.add(exp)
print(json.dumps({"ok": not errors, "task_count": len(ids), "ledger_records": len(experiment_ids), "errors": errors}, indent=2))
sys.exit(bool(errors))
