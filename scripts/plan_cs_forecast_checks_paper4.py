#!/usr/bin/env python3
"""Rank the CS breakthrough-forecast checks with the Paper 4 evidence planner.

Uses the unmodified planner from github.com/OpenFindings/scientific-evidence-planner
(pinned commit recorded in the output). Hypotheses, evidence, candidate checks, costs and
times below are explicit planning assumptions, not measurements; the resulting utilities are
a check order, not evidence of scientific value.

    python3 scripts/plan_cs_forecast_checks_paper4.py \
        --planner-src /home/user/openfindings/scientific-evidence-planner
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HYPOTHESES = [
    ("H1", "Paper 3 structure features forecast top-decile CS attention beyond baselines", 0.30),
    ("H2", "Any signal is reducible to early-citation / topic momentum", 0.30),
    ("H3", "Top-decile citation attention is a visibility artifact, not breakthrough", 0.20),
    ("H4", "No out-of-time signal at all", 0.20),
]

# (node_id, type, label, provenance root or None)
NODES = [
    ("paper3_astro", "paper", "Paper 3 astronomy study (980 questions, 5 cutoffs)", None),
    ("claim_p3_temporal_auc", "claim", "Astronomy temporal-split AUC 0.71 from structured features",
     "paper3_astro"),
    ("claim_p3_robust_predictors", "claim",
     "Robust astronomy predictors: review recognition, related-evidence density", "paper3_astro"),
    ("paper4_planner", "paper", "Paper 4 evidence planner study", None),
    ("claim_p4_neglect_artifact", "claim",
     "Paper 4 neglect finding withdrawn: retrieval label under-counted engagement",
     "paper4_planner"),
]

# (source, target hypothesis, edge type, confidence)
EDGES = [
    ("claim_p3_temporal_auc", "H1", "supports", 0.4),  # different domain: discounted
    ("claim_p3_robust_predictors", "H2", "supports", 0.4),
    ("claim_p4_neglect_artifact", "H3", "supports", 0.5),
]

# (id, action type, target, cost, time, resources, description)
CHECKS = [
    ("A1_openalex_snapshot", "search_archive", "H4", 0.15, 0.20, ["openalex"],
     "Targeted OpenAlex snapshot of the 1,006 frame papers: abstracts, references, "
     "citations by year, topic volumes"),
    ("A2_rolling_backtest", "rerun_analysis", "H1", 0.30, 0.30, ["openalex", "compute"],
     "Rolling-origin backtest of the Paper 3 CS feature model against frozen baselines"),
    ("A3_momentum_head_to_head", "compare_datasets", "H2", 0.20, 0.20, ["openalex", "compute"],
     "Combined-vs-best-baseline paired delta AUROC, incl. early-citation momentum"),
    ("A4_permutation_null", "run_simulation", "H4", 0.10, 0.10, ["openalex", "compute"],
     "Within-year label permutation null for the Paper 3 model"),
    ("A5_blind_human_labels", "collect_observation", "H3", 0.60, 0.70, ["human_labeler"],
     "Blinded human breakthrough labels (HTML) on a prioritized sample vs citation label"),
    ("A6_survey_exclusion", "rerun_analysis", "H3", 0.10, 0.10, ["openalex", "compute"],
     "Re-score after excluding survey/review/tutorial papers"),
    ("A7_group_ablation", "rerun_analysis", "H1", 0.20, 0.20, ["openalex", "compute"],
     "Feature-group ablations (drop-one / only-one)"),
    ("A8_leave_topic_out", "compare_datasets", "H1", 0.20, 0.20, ["openalex", "compute"],
     "Leave-one-frame-topic-out generalization"),
    ("A9_title_only_text", "rerun_analysis", "H1", 0.10, 0.10, ["openalex", "compute"],
     "Text features from titles only (abstract-version leakage sensitivity)"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner-src", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "reports/paper4_cs_forecast_check_plan.json")
    args = ap.parse_args()
    sys.path.insert(0, str(args.planner_src / "src"))
    from planner import (  # noqa: E402
        ActionType, CandidateAction, EdgeType, EvidenceEdge, EvidenceGraph, EvidenceNode,
        GapAnalyzer, Hypothesis, NodeType, Planner, Question, UtilityEstimator,
        load_utility_config,
    )
    from planner.utility import ResourceTractabilityEstimator  # noqa: E402

    commit = subprocess.run(["git", "-C", str(args.planner_src), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    question = Question("CS-BREAKTHROUGH-FORECAST-V1",
                        "Do cutoff-time Paper 3 features forecast top-decile future attention "
                        "of CS papers beyond simple baselines?", domain="computer_science")
    hyps = [Hypothesis(h, d, prior=p) for h, d, p in HYPOTHESES]
    graph = EvidenceGraph()
    for h, d, _ in HYPOTHESES:
        graph.add_node(EvidenceNode(h, NodeType.HYPOTHESIS, d))
    for nid, ntype, label, _ in NODES:
        graph.add_node(EvidenceNode(nid, NodeType(ntype), label))
    for nid, _, _, root in NODES:
        if root:
            graph.add_edge(EvidenceEdge(nid, root, EdgeType.DERIVED_FROM))
    for src, tgt, etype, conf in EDGES:
        graph.add_edge(EvidenceEdge(src, tgt, EdgeType(etype), confidence=conf))
    gaps = GapAnalyzer().analyze(question, hyps, graph)

    actions = [CandidateAction(aid, ActionType(t), desc, cost, time, list(res), target)
               for aid, t, target, cost, time, res, desc in CHECKS]
    weights = load_utility_config(args.planner_src / "configs/default.yaml")
    scenarios = {
        "openalex_available": {"compute", "openalex", "human_labeler"},
        "openalex_blocked": {"compute", "human_labeler"},
    }
    rankings = {}
    for name, resources in scenarios.items():
        est = UtilityEstimator(config=weights,
                               tractability=ResourceTractabilityEstimator(resources))
        recs = Planner(est).rank(actions, hyps, graph)
        rankings[name] = [{"rank": r.rank, "action_id": r.action.action_id,
                           "target": r.action.target_hypothesis,
                           "utility": r.utility.to_dict(), "reasoning": r.reasoning}
                          for r in recs]
    out = {
        "planner_repo": "https://github.com/OpenFindings/scientific-evidence-planner",
        "planner_commit": commit,
        "utility_weights": "configs/default.yaml of the planner repo",
        "question": question.to_dict(),
        "hypotheses": [h.to_dict() for h in hyps],
        "evidence_graph": graph.to_dict(),
        "gap_report": gaps.to_dict(),
        "rankings": rankings,
        "status": "planning estimate; costs, times, priors and edge confidences are declared "
                  "assumptions, not measurements",
    }
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    for name, recs in rankings.items():
        print(name)
        for r in recs:
            print(f"  {r['rank']}. {r['action_id']:<26} {r['target']}  "
                  f"U={r['utility']['total']:.3f}")


if __name__ == "__main__":
    main()
