#!/usr/bin/env python3
"""Build the additive historical evidence-trajectory checkpoint for all 16 rows.

The source-screen ledgers are immutable inputs.  The four appended rows contain
only bounded, dated follow-up checks performed after their source-only locks;
absence of a direct match remains unadjudicated rather than a negative label.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def row(versioned_id: str, question: str, cutoff: str, followup_end: str, terms: list[str], dimensions: dict, scope: str | None, evidence: list[dict], excluded: list[dict], decision: str, limitations: str) -> dict:
    return {
        "versioned_id": versioned_id,
        "question": question,
        "cutoff": cutoff,
        "followup_end": followup_end,
        "search_date_utc": "2026-10-15",
        "search_terms": terms,
        "dimensions": dimensions,
        "unadjudicated_direct_outcome": True,
        "supported_dimension_scope": scope,
        "evidence": evidence,
        "excluded_near_matches": excluded,
        "decision": decision,
        "limitations": limitations,
    }


def build() -> dict:
    old = json.loads((ROOT / "reports/historical_evidence_trajectory_round1.json").read_text())
    new = [
        row(
            "1805.02751v2",
            "Across a preregistered sample of connected children's toys, can an automated policy-to-property audit recover the same objectively verifiable privacy and network-security violations as independent manual analysis while reducing analyst effort without increasing false negatives?",
            "2018-12-31T23:59:59Z",
            "2023-12-31T23:59:59Z",
            ["1805.02751 smart toy privacy policy automated audit follow-up", "connected toy privacy security audit 2019 2020 2021 2022", "smart toys policy to technical property verification"],
            {k: "not_observed_after_bounded_search" for k in ["direct_scientific_resolution", "premise_refutation_or_revision", "partial_progress", "independent_evidence_strengthening", "contradictory_evidence", "scope_narrowing_or_reformulation", "continued_explicit_uncertainty"]},
            None,
            [],
            [
                {"url": "https://www.sciencedirect.com/science/article/pii/S1567422319300997", "reason": "A 2019 smart-toy risk review synthesizes risks and proposed solutions but does not run the frozen automated policy-to-property versus manual audit."},
                {"url": "https://consumer.ftc.gov/consumer-alerts/2019/12/what-ask-buying-internet-connected-toys", "reason": "Regulatory consumer guidance, not a primary controlled audit outcome."}
            ],
            "The bounded search found adjacent smart-toy risk synthesis and regulatory guidance, but no dated primary study matching automated policy-to-property mapping against an independent manual audit with recall, false-positive and analyst-time endpoints. The direct question remains unadjudicated.",
            "The source itself covers only three products. Later toy studies with different products or policy definitions are not direct resolution."
        ),
        row(
            "2003.02892v1",
            "For heterogeneous smart-home devices with software-update and adversarial-traffic regimes, can collaborative whitelist learning converge to a stable permitted-connection set while keeping false blocking and attacker-injected allowance below predeclared thresholds?",
            "2020-12-31T23:59:59Z",
            "2025-12-31T23:59:59Z",
            ["SERENIoT whitelist convergence generalization across devices", "SERENIoT IoT policy generalization 2021 2022 2023", "collaborative IoT allowlist consensus adversarial traffic"],
            {"direct_scientific_resolution": "not_observed_after_bounded_search", "premise_refutation_or_revision": "not_observed_after_bounded_search", "partial_progress": "not_observed_after_bounded_search", "independent_evidence_strengthening": "not_observed_after_bounded_search", "contradictory_evidence": "not_observed_after_bounded_search", "scope_narrowing_or_reformulation": "supported", "continued_explicit_uncertainty": "not_observed_after_bounded_search"},
            "A later dissertation explicitly distinguishes SERENIoT's collaborative allowlist idea from the unstudied generalization of traffic data and cross-device policy transfer, and notes that lab consensus behavior may not carry to load-balanced environments. This narrows the decisive question to cross-device generalization and field robustness; it does not answer the source's convergence/safety claim.",
            [
                {"title": "Making Interactions With Home IoT Devices More Secure, Private, and Usable", "first_public_url": "https://mailman.cs.uchicago.edu/mailman/public/cs/attachments/20220707/a4ebadef/attachment-0001.pdf", "first_public_date": "2022-07-07", "date_scope": "public mailing-list attachment date; exact dissertation deposit date not independently authenticated", "primary_fulltext_url": "https://mailman.cs.uchicago.edu/mailman/public/cs/attachments/20220707/a4ebadef/attachment-0001.pdf", "locator": "PDF discussion of data-driven allowlist approaches and SERENIoT; statement that generalization across devices is not evaluated", "directness": "scope_narrowing_not_direct_resolution", "independence": "Different author and dataset; discusses SERENIoT as prior work.", "observed_claim": "The later work states that SERENIoT creates allowlists from observed behavior but does not study how traffic data generalizes or how policies generalize across devices, and flags deployment variation as a concern."}
            ],
            [],
            "Count scope narrowing only. The later source makes the missing generalization endpoint explicit; no comparable collaborative-whitelist experiment with the frozen metrics was authenticated.",
            "The follow-up is a public dissertation PDF with a mailing-list date bound, not a peer-reviewed replication. It cannot supply a direct label."
        ),
        row(
            "1903.05387v1",
            "On constrained virtual-machine configuration spaces, does adding solver-backed constraint handling to Avocado reduce invalid or redundant test executions while preserving or improving detection of invalid configurations relative to unconstrained t-way generation?",
            "2019-12-31T23:59:59Z",
            "2024-12-31T23:59:59Z",
            ["Avocado constrained interaction testing solver follow-up 2020", "1903.05387 constrained CIT invalid configurations", "Avocado Open-Source Flexible Constrained Interaction Testing"],
            {"direct_scientific_resolution": "not_observed_after_bounded_search", "premise_refutation_or_revision": "not_observed_after_bounded_search", "partial_progress": "supported", "independent_evidence_strengthening": "not_observed_after_bounded_search", "contradictory_evidence": "not_observed_after_bounded_search", "scope_narrowing_or_reformulation": "not_observed_after_bounded_search", "continued_explicit_uncertainty": "not_observed_after_bounded_search"},
            "A 2020 follow-up from the Avocado collaboration reports implementing solver-backed constrained interaction testing and an industrial-scale application. It is partial progress on the source's planned capability, but the bounded record does not provide a matched unconstrained baseline with the frozen detection and cost endpoints.",
            [
                {"title": "Avocado: Open-Source Flexible Constrained Interaction Testing for Practical Application", "first_public_url": "https://arxiv.org/abs/2002.00390", "first_public_date": "2020-02-02", "primary_fulltext_url": "https://arxiv.org/pdf/2002.00390", "locator": "Abstract and implementation/evaluation sections; solver-backed constrained CIT and industrial application", "directness": "partial_progress_on_planned_constraint_handling", "independence": "Same project lineage and overlapping authors; not an independent outcome unit.", "observed_claim": "The follow-up describes constraint-solver support, constrained suite generation, execution and an industrial application, but does not authenticate the source question's matched comparison as a direct result."}
            ],
            [],
            "Count partial progress only. The planned solver capability became an implemented framework feature, but implementation and a case study are not evidence that it reduces invalid executions at matched detection recall and cost.",
            "The source and follow-up are closely related, so this is not independent strengthening. Exact configuration models and matched baseline denominators require source-code audit."
        ),
        row(
            "2007.03275v1",
            "Can the security-pattern checking approach generalize from UML-sequence-diagram-supported Web applications to applications or patterns lacking those diagrams by using code annotations, while preserving independently verified behavioral-property detection precision and recall?",
            "2020-12-31T23:59:59Z",
            "2025-12-31T23:59:59Z",
            ["security pattern checking UML sequence diagrams annotations follow-up", "Salva Regainia security pattern LTL code annotations 2021 2022", "security pattern detection framework behavioral properties applications"],
            {k: "not_observed_after_bounded_search" for k in ["direct_scientific_resolution", "premise_refutation_or_revision", "partial_progress", "independent_evidence_strengthening", "contradictory_evidence", "scope_narrowing_or_reformulation", "continued_explicit_uncertainty"]},
            None,
            [],
            [
                {"url": "https://www.sciencedirect.com/science/article/abs/pii/S0164121220302296", "reason": "A 2021 security-pattern detection framework reports a different detection technique and endpoint; it does not test the source's annotation-based replacement for missing UML sequence diagrams."},
                {"url": "https://link.springer.com/article/10.1186/s42400-022-00109-w", "reason": "A 2022 conceptual paper on abstract security patterns does not provide the frozen project-disjoint behavioral-property comparison."}
            ],
            "The bounded search found adjacent security-pattern detection and conceptual pattern work, but no primary result matching the source's proposed annotation representation against the UML-sequence-diagram pipeline on independently checked behavioral properties. The question remains unadjudicated.",
            "Adjacent detection frameworks cannot be treated as direct resolution because intervention, input representation and endpoints differ."
        )
    ]
    rows = old["rows"] + new
    counts = {
        "selected_titles": 16,
        "source_screened": 16,
        "eligible_questions": 12,
        "future_audited_questions": len(rows),
        "direct_resolution_supported": 0,
        "direct_resolution_refuted": 0,
        "premise_refutation_or_revision_supported": 0,
        "partial_progress_supported": sum(r["dimensions"]["partial_progress"] == "supported" for r in rows),
        "independent_evidence_strengthening_supported": sum(r["dimensions"]["independent_evidence_strengthening"] == "supported" for r in rows),
        "contradictory_evidence_supported": sum(r["dimensions"]["contradictory_evidence"] == "supported" for r in rows),
        "scope_narrowing_or_reformulation_supported": sum(r["dimensions"]["scope_narrowing_or_reformulation"] == "supported" for r in rows),
        "continued_explicit_uncertainty_supported": sum(r["dimensions"]["continued_explicit_uncertainty"] == "supported" for r in rows),
        "direct_outcome_unadjudicated": sum(r["unadjudicated_direct_outcome"] for r in rows),
    }
    return {
        "dataset_id": "HCS-OBSERVABLE-16-TRAJECTORY-ROUND2-2026-10-15",
        "protocol": "research/historical_evidence_trajectory_protocol_v1.json",
        "source_screens": [
            "reports/historical_observable_source_screen_round1.json",
            "reports/historical_observable_source_screen_round2.json",
            "reports/historical_observable_source_screen_round3.json",
            "reports/historical_observable_source_screen_round4.json",
            "reports/historical_observable_source_screen_round5.json",
            "reports/historical_observable_source_screen_round6.json",
        ],
        "population_note": "All 16 source-selected papers now have a locked source-only status. Twelve eligible questions received bounded follow-up checks; direct resolution remains unadjudicated for every row. Dimension counts are descriptive and nonexclusive, not Paper 3 labels.",
        "rows": rows,
        "counts": counts,
        "analysis_gate": "No Paper 3 AUC, calibration or breakthrough probability: the direct-resolution class has zero positive and zero negative labels, absence-of-hit rows are unadjudicated, and no grouped chronological holdout has an adequate directly adjudicated contrast.",
        "changed_decisions": [
            "The original 20-paper blind cohort is unchanged and still has zero direct future-resolution labels.",
            "The separate 16-paper observable cohort is now fully source-screened: 12 eligible and 4 ineligible; no outcome-informed replacement was used.",
            "Trajectory evidence is measurable as partial progress and scope narrowing, but not as direct resolution; Paper 3 transfer remains infeasible under the frozen gate.",
            "The most actionable low-cost new questions are constrained-CIT baseline auditing and IoT whitelist generalization, both requiring matched endpoint experiments before positive claims."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/historical_evidence_trajectory_round2.json")
    args = parser.parse_args()
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
