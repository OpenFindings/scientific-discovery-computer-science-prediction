#!/usr/bin/env python3
"""Check the arithmetic obligations of the reviewed EDCS one-toggle lemma.

This is a symbolic/arithmetic proof audit, not a graph search and not a new
experiment. It checks beta=3..100 and the alternate-edge counterexample to the
overbroad deficient-edge claim.
"""
from __future__ import annotations


def check_parameterized_family(beta: int) -> dict[str, bool | int]:
    assert beta >= 3
    beta_minus = beta - 1
    star_edges = beta - 1
    before_cross = 1
    old_edge_after_add = (beta - 1) + 2
    other_unused_after_add = (beta - 1) + 2
    return {
        "beta": beta,
        "star_edges": star_edges,
        "cross_edge_deficient": before_cross < beta_minus,
        "delete_keeps_cross_deficient": before_cross < beta_minus,
        "add_cross_violates_p1": old_edge_after_add > beta,
        "add_other_unused_violates_p1": other_unused_after_add > beta,
        "one_toggle_impossible": (
            before_cross < beta_minus
            and old_edge_after_add > beta
            and other_unused_after_add > beta
        ),
    }


def check_overbroad_claim_counterexample() -> dict[str, object]:
    beta, beta_minus = 4, 2
    # H={(x',a),(v,b)}; f=(x',v) is unused and e=(x,v) is inserted.
    pre_degrees = {"x'": 1, "a": 1, "v": 1, "b": 1, "x": 0}
    post_f_degrees = {**pre_degrees, "x'": 2, "v": 2}
    return {
        "beta": beta,
        "beta_minus": beta_minus,
        "e_unused_sum_after_f": post_f_degrees["x"] + post_f_degrees["v"],
        "f_used_sum_after_f": post_f_degrees["x'"] + post_f_degrees["v"],
        "old_used_sums_after_f": [
            post_f_degrees["x'"] + post_f_degrees["a"],
            post_f_degrees["v"] + post_f_degrees["b"],
        ],
        "alternate_repair_valid": (
            post_f_degrees["x"] + post_f_degrees["v"] >= beta_minus
            and post_f_degrees["x'"] + post_f_degrees["v"] <= beta
            and all(
                value <= beta
                for value in [
                    post_f_degrees["x'"] + post_f_degrees["a"],
                    post_f_degrees["v"] + post_f_degrees["b"],
                ]
            )
        ),
    }


def main() -> int:
    rows = [check_parameterized_family(beta) for beta in range(3, 101)]
    assert all(row["one_toggle_impossible"] for row in rows)
    counterexample = check_overbroad_claim_counterexample()
    assert counterexample["alternate_repair_valid"] is True
    print(
        "parameterized proof obligations passed for beta=3..100; "
        "alternate-edge counterexample passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
