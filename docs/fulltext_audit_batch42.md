# Full-text audit batch 42: algorithmic guarantees live inside explicit regimes

Updated 2026-10-12. This batch audits all seven previously unread uniform-random records in the `algorithms_complexity` topic cell. The papers do not form a single empirical literature or directly replicate one another. The useful cross-paper observation is methodological: each headline “efficient”, “fair”, or “hard” result is conditional on a precise model/parameter regime, and weakening one premise can change what is known. This is a research-design lead, not a new theorem or population-level finding.

## Seven sampled full texts

### 1. The Two Bicliques Problem is in NP intersection coNP (arXiv:1104.3463v4; 2011)

[arXiv full text](https://arxiv.org/pdf/1104.3463v4).

The paper studies whether a graph's vertices can be covered by at most two bicliques and proves membership in NP∩coNP. This is a meaningful complexity-class placement, but it is not a polynomial-time algorithm and does not prove membership in P. The paper's “more likely polynomial than NP-complete unless P=NP” phrasing is a heuristic interpretation of that placement, not a resolution of P versus NP. Its conclusion separately leaves a related two-biclique **partition** problem open; cover and partition must not be silently treated as identical. The archived v4 PDF also has an internal date/header oddity, so claims here follow the versioned arXiv file rather than inferring a venue history.

### 2. Distributed Exact Weighted All-Pairs Shortest Paths in Near-Linear Time (arXiv:1811.03337v2; 2018)

[arXiv full text](https://arxiv.org/abs/1811.03337).

In the CONGEST distributed-network model, the authors give a randomized Las Vegas exact APSP algorithm in near-linear (polylogarithmic factors suppressed) rounds, matching the known near-linear lower bound up to polylogs. The construction uses randomized landmark sampling, filtering/broadcast, and congestion scheduling; it is a proved communication-round bound, not a wall-clock benchmark. The model and graph assumptions matter: the main formulation is weighted distributed networks, and the paper explains extensions to directed communication/zero or negative weights while requiring the relevant shortest-path distances to be well-defined. This does not imply near-linear centralized APSP or low real-world runtime on arbitrary networks.

### 3. Contraction: a Unified Perspective of Correlation Decay and Zero-Freeness of 2-Spin Systems (arXiv:1909.04244v3; journal version 2021)

[arXiv full text](https://arxiv.org/html/1909.04244) · [journal record](https://doi.org/10.1007/s10955-021-02831-0).

For a fixed maximum degree Δ, a real parameter point satisfying the paper's contraction condition has a complex neighborhood in which the partition function is zero-free and correlation decay holds; this yields an FPTAS in the stated bounded-degree 2-spin setting. The result connects two proof routes—Weitz-style correlation decay and Barvinok-style zero-free interpolation—but the theorem is a sufficient-condition transfer, not an equivalence for every model or a guarantee outside the neighborhood. The paper's related-work discussion acknowledges overlapping restricted-case zero-free results in Liu's thesis; “first” language therefore needs that scope qualifier.

### 4. On Fairness and Stability in Two-Sided Matchings (arXiv:2111.10885v1; ITCS 2022)

[ITCS full text and abstract](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2022.92).

The paper gives a concrete composition failure: even when hospitals' preferences are individually fair, applying classical Gale–Shapley can produce a blatantly unfair outcome. It then gives efficient fair-and-stable algorithms under two strong premises: fair hospital preferences and a proto-metric where every doctor-pair distance is 0 or 1. Outside those premises, the impossibility is only for a specified natural class of algorithms (including Gale–Shapley-style and the paper's own algorithms), not a theorem that no conceivable algorithm can work. This is theory about a formal matching model, not evidence of measured discrimination in deployed residency allocation.

### 5. Time and Energy Efficient Contention Resolution in Asynchronous Shared Channels (arXiv:2209.14140; 2022)

[arXiv full text](https://arxiv.org/html/2209.14140).

For asynchronous shared channels with simple success acknowledgements, adaptive protocols—or protocols given the number k of contenders—can achieve O(k) message latency, asymptotically optimal in that setting. Remove both adaptivity and knowledge of k, and the authors prove a lower bound of Ω(k log k/(log log k)^2); their non-adaptive unknown-k protocol nearly matches it. They also analyze total transmissions (energy), not just completion time. The contrast isolates information/adaptivity as a complexity resource; it is not a statement that asynchronous protocols are universally efficient, and the high-probability/the adversary/model qualifications in the theorem remain essential.

### 6. Tight (S)ETH-based Lower Bounds for Pseudopolynomial Algorithms for Bin Packing and Multi-Machine Scheduling (arXiv:2603.12999v1; 2026)

[arXiv full text](https://arxiv.org/html/2603.12999).

This is a conditional lower-bound paper, not an implementation comparison. Assuming ETH, it rules out 2^{o(n)}T^{o(k)} time for k-bin packing, tightening an earlier bound by closing a logarithmic-factor gap. Assuming SETH, it rules out 2^{o(n)}T^{k−1−ε} time for several k-machine scheduling objectives and 2^{o(n)}T^{k−ε} for total processing time of tardy jobs, matching the exponents of classic pseudopolynomial dynamic programs. These are conditional statements with problem-specific parameter T and objective definitions; they do not rule out algorithms outside those time forms, nor faster algorithms under weaker input/parameter restrictions.

### 7. A computational phase diagram for the transverse field Ising model (arXiv:2610.02079v1; submitted 2026-10-01)

[arXiv full text](https://arxiv.org/html/2610.02079).

For the specified transverse-field Ising Hamiltonian, the paper gives a randomized classical relative-approximation algorithm for the partition function when Δ(J)·tanh(βη)/η ≤ 1, and proves NP-hardness of approximation within exp(o(n))-multiplicative factor when the expression is >1. In the tractable regime it also treats Pauli-string observables, with additive error generally and relative error for the stated X-diagonal special case. This sharp-looking boundary is an asymptotic theorem under its Hamiltonian/input assumptions, not a measured phase transition in quantum hardware; equality belongs to the tractable side as stated. The paper is very recent, so independent follow-up/replication evidence is not yet established by this audit.

## Bounded cross-paper synthesis

Across this deliberately heterogeneous seven-paper draw, “efficiency” is inseparable from the formal regime: bounded degree and contraction for 2-spin FPTAS; fair preferences plus a binary proto-metric for matching; knowledge/adaptivity for asynchronous contention; ETH/SETH assumptions for pseudopolynomial lower bounds; and a spectral-width/temperature inequality for the transverse Ising model. The biclique paper is a useful guardrail: NP∩coNP is not P. These are not replications and should not be pooled into a single effect or presented as one scientific law.

**Falsifiable research-design lead (not a novelty claim):** for algorithm papers with a claimed regime boundary, build a “boundary audit” that independently checks (1) exact model/input premises, (2) guarantee strictly inside/on/outside the boundary, (3) what the lower bound actually excludes, and (4) whether realistic instances satisfy the premises. A study of usefulness could sample theorem-backed algorithms and compare how often abstract guarantees survive realistic instance distributions. It would be weakened if a preregistered sample showed that relaxing stated premises rarely changes guarantees or practical applicability. That empirical study has not been run here; this batch supplies examples and a protocol, not its result.

## Audit boundary

All seven random selections in this topic-period cell have now been checked against full text or the primary conference proceedings record. Venue dates are verified only where indicated. No systematic citation graph, exhaustive follow-up review, theorem re-proving, or independent experimental replication was performed. This closes one 7-paper sample cell only; it does not constitute a review of the 198,690-candidate pool.
