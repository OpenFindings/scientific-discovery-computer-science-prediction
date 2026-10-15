#!/usr/bin/env python3
"""Print the persistent research campaign checkpoint."""
import json
from pathlib import Path
from research_supervisor import eligible_tasks, proposed_continuations

ROOT = Path(__file__).resolve().parents[1]
state = json.loads((ROOT / "research/state.json").read_text())
queue = json.loads((ROOT / "research/task_queue.json").read_text())
tasks = queue["tasks"]
ready = eligible_tasks(queue, set(state.get("completed_tasks", [])))
next_task = ready[0] if ready else None
best = state.get("current_best_opportunities", [])
print(f"Campaign: {state.get('campaign_id')} [{state.get('campaign_status')}]")
print(f"Phase/round: {state.get('current_phase')} / {state.get('current_research_round')}")
print(f"Hypothesis/experiment: {state.get('active_hypothesis_id') or 'none'} / {state.get('active_experiment_id') or 'none'}")
print(f"Latest actual result: {state.get('actual_experiment_results')[-1] if state.get('actual_experiment_results') else 'none recorded'}")
print(f"Best opportunity: {best[0]['finding_id'] if best else 'none'} — {best[0]['status'] if best else ''}")
print(f"Checkpoint: {state.get('checkpoint_time')}")
print(f"Blockers: {', '.join(state.get('blocked_tasks', [])) or 'none'}")
print(f"Next task: {next_task['task_id'] + ' — ' + next_task['objective'] if next_task else state.get('next_action')}")
b = state.get("budget_consumption", {})
print(f"Local per-start round cap≤{b.get('configured_max_rounds',0)} (historical research milestones: {state.get('current_research_round',0)}; not a service quota); worker invocations remaining≤{max(0,b.get('configured_max_worker_invocations',0)-b.get('worker_invocations_started',0))}; experiment starts remaining≤{max(0,b.get('configured_max_experiments',0)-b.get('experiments_started',0))}; service quota: unknown to supervisor")
print(f"Evidence-gated task proposals: {', '.join(t['task_id'] for t in proposed_continuations(ROOT, queue)) or 'none'}")
