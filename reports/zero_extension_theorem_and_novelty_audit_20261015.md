# Zero Extension exact metric sparsifiers: theorem audit and proof-obligation program

**Audit date:** 2026-10-15
**Candidate:** `ZERO-EXTENSION-EXACT-SPARSIFIER-005`
**Scope:** exact metric sparsifiers for the crossing-number-bounded Zero Extension definition in Reidl--Wahlström, not a generic audit of every object called a sparsifier. No new experiment was run and no experimental authorization was consumed.

## Executive conclusion

The source-matched question remains unresolved in the audited record:

> For a graph (G) with terminal set (S), crossing budget (k), and at most (s) labels, must every exact (k)-bounded metric sparsifier have a size exponent that grows with (s), or can one obtain (k^{O(1)}) with a universal exponent under the same definition?

The 2018 paper proves an (O(k^{s+1}))-edge upper bound for fixed constant (s), and explicitly asks for a lower bound and for a degree independent of (s). The strongest apparent follow-up in Wahlström's multicut paper is not usable evidence for a resolution: its final version explicitly retracts the earlier 0-Extension metric-sparsifier claims because a key sparse-cut step was incorrect. The later exact flow, approximate flow, exact/approximate cut, and Steiner-node 0-Extension results are important boundaries, but preserve different objects or guarantees. In the audited forward chain through 2026-10-15, no primary source matching all of the original definition, exact preservation requirement, and (k,s) parameterization was authenticated.

This is **not** a proof that no such result exists. It is a source-matched novelty/feasibility conclusion: no label-independent polynomial exponent is proved or ruled out by the audited chain. The first serious mathematical obligation is to replace the (s+1)-element representative-set certificate, or prove that a restricted version of that replacement is impossible.

## 1. Source-matched theorem reconstruction

### 1.1 The object being preserved

