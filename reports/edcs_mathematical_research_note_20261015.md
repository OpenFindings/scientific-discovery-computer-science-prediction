# EDCS lazy-repair mathematical note — 2026-10-15

## Scope and provenance boundary

The result concerns only the frozen deterministic variant in
`research/edcs_experiment_protocol_v1.json`: simple bipartite graphs,
`beta=4`, `beta_minus=3`, FIFO dirty vertices, lexicographic incident-edge
inspection, P1 removals before P2 additions, and at most one H-edge toggle per
external update. It is not a counterexample to the Bernstein–Stein EDCS
definition, matching theorem, or dynamic maintenance algorithm.

The fixed witness below was replayed by the separate
`scripts/audit_edcs_witness.py` checker. The checker does not import the
experiment runner and writes `mathematical_witness_check.json`.

## Four updates, step by step

Let `L={0,1}` and `R={0,1,2}`. Initially `G=H=empty` and the dirty FIFO is
empty. A repair flip means one insertion or deletion of one edge in `H`.

| update | external edge | repair decision | resulting H degrees | invariant state |
|---|---|---|---|---|
| 1 | insert `(0,0)` | P2 is deficient (`0<3`), add `(0,0)` | `d(L0)=1,d(R0)=1` | used sum `2<=4` |
| 2 | insert `(0,1)` | P2 is deficient (`1<3`), add `(0,1)` | `d(L0)=2,d(R0)=1,d(R1)=1` | used sums `3<=4` |
| 3 | insert `(0,2)` | P2 is deficient (`2<3`), add `(0,2)` | `d(L0)=3,d(R0)=d(R1)=d(R2)=1` | used sums `4<=4` |
| 4 | insert `(1,0)` | after stale FIFO vertices with no violation are popped, `(1,0)` is P2-deficient (`d(L1)+d(R0)=0+1=1<3`), so add it | `d(L0)=3,d(L1)=1,d(R0)=2` | old used `(0,0)` has `3+2=5>4` |

The queue matters only to identify which violation is serviced first. After
updates 1–3, `L0` remains at the head after each one-flip repair; on update 4
it is checked, found clean, and popped. `R0` is then checked and sees the
deficient new edge `(1,0)`, which consumes the single allowed flip. The queue
cannot perform the second necessary toggle in the same update.

At update 4, leaving `(1,0)` unused violates P2. Adding it creates the P1
violation on `(0,0)`. Thus the failure is not a runner assertion: it follows
directly from the degree arithmetic and the declared one-toggle semantics.
The exact matching values are `mu(G)=2` and `mu(H)=2`, so the matching ratio is
`1`, not a failing endpoint.

## Generalization that does survive scrutiny

### A proved parameterized family

For every integer `b>=3`, set `beta=b` and `beta_minus=b-1`. Take a center
`a` in the left side, a second left vertex `x`, and right vertices
`v_1,...,v_{b-1}`. Insert the star edges `(a,v_i)` in order.

Before the i-th star edge is repaired, its endpoint-degree sum is `i-1`, so
`i-1 <= b-2 < beta_minus`; the rule adds it. After the star is built,
`d(a)=b-1` and every `d(v_i)=1`, hence every used-edge sum is exactly `b` and
P1 holds. Now insert `(x,v_1)`. Before adding it, its sum is `0+1=1<b-1`
for `b>=3`, so P2 requires that edge to enter H. Adding it raises `d(v_1)`
from 1 to 2, making the old edge `(a,v_1)` have sum
`(b-1)+2=b+1>beta`.

Therefore, for this explicitly specified class, no maintenance rule that is
allowed only one single-edge H toggle after the external insertion can leave
both P1 and P2 true. The statement is a theorem about the class and the
one-toggle model, not about the original EDCS maintenance algorithm. It also
does not cover arbitrary `beta_minus`; when `beta_minus < beta-1`, the empty-
state star-growth argument no longer forces all `b-1` star edges into H.

### Repair lower bound

More generally, suppose a valid state has an inserted edge `e=(x,v)` that is
the only G-edge incident to degree-zero `x`, and `e` is P2-deficient. Suppose
adding `e` makes at least one already-used edge incident to `v` P1-violating.
Any valid post-update state must toggle `e` into H (otherwise P2 remains false)
and must toggle at least one old used edge out of H (otherwise P1 remains
false). Hence at least two single-edge H toggles are necessary. The four-edge
witness instantiates this lemma with `e=(1,0)` and old edge `(0,0)`.

This lower bound is fully proved under its stated assumptions. It does not
establish a lower bound for compound swaps, arbitrary repair primitives, or
the Bernstein–Stein algorithm.

## Prior-art and novelty classification

| claim | classification |
|---|---|
| Four-edge violation for the frozen deterministic one-toggle variant | independently reproduced; finite counterexample only |
| Parameterized family for `beta=b>=3, beta_minus=b-1` in the one-toggle model | fully proved for the explicitly stated model |
| Two single-edge toggles required in the stated deficient-edge/full-edge class | fully proved conditional repair lower bound |
| P1/P2 restoration through alternating full/deficient paths and bounded repair work | known prior art in Bernstein–Stein |
| Hierarchical EDCS as a dynamic matching generalization | known prior art in Behnezhad–Khanna |
| EDCS used as verification/repair in later dynamic maximal matching | known prior art in Bernstein et al. 2025 and subsequent work |
| A new theorem about original EDCS or a new dynamic-matching lower bound | unverified; no claim made |
| Refutation of original EDCS theory or matching theorems | disproved as an interpretation: the witness does not target them |

Bernstein–Stein explicitly describe alternating repairs, show a bounded path
length, and derive an `O(beta)` update ratio; this is precisely the cascading
repair phenomenon absent from the tested one-toggle variant. Later work uses
EDCS/HEDCS in different roles and does not turn this variant witness into a
new theorem.

## Next experiment — not executed

The single most discriminating next experiment would preregister a small
parameter matrix comparing (i) `beta_minus=beta-1` against lower gaps, (ii)
one-toggle repair against a two-toggle remove-then-add repair, and (iii) the
FIFO rule against a repair rule that treats the newly inserted deficient edge
first. The endpoint would be the first update at which P1/P2 fail, with the
minimum number of H toggles recorded. This separates a threshold-gap cause
from a one-toggle budget cause and from queue-order artifacts. It requires a
new explicit experiment authorization and was not run in this cycle.

## Paper 3 and Paper 4 boundaries

Paper 3 Target A and Target B remain separate and unscored because the
historical cohorts lack authenticated direct outcomes. Paper 4's EDCS action
was feasible and informative, but one action cannot establish planner
superiority; its original assumptions are unchanged.
