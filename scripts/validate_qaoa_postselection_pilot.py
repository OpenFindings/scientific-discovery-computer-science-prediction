#!/usr/bin/env python3
"""Independently validate the frozen local Paper 4 QAOA pilot output."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reports/paper4_prospective_plan_v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/qaoa_postselection_pilot_20261015/result.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/paper4_qaoa_postselection_validation_20261015.json"))
    args = parser.parse_args()
    result = json.loads(args.input.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["experiment_id"] = result.get("experiment_id") == "EXP-PAPER4-QAOA-POSTSELECTION-PILOT-20261015"
    checks["frozen_plan_id"] = result.get("plan_id") == plan.get("plan_id")
    checks["frozen_plan_hash"] = result.get("plan_sha256") == plan.get("plan_sha256")
    checks["plan_hash_recomputes"] = hashlib.sha256(
        json.dumps({k: v for k, v in plan.items() if k != "plan_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest() == plan.get("plan_sha256")
    observations = result.get("observations")
    checks["observation_count"] = isinstance(observations, list) and len(observations) == 20
    checks["independent_unit_is_graph"] = all(isinstance(row.get("graph_index"), int) for row in observations or [])
    checks["a2_setup_no_go_is_explicit"] = result.get("falsification_gate", {}).get("status") == "setup_infeasible_for_alternative"
    checks["a2_has_no_valid_rows"] = result.get("summary", {}).get("valid_graphs_3") == 0
    checks["a1_denominator_is_preserved"] = result.get("summary", {}).get("valid_graphs_2") == 16
    checks["no_nan_payload"] = "NaN" not in json.dumps(result, allow_nan=False)
    checks["uncertainty_and_next_action_present"] = bool(result.get("uncertainty")) and bool(result.get("next_falsifiable_action"))
    checks["limitations_present"] = bool(result.get("limitations"))
    output = {
        "validation_id": "VALIDATE-EXP-PAPER4-QAOA-POSTSELECTION-PILOT-20261015",
        "input": str(args.input),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "scientific_interpretation": "A2 is a setup-feasibility no-go at the preregistered n=8 graph family; A1 is a conditional source-style baseline observation. Neither establishes a breakthrough or Paper 4 planning utility.",
        "unresolved": [
            "A2 feasibility at larger n or under a source-consistent conditioning definition was not tested.",
            "The A1 positive delta is conditional on 16 admitted graphs and has no population-level uncertainty estimate.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