Reidl--Wahlström define, for an instance (I=(G,\tau,\mu,q)), `cost(I,k)` as the minimum cost of a τ-extension whose crossing number is at most (k), with value infinity when no such extension exists. A crossing edge has endpoints receiving different labels. For a graph ((G,S)), (k), and (s\ge |S|), a **(k)-bounded metric sparsifier for metrics with up to (s) labels** is a graph (G') with the same terminals such that, for every metric μ on a label set (D) of size at most (s), and every injective terminal labeling τ:S→D,

\[
  \operatorname{cost}((G,\tau,\mu,q),k)
  =
  \operatorname{cost}((G',\tau,\mu,q),k).
\]

The source definition is an exact equality of the restricted optimum, not an approximation ratio, not preservation of all multicommodity flows, and not merely preservation of terminal cuts. The source's notation includes (q), but the displayed restricted-cost definition is the operative preservation target for this audit.

### 1.2 The theorem and its quantifiers

The source theorem labelled `theorem:kernel` states, in substance:

* for fixed constant (s\ge 3), every graph (G), terminal set (S) with (|S|\le s), and integer (k),
* a randomized polynomial-time algorithm computes (Z\subseteq E(G)) of size (O(k^{s+1})),
* such that for every compatible metric and terminal labeling for which a (k)-crossing solution exists, some minimum-cost (k)-crossing extension has every crossing edge in (Z).

Contracting edges outside (Z\cup E_S) then gives the stated metric sparsifier. The corollary gives an (O(k^{s+1}))-edge sparsifier, and for integer-valued metrics the same construction yields an (O(q^{s+1}))-vertex kernel because a solution of cost at most (q) has at most (q) crossing edges.

The theorem is explicitly a fixed-(s) result. It is not a uniform-in-(s) theorem: the hidden constant and the exponent are both allowed to depend on (s). Nothing in the theorem is a lower bound.

### 1.3 Where (s+1) enters

The proof has four relevant layers.

1. A pushing reduction turns a solution into a form in which terminal-boundary edges are controlled; if the terminal incident-edge count is too large, the instance is rejected or is outside the finite (k)-crossing case. In the proof this gives (|E_S|\le 2k) after the relevant reduction.
2. The proof builds a direct-sum matroid (M=M_0\oplus M_1\oplus\cdots\oplus M_s). (M_0) is a uniform matroid of rank (k). Each (M_i) is a gammoid layer with rank (O(k)); the total rank is (r=O(sk)), which is (O(k)) only when (s) is treated as a constant.
3. Each non-terminal edge (e) is represented by a set (Y(e)) containing one copy in each of the (s) gammoid layers and one copy in the uniform layer. Thus (|Y(e)|=s+1).
4. A representative-set lemma for independent sets of size (p=s+1) retains at most a binomial number of representatives, bounded by (O(r^{p})) for fixed (p). Substituting (r=O(sk)), and treating (s) as constant, gives (O(k^{s+1})).

Thus the exponent is not a loose conversion from vertices to edges. It is the size of the per-edge certificate passed to the representative-set lemma. A label-independent exponent would require a materially different certificate, a nontrivial compression of these (s) label layers, or a lower-bound argument showing that such compression is impossible. Merely improving the polynomial implementation of the same representative-set step cannot remove the (s+1) exponent.

## 2. Forward-citation and theorem-level audit

The table records the audited primary statements and the exact boundary that prevents each from answering the candidate question.

| Work | Theorem-level result audited | Exactness / object | Decision for ZERO-EXTENSION-005 |
|---|---|---|---|
| Reidl--Wahlström, ICALP 2018, [arXiv:1802.06026](https://arxiv.org/abs/1802.06026), [LIPIcs 94](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2018.94) | Fixed-(s) exact (k)-bounded metric sparsifier with (O(k^{s+1})) edges; conclusions explicitly ask for lower bounds and degree independent of (s). | **Exact metric / Zero Extension / crossing budget (k)** | Direct starting theorem; leaves the target open. |
| Wahlström, ICALP 2020 / final ACM TALG version, [arXiv:2002.08825](https://arxiv.org/abs/2002.08825), [DOI](https://doi.org/10.1145/3501304) | Final paper proves quasipolynomial multicut-covering and multicut-mimicking bounds. It explicitly retracts preliminary 0-Extension metric-sparsifier claims because the sparse-cut step assumed an unsupported bound on internal crossing edges. | **Exact multicut mimicking / different problem**; preliminary 0-Extension extension is withdrawn. | Strong negative novelty boundary. It does not resolve the target. |
| Krauthgamer--Mosenzon, SODA 2023, [arXiv:2207.07363](https://arxiv.org/abs/2207.07363), [SODA chapter](https://epubs.siam.org/doi/10.1137/1.9781611977554.ch91) | For every (k\ge6), some (k)-terminal networks have exact flow sparsifiers requiring arbitrarily many vertices. | **Exact multicommodity-flow polytope**, not metric-labeling cost; arbitrary flow sparsifier networks. | Adjacent lower-bound boundary only. It cannot be transferred without a reduction preserving the target objective. |
| Chen--Tan, SODA 2024, [arXiv:2310.07857](https://arxiv.org/abs/2310.07857), [SODA chapter](https://epubs.siam.org/doi/10.1137/1.9781611977912.63) | Quality-((1+\varepsilon)) contraction-based flow sparsifiers have a 5-terminal / 6-terminal separation. | **Approximate flow**, contraction-based; not exact metric sparsification. | Definition mismatch; no target resolution. |
| Das--Kumar--Vaz, MFCS 2024, [arXiv:2407.09433](https://arxiv.org/abs/2407.09433), [MFCS 45](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2024.45) | Bounded exact flow and cut sparsifier bounds for quasi-bipartite graphs. | **Exact flow/cut**, restricted graph family; no Zero Extension metric-cost guarantee. | Restricted adjacent result, not a transfer theorem. |
| Chen--Tan, ICALP 2024, [LIPIcs 47](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2024.47), [arXiv:2401.09585](https://arxiv.org/abs/2401.09585) | 0-Extension with Steiner nodes retains a superconstant Ω(log log(|T|)) integrality gap even with (O(|T|\log^{1-\varepsilon}|T|)) Steiner nodes. | **Approximation / LP integrality gap / Steiner-node 0-Extension**; not an exact sparsifier-size theorem. | Relevant conceptual boundary; no answer to exact edge/vertex sparsifier size. |
| Chen--Tan, ICALP 2025, [paper](https://drops.dagstuhl.de/storage/00lipics/lipics-vol334-icalp2025/html/LIPIcs.ICALP.2025.53/LIPIcs.ICALP.2025.53.html), [arXiv:2407.10852](https://arxiv.org/abs/2407.10852) | Exact and approximate cut-preserving vertex sparsifiers: planar approximate near-linear bounds, quasi-bipartite exact contraction-based bounds, and lower bounds. | **Exact/approximate terminal cuts**, including Steiner-node/contraction variants; not metric-labeling cost. | Relevant terminology and restricted-family techniques, but not a direct theorem. |
| Dvořák--Kolmogorov, [generalized minimum 0-Extension](https://link.springer.com/article/10.1007/s10107-024-02064-5) | Algorithmic/discrete-convexity results for generalized 0-Extension. | **Optimization structure**, not sparsifier preservation or size. | No direct resolution. |
| 2025--2026 forward search | Searches and citation tracing were checked against the exact definition, (k)-bounded crossing condition, and metric-cost equality. No additional source in the audited chain supplied a matching theorem through 2026-10-15. | Search non-detection is not a proof of absence. | Novelty remains **unresolved/uncertain**, not established. |

Two distinctions are decisive. First, an exact cut mimicking network preserves every terminal cut value, whereas the target preserves the minimum cost of all metric labelings subject to a crossing cap. Second, an exact flow sparsifier preserves a multicommodity demand polytope; the 2023 unboundedness result therefore does not imply an unbounded target metric sparsifier. A Steiner-node or contraction-based construction is also not automatically a theorem about the source's unrestricted (G'), which only requires the same terminals and exact target behavior.

## 3. Adversarial review of the proposed opportunity

### What is established

* The source definition and its quantifiers are exact and narrower than generic “metric sparsifier” keyword matches.
* The fixed-(s) (O(k^{s+1})) upper bound and its representative-set proof architecture are source-authenticated.
* The (s+1) exponent enters at the certificate size (Y(e)), before the representative-set counting step.
* The 2018 authors themselves leave a lower-bound and (s)-independent-degree question.
* The later preliminary 0-Extension quasipolynomial claim cannot be counted as a resolution because the final version retracts it.

### Arguments that do **not** survive review

1. **“A cut/flow lower bound proves the target lower bound.”** False without a reduction preserving exact metric-labeling costs and the crossing restriction. The objectives and allowed sparsifier models differ.
2. **“The proof's (s+1) certificate proves an (s+1) lower bound.”** False. A representative-set upper-bound certificate is not a lower-bound certificate; several source edges can be encoded jointly, and the target permits an arbitrary terminal-preserving (G'), not only the proof's contraction output.
3. **“Every edge outside (Z) must remain absent from any exact sparsifier.”** Unsupported. The theorem only proves existence of an optimum with crossing edges in (Z), then uses a particular contraction construction. It does not characterize all exact sparsifiers.
4. **“A sparse terminal cut controls internal crossing edges.”** This is the exact step the final Wahlström paper says was implicitly assumed and could not justify. It must not be reused as a lemma for this project.

### Finite evidence boundary

No new enumeration or experiment was run in this checkpoint. Existing bounded searches only established source eligibility and did not produce an asymptotic gadget. Consequently there is no finite computational evidence to promote into a theorem, and there is no claim that a small-instance pattern has been found.

## 4. Two nontrivial subproblems

### Subproblem A: uniform exponent on a restricted host class

**Candidate lemma A (open, not asserted):** Let (G) be a tree or cactus with terminal set (S), after the source pushing reduction and with (|E_S|\le2k). Does there exist a terminal-preserving exact (k)-bounded metric sparsifier (G') with (O(k^c)) edges for a universal constant (c), simultaneously for every metric with at most (s) labels and every injective τ, independent of (s)?

The first proof obligation is to define a boundary signature for a component of (G-E_S) that captures every possible minimum-cost (k)-crossing extension without storing one independent gammoid coordinate per label. A plausible route is a laminar/tree path signature plus a representative family over terminal-boundary cuts. The proof must show both directions of exact cost preservation, including arbitrary metrics and tie cases; a bound only for discrete Multiway Cut is insufficient.

**Adversarial checks:**

* A component can touch several terminal-side regions, so “one signature per component” is not enough without proving a closure/uncrossing property.
* A tree/cactus restriction alone does not bound the number of nonterminal vertices; a long degree-two chain can only be contracted after proving that all metric costs and crossing counts are preserved.
* The desired exponent must not hide an (s)-dependent constant. Any proof that invokes the same (s+1)-set representative lemma has not advanced the question.

This is a useful restricted theorem target even if the unrestricted question remains open: it would isolate whether the exponent is caused by general graph topology or by label-state information.

### Subproblem B: a proof-compatible lower-bound obstruction

**Candidate lemma B (open, not asserted):** In the narrower class of **contraction-only** sparsifiers generated by deleting/contracting original edges, construct for each (s) a family (G_{s,k}) and a set of source edges with pairwise distinguishable exact (k)-bounded metric-cost signatures, large enough to force a superconstant-in-(s) representative family. A successful construction should identify the metric and terminal labeling that distinguishes each signature and prove that contracting it changes the exact restricted optimum.

This is deliberately weaker than a lower bound for all allowed sparsifiers. It is a mathematically meaningful diagnostic because it tests whether the (s) gammoid coordinates are an artifact of the proof or encode genuinely independent label-boundary states. To imply an Ω((k^{s+1})) lower bound, the construction would need a quantitatively matching family of mutually distinguishable signatures; that implication is a separate proof obligation, not part of the candidate lemma.

**Adversarial checks:**

* Pairwise distinguishability of original edges does not imply that an arbitrary new gadget must contain one vertex/edge per signature.
* A metric may collapse labels or make multiple signatures cost-equivalent; the lower-bound proof must quantify over a separating metric, not merely draw a combinatorial picture.
* A contraction-only lower bound cannot be reported as a lower bound for Reidl--Wahlström's unrestricted (G') without an additional simulation theorem.

### Optional bridge problem: Multiway Cut transfer

Prove or disprove the exact reduction from a uniform-in-(s) metric sparsifier to a uniform-degree kernel for (s)-Multiway Cut under the same terminal and crossing conventions. The discrete metric is a special case, but a kernel transfer must track the source's (k)-bounded optimum and the output representation. This bridge would make a restricted result consequential without conflating the two notions.

## 5. Proof-obligation ledger

The machine-readable version is [`research/zero_extension_proof_obligation_ledger_v1.json`](../research/zero_extension_proof_obligation_ledger_v1.json).

| ID | Obligation | Status | Required evidence |
|---|---|---|---|
| O1 | Match the source definition, including exact cost equality, (k)-crossing restriction, (|S|\le s), and injective τ. | **Established** | Reidl--Wahlström kernel definition and theorem. |
| O2 | Reconstruct the pushing reduction and terminal-boundary cap used by the proof. | **Established at source level** | Source proof; not independently reproved here. |
| O3 | Explain (s+1) from (Y(e)) and the representative-set lemma. | **Established at source level** | (s) gammoid copies plus one uniform copy; rank (O(sk)). |
| O4 | Show that later exact flow/cut/Steiner results answer the same target. | **Disproved as a transfer shortcut** | Definitions and guarantees differ; no reduction supplied. |
| O5 | Use the retracted sparse-cut step to prove a lower bound. | **Failed / forbidden** | Final Wahlström correction identifies the unsupported assumption. |
| O6 | Uniform-in-(s) exact sparsifier for trees/cacti. | **Open proof obligation A** | Boundary signature, exact two-sided preservation, universal exponent. |
| O7 | Contraction-only label-state lower-bound family. | **Open proof obligation B** | Separating metrics, forced non-contraction, quantitative (s)-dependence. |
| O8 | Lift contraction-only lower bound to arbitrary terminal-preserving sparsifiers. | **Open and harder** | A simulation or information lower bound for arbitrary (G'). |
| O9 | Produce a finite gadget and independently verify it. | **Not started; experiment-gated** | New authorization would be required for computation; finite evidence cannot prove asymptotics. |
| O10 | Prove a label-independent exponent for the unrestricted target. | **Not established** | Would require a new theorem beyond the audited sources. |

## 6. Novelty verdict and next action

**Classification of the current claims:**

* (O(k^{s+1})) exact fixed-(s) upper bound: **known prior art**.
* The (s+1) representative-set explanation: **source-established proof architecture**.
* The label-independent exponent question: **source-authenticated open question at the 2018 cutoff; current status unresolved in this bounded forward audit**.
* A (k^{\Omega(s)}) lower bound: **plausible but unproved**.
* Any lower bound inferred from exact flow/cut or Steiner-node results: **disproved as an inference**.
* Any “no theorem exists through 2026” statement: **not established globally; only no matching theorem was authenticated in this audit**.

The strongest next mathematical task is therefore **O6/O7 source-and-proof work**, beginning with O6 on trees/cacti. It is admitted to the research queue as a non-experimental, bounded proof-audit task. The task must first attempt the boundary-signature lemma and actively search for a counterexample; if it fails, it should record the smallest obstruction and then switch to O7. No experiment budget is renewed by this admission.

Paper 3 remains separate: this audit changes the opportunity registry and proof queue, not the frozen historical cohorts, Target A labels, Target B evidence-growth labels, or any forecast score.
