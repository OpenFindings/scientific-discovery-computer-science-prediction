#!/usr/bin/env python3
"""Paper 4 retrospective: belief update from executed checks, planner calibration, re-rank.

Uses the unmodified planner (same pinned commit as reports/paper4_cs_forecast_check_plan.json)
and its own binary-outcome likelihood model. Outcome codes are frozen in
research/paper4_retrospective_outcome_coding_v1.json. Candidate costs, times and resources
are declared planning assumptions, not measurements.

    python3 scripts/paper4_update_and_rerank.py \
        --planner-src /home/user/openfindings/scientific-evidence-planner
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]

# (id, action type, target, cost, time, resources, description)
NEXT_CANDIDATES = [
    ("B1_zero_citation_cutoff", "rerun_analysis", "H2", 0.25, 0.30, ["compute", "openalex"],
     "Re-run the frozen forecast at a cutoff before any citations exist (posting month), so "
     "momentum is unavailable: does structure beat the remaining baselines?"),
    ("B2_fresh_frame_replication", "compare_datasets", "H1", 0.50, 0.60, ["compute", "openalex"],
     "Pre-register and run the same forecast on a fresh, independently sampled CS frame"),
    ("B3_independent_reimplementation", "rerun_analysis", "H2", 0.30, 0.40, ["compute", "web_agents"],
     "Fresh agent re-implements the primary analysis from the protocol text only"),
    ("B4_second_human_labeler", "collect_observation", "H3", 0.60, 0.70, ["human_labeler"],
     "Second blinded human labeler on the same 120 papers"),
    ("B5_structure_vs_value_markers", "rerun_analysis", "H1", 0.10, 0.10, ["compute"],
     "Does the Paper 3 score predict documentary value markers across all 398 searched papers?"),
    ("B6_cross_domain_transfer", "compare_datasets", "H1", 0.60, 0.70, ["compute", "openalex"],
     "Apply the CS-adapted features to a non-CS field frame"),
    ("B7_prospective_registration", "collect_observation", "H1", 0.30, 1.00, ["compute", "openalex"],
     "Register forecasts for 2025 papers now; outcomes mature in 2028"),
]
AVAILABLE = {"compute", "openalex", "web_agents"}  # no human labeler (owner's decision)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner-src", required=True, type=Path)
    ap.add_argument("--coding", default="v2", choices=["v1", "v2"])
    args = ap.parse_args()
    sys.path.insert(0, str(args.planner_src / "src"))
    from planner import (  # noqa: E402
        ActionType, CandidateAction, EdgeType, EvidenceEdge, EvidenceNode, NodeType, Planner,
        UtilityEstimator, load_utility_config,
    )
    from planner.belief_update import BayesianBeliefUpdater  # noqa: E402
    from planner.schemas import Hypothesis, NewEvidence  # noqa: E402
    from planner.utility import (  # noqa: E402
        DEFAULT_DISCRIMINATIVE_POWER, ExpectedEntropyReductionEstimator,
        ResourceTractabilityEstimator, entropy,
    )

    spec = importlib.util.spec_from_file_location(
        "orig", ROOT / "scripts/plan_cs_forecast_checks_paper4.py")
    orig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(orig)
    commit = subprocess.run(["git", "-C", str(args.planner_src), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    plan = json.loads((ROOT / "reports/paper4_cs_forecast_check_plan.json").read_text())
    if commit != plan["planner_commit"]:
        sys.exit(f"planner commit {commit} != pinned {plan['planner_commit']}")
    v1 = json.loads((ROOT / "research/paper4_retrospective_outcome_coding_v1.json").read_text())
    coding = json.loads((ROOT / f"research/paper4_retrospective_outcome_coding_{args.coding}.json").read_text())
    planned = {x["order"]: (x["target"], x["action_type"]) for x in v1["steps"]}
    for st in coding["steps"]:  # v2 steps keep the planned target for the predicted-IG column
        st.setdefault("target", planned[st["order"]][0])
        if "predicts" in st:
            st["code"] = "multi"

    hyps = [Hypothesis(h, d, prior=p) for h, d, p in orig.HYPOTHESES]
    ids = [h.hypothesis_id for h in hyps]
    ig_est, updater = ExpectedEntropyReductionEstimator(), BayesianBeliefUpdater()
    steps = []
    for s in coding["steps"]:
        atype = ActionType(s["action_type"])
        act = CandidateAction(s["check"], atype, s["basis"], 0.0, 0.0, [], s["target"])
        predicted = ig_est.estimate(act, hyps, None)
        before = [h.prior for h in hyps]
        if s["code"] == "multi":
            r = DEFAULT_DISCRIMINATIVE_POWER[atype]
            lik = {h: (r / (r + 1) if h in s["predicts"] else 1 / (r + 1) if h in s["opposes"]
                       else 0.5) for h in ids}
            hyps = updater.update(hyps, NewEvidence(s["check"], s["basis"], lik))
        elif s["code"] != "null":
            r = DEFAULT_DISCRIMINATIVE_POWER[atype]
            hit, miss = r / (r + 1), 1 / (r + 1)
            fav = s["code"] == "favor"
            lik = {h: ((hit if fav else miss) if h == s["target"] else (miss if fav else hit))
                   for h in ids}
            hyps = updater.update(hyps, NewEvidence(s["check"], s["basis"], lik))
        after = [h.prior for h in hyps]
        steps.append({"order": s["order"], "check": s["check"], "target": s["target"],
                      "code": s["code"], "predicted_ig_bits": predicted,
                      "realized_entropy_reduction_bits": entropy(before) - entropy(after),
                      "posterior": dict(zip(ids, after))})

    coded = [x for x in steps]
    rho = spearmanr([x["predicted_ig_bits"] for x in coded],
                    [abs(x["realized_entropy_reduction_bits"]) for x in coded]).statistic
    orig_rank = {r["action_id"]: r["rank"] for r in plan["rankings"]["openalex_available"]}
    decisive = sorted(steps, key=lambda x: -abs(x["realized_entropy_reduction_bits"]))

    # re-rank next actions with updated beliefs and the executed checks as new evidence
    from planner import EvidenceGraph  # noqa: E402
    graph = EvidenceGraph()
    for h, d, _ in orig.HYPOTHESES:
        graph.add_node(EvidenceNode(h, NodeType.HYPOTHESIS, d))
    for nid, ntype, label, _ in orig.NODES:
        graph.add_node(EvidenceNode(nid, NodeType(ntype), label))
    for nid, _, _, root in orig.NODES:
        if root:
            graph.add_edge(EvidenceEdge(nid, root, EdgeType.DERIVED_FROM))
    for src, tgt, etype, conf in orig.EDGES:
        graph.add_edge(EvidenceEdge(src, tgt, EdgeType(etype), confidence=conf))
    graph.add_node(EvidenceNode("cs_forecast_v1", NodeType("paper"), "This project's CS forecast v1"))
    for s in coding["steps"]:
        if s["code"] == "null":
            continue
        nid = f"res_{s['order']}"
        graph.add_node(EvidenceNode(nid, NodeType("claim"), s["basis"]))
        graph.add_edge(EvidenceEdge(nid, "cs_forecast_v1", EdgeType.DERIVED_FROM))
        if s["code"] == "multi":
            for h in s["predicts"]:
                graph.add_edge(EvidenceEdge(nid, h, EdgeType("supports"), confidence=0.7))
            for h in s["opposes"]:
                graph.add_edge(EvidenceEdge(nid, h, EdgeType("contradicts"), confidence=0.7))
        else:
            graph.add_edge(EvidenceEdge(nid, s["target"], EdgeType(
                "supports" if s["code"] == "favor" else "contradicts"), confidence=0.7))
    actions = [CandidateAction(a, ActionType(t), d, c, tm, list(res), tg)
               for a, t, tg, c, tm, res, d in NEXT_CANDIDATES]
    est = UtilityEstimator(config=load_utility_config(args.planner_src / "configs/default.yaml"),
                           tractability=ResourceTractabilityEstimator(AVAILABLE))
    recs = Planner(est).rank(actions, hyps, graph)

    out = {
        "planner_repo": plan["planner_repo"], "planner_commit": commit,
        "outcome_coding": f"research/paper4_retrospective_outcome_coding_{args.coding}.json",
        "prior": {h: p for h, _, p in orig.HYPOTHESES},
        "posterior": {h.hypothesis_id: h.prior for h in hyps},
        "steps": steps,
        "calibration": {
            "spearman_predicted_ig_vs_abs_realized": float(rho),
            "note": "Realized = entropy reduction under the planner's own likelihood model given "
                    "the coded outcome; null-coded checks realize 0 by construction.",
            "original_plan_rank_of_most_decisive": [
                {"check": x["check"], "realized_bits": x["realized_entropy_reduction_bits"],
                 "original_rank": orig_rank.get(x["check"])} for x in decisive[:4]]},
        "next_action_ranking": [{"rank": r.rank, "action_id": r.action.action_id,
                                 "target": r.action.target_hypothesis,
                                 "utility": r.utility.to_dict(), "reasoning": r.reasoning}
                                for r in recs],
        "available_resources": sorted(AVAILABLE),
        "status": "planning estimate; outcome codes are retrospective; costs, times and "
                  "discriminative powers are declared assumptions, not measurements",
    }
    path = ROOT / f"reports/paper4_cs_forecast_update_and_rerank_{args.coding}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("prior", "posterior")}, indent=1))
    for x in steps:
        print(f'{x["order"]:>2} {x["check"]:<30} {x["target"]} {x["code"]:<7} '
              f'pred {x["predicted_ig_bits"]:.3f}  real {x["realized_entropy_reduction_bits"]:+.3f}')
    print("spearman", round(rho, 3))
    for r in out["next_action_ranking"]:
        print(r["rank"], r["action_id"], r["target"], round(r["utility"]["total"], 2),
              "IG", round(r["utility"]["information_gain"], 3))


if __name__ == "__main__":
    main()
