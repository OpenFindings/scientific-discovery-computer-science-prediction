# Full-text audit batch 22: algorithmic guarantees need their assumption contract

Updated 2026-10-11. Four fixed-frame uniform-random `algorithms_complexity` papers were reviewed, one per submission period. They cover geometric pricing, truthful ordinal mechanisms, massively parallel graph connectivity, and weighted online paging/server migration. The papers do not share an empirical outcome or one approximation ratio. Their useful commonality is methodological: each headline guarantee is attached to a precise model and parameter regime, and dropping those premises makes the claim easy to overgeneralize.

## 1. Geometric Pricing: How Low Dimensionality Helps in Approximability (2012)

[Chalermsook et al., arXiv:1202.2840v2](https://arxiv.org/abs/1202.2840); [full arXiv PDF](https://arxiv.org/pdf/1202.2840), §§1–3 and appendices.

The paper studies unit-demand uniform-budget min-buying pricing and single-minded pricing when consumers/items are represented by points and consumer consideration sets are induced by coordinate-wise attributes. For fixed dimension `d`, it gives an `O~_d(n^(1-ε(d)))` approximation where `ε(d)=1/4^(d−1)` (with the paper noting a slight improvement under an additional QPTAS implication). It also gives QPTAS results in dimension two and hardness boundaries, including NP-hardness already in small dimensions and APX-hardness by dimension four for the stated variants.

**Boundary:** “sublinear approximation” is a fixed-dimension asymptotic result; the exponent improvement shrinks rapidly as dimension rises, and constants are hidden in the dimension-dependent notation. The model further assumes conjunctive attribute-based consideration sets and the specified buyer/pricing behaviors. This is a theorem about that formal model, not evidence from deployed pricing data or arbitrary consumer preferences.

## 2. Truthful Mechanisms for Matching and Clustering in an Ordinal World (2016)

[Anshelevich and Sekar, arXiv:1610.04069v2](https://arxiv.org/abs/1610.04069); [full arXiv PDF](https://arxiv.org/pdf/1610.04069), §§1–3 and result table.

Agents have hidden numerical edge utilities but provide only ordinal preference rankings, and may strategically misreport. The paper proves universally truthful approximation mechanisms for weighted graph problems: e.g. 1.7638 for weighted perfect matching, 2 for max k-matching and k-sum clustering, and 2 for max TSP only when hidden weights form a metric. It reports a 6-approximation for densest k-subgraph, with a separate bicriteria relaxation. The paper also gives non-truthful ordinal algorithms; some have better ratios (for example, weighted perfect matching 1.6 and max TSP 1.88), but they do not retain the truthfulness guarantee.

**Boundary:** the result depends on the ordinal-information and single-agent truthfulness model, objective defined as total hidden edge weight, and—in the TSP guarantee—the metric assumption. Approximation factors are not directly comparable to algorithms with cardinal inputs, different incentives, or different objectives. This is a proof result, not a user study measuring real preference elicitation.

## 3. Deterministic Massively Parallel Connectivity (2021)

[Czumaj, Davies, and Parter, arXiv:2108.04102v1](https://arxiv.org/abs/2108.04102); [full arXiv PDF](https://arxiv.org/pdf/2108.04102), §§1–2, 6–8.

In the massively parallel computation (MPC) model, the paper derandomizes low-local-space connectivity algorithms without asymptotic loss: for an undirected graph with `n` vertices, `m` edges, and component diameter at most `D`, it gives a deterministic `O(log D + log log_{m/n} n)`-round algorithm with per-machine local space `O(n^δ)` for constant `δ>0` and total/global space `O(m+n)`. It also extends a conditional `Ω(log D)` lower bound across diameter regimes under the 1-vs-2-cycles conjecture. The authors explicitly note that the algorithm is not component-stable, which is important because a conditional lower-bound framework rules out constant-round deterministic low-space component-stable algorithms under that conjecture.

**Boundary:** the round bound is meaningful only with the MPC communication, local/global space, graph, and diameter assumptions stated. “Deterministic” does not mean a result for ordinary single-machine execution, and the lower bound is conditional. The paper proves asymptotic complexity; it does not provide a production-cluster measurement of constants, data movement, or wall-clock performance.

## 4. Weighted k-Server Admits an Exponentially Competitive Algorithm (2025)

[Chiplunkar and Kumar, arXiv:2507.12130v2](https://arxiv.org/abs/2507.12130); [full arXiv PDF](https://arxiv.org/pdf/2507.12130), §§1–2, 6–7.

For the weighted k-server problem on uniform metric spaces, the paper proves a randomized `exp(O(k²))` competitive ratio, closing an exponential gap in the asymptotic dependence on `k`; its technique also yields `exp(O(k²))` for generalized weighted k-server on uniform metrics. It accounts for arbitrary server weights by rounding with at most a `2^(k−1)` competitive-ratio loss. This does not solve the arbitrary-metric problem: the paper notes that no competitive algorithm is known there for general `k>2` and explicitly identifies broader metric families as open.

**Counterweight:** competitive ratio is an information-theoretic worst-case measure, not runtime or practical service cost. The authors explicitly say computational efficiency cannot be ignored and identify the memory-versus-competitive-ratio trade-off as open; they note that known algorithms generally require at least doubly exponential memory in `k`, except for a particular randomized memoryless algorithm. The new theorem's ratio must therefore not be presented as an efficient practical implementation without separate resource analysis.

## Bounded cross-paper finding

Across these papers, a guarantee is not just its headline number: it is a tuple comprising the problem definition, information/incentive/adversary model, input structure, parameter regime, success guarantee, and resource measure. Examples: geometric pricing's sublinear ratio relies on fixed low dimension; the ordinal matching ratios change when truthfulness is removed and one TSP guarantee requires metric weights; MPC connectivity's rounds trade on local/global memory and graph diameter; weighted k-server's new ratio is for uniform metrics and leaves computational memory as a separate concern. These theorem statements are internally meaningful, but flattening them to a broad “algorithms” label or raw approximation/round count would create false comparisons.

**Falsifiable next test:** assemble a blinded benchmark of theorem-transfer questions from a larger, stratified sample of algorithms papers. For each source theorem and target problem variant, ask reviewers or systems with (a) title/abstract/topic metadata only versus (b) a typed guarantee contract (problem, input class, information/adversary, parameters, probability, resources, and conditional assumptions) to decide whether the theorem applies. Measure false-transfer rate and expert adjudication time, stratified by subfield and era. The hypothesis is weakened if the typed contract does not reduce false transfers or materially improve reviewer agreement/time.

This sample is a cross-era audit of four theory papers, not a trend estimate, empirical evaluation of the theorems, or a novelty claim.
