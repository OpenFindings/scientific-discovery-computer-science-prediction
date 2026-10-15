#!/usr/bin/env python3
"""Apply one bounded, auditable local experiment-budget renewal."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, effective_experiment_cap, now, read_json

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--additional", type=int, required=True)
    parser.add_argument("--renewal-id", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    if not 1 <= args.additional <= 4:
        raise SystemExit("additional renewal must be between 1 and 4 experiments")
    state_path = ROOT / "research/state.json"
    events_path = ROOT / "research/supervisor_events.jsonl"
    state = read_json(state_path)
    budget = state.setdefault("budget_consumption", {})
    existing = budget.get("renewable_experiment_budget")
    if isinstance(existing, dict) and existing.get("status") == "AUTHORIZED" and existing.get("renewal_id") != args.renewal_id:
        raise SystemExit("an active experiment renewal already exists")
    started = int(budget.get("experiments_started", 0))
    base = int(budget.get("configured_max_experiments", 0))
    renewal = {
        "status": "AUTHORIZED",
        "renewal_id": args.renewal_id,
        "authorized_additional": args.additional,
        "consumed": max(0, started - base),
        "remaining": max(0, base + args.additional - started),
        "reason": args.reason,
        "created_at": now(),
        "expires_after_experiments_started": started + args.additional,
    }
    budget["renewable_experiment_budget"] = renewal
    state["checkpoint_time"] = now()
    state["campaign_status"] = "waiting_for_eligible_task"
    state["next_action"] = "Admit only the frozen independent QAOA replication and fair-cost comparison tasks."
    atomic_json(state_path, state)
    append_jsonl(events_path, {"event": "renewable_experiment_budget_authorized", "renewal": renewal, "timestamp": now()})
    print(json.dumps({"effective_cap": effective_experiment_cap(budget), "renewal": renewal}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
