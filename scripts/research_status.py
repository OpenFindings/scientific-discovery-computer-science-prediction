#!/usr/bin/env python3
"""Print the persistent research campaign checkpoint."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
state = json.loads((ROOT / "research/state.json").read_text())
queue = json.loads((ROOT / "research/task_queue.json").read_text())
tasks = queue["tasks"]
next_task = next((t for t in tasks if t.get("status") in {"pending", "failed"} and
                  set(t.get("dependencies", [])).issubset(set(state.get("completed_tasks", [])))), None)
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
print(f"Configured remaining: rounds≤{max(0,b.get('configured_max_rounds',0)-state.get('current_research_round',0))}; worker invocations≤{max(0,b.get('configured_max_worker_invocations',0)-b.get('worker_invocations_started',0))}; experiments≤{max(0,b.get('configured_max_experiments',0)-b.get('experiments_started',0))}; service quota: unknown to supervisor")
