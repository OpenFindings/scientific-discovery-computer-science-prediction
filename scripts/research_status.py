#!/usr/bin/env python3
"""Print the persistent research campaign checkpoint."""
import json
from pathlib import Path
from research_supervisor import eligible_tasks, proposed_continuations

ROOT = Path(__file__).resolve().parents[1]
state = json.loads((ROOT / "research/state.json").read_text())
queue = json.loads((ROOT / "research/task_queue.json").read_text())
supervisor_path = ROOT / "research/supervisor_state.json"
supervisor = json.loads(supervisor_path.read_text()) if supervisor_path.is_file() else {"status": "NOT_INITIALIZED"}
tasks = queue["tasks"]
ready = eligible_tasks(queue, set(state.get("completed_tasks", [])))
next_task = ready[0] if ready else None
best = state.get("opportunity_ranking") or state.get("current_best_opportunities", [])
print(f"Campaign: {state.get('campaign_id')} [{state.get('campaign_status')}]")
print(f"Supervisor: {supervisor.get('status')} (stop_requested={supervisor.get('stop_requested', False)})")
print(f"Phase/round: {state.get('current_phase')} / {state.get('current_research_round')}")
print(f"Hypothesis/experiment: {state.get('active_hypothesis_id') or 'none'} / {state.get('active_experiment_id') or 'none'}")
print(f"Latest actual result: {state.get('actual_experiment_results')[-1] if state.get('actual_experiment_results') else 'none recorded'}")
print(f"Latest scientific increment: {state.get('latest_scientific_increment', 'none recorded')}")
best_id = (best[0].get("task_id") or best[0].get("finding_id")) if best else "none"
best_status = best[0].get("status", "queued") if best else ""
print(f"Best opportunity: {best_id} — {best_status}")
print(f"Checkpoint: {state.get('checkpoint_time')}")
print(f"Blockers: {', '.join(state.get('blocked_tasks', [])) or 'none'}")
quota = supervisor.get("quota", {})
print(f"Quota: {quota.get('state', 'unknown')} (next_check={quota.get('next_check_at') or 'none'}, official_reset={quota.get('official_reset_at') or 'unknown'})")
usage = supervisor.get("usage", {})
limits = state.get("operational_limits", {})
print(f"Local budget: {usage.get('conservative_worker_seconds', 0):.1f}s/{limits.get('max_daily_worker_seconds', 'unknown')}s daily; tracks={usage.get('track_worker_seconds', {})}")
for track in ("forecasting", "experiments"):
    path = ROOT / "research/tracks" / track / "state.json"
    if path.is_file():
        lane = json.loads(path.read_text())
        print(f"Track {track}: {lane.get('status')} active={lane.get('active_task_ids', [])} pending={len(lane.get('pending_task_ids', []))} completed={len(lane.get('completed_task_ids', []))}")
print(f"Next task: {next_task['task_id'] + ' — ' + next_task['objective'] if next_task else state.get('next_action')}")
b = state.get("budget_consumption", {})
activation = supervisor.get("activation", {})
print(f"Local activation cap≤{activation.get('max_worker_invocations', b.get('configured_max_worker_invocations_per_activation', 1))} (used {activation.get('worker_invocations', 0)}); lifetime workers={b.get('worker_invocations_started', 0)} append-only; historical rounds={state.get('current_research_round',0)}; experiment starts remaining≤{max(0,b.get('configured_max_experiments',0)-b.get('experiments_started',0))}; service quota: unknown to supervisor")
print(f"Evidence-gated task proposals: {', '.join(t['task_id'] for t in proposed_continuations(ROOT, queue)) or 'none'}")
