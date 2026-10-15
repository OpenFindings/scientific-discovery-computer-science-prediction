# Full-text audit batch 49: algorithmic guarantees, scope, and stale open problems

Updated 2026-10-12. This batch audits the three remaining lexical-priority records in `algorithms_complexity × 2020–2024`. The label is an umbrella: the three papers concern computational hardness for reinforcement learning, dynamic string edit distance, and a restricted quantum complexity class. Their results are not pooled. Two later full-text citation follow-ups were checked to update the current status of open problems and to test whether apparently conflicting dynamic-tree results actually conflict.

## Sampled papers

### 1. Computational-Statistical Gaps in Reinforcement Learning (arXiv:2202.05444v2; 2022)

[arXiv HTML full text](https://arxiv.org/html/2202.05444v2); locally retrieved PDF: `data/fulltexts/arxiv/2202.05444v2.pdf` (19 pages); extracted text: `data/fulltexts/text/2202.05444v2.txt`.

The main lower bound concerns Linear-2-RL/Linear-3-RL: a deterministic-transition MDP, two or three actions, horizon `H = O(d)`, known access oracles for rewards, transitions, and `d`-dimensional features, and both optimal `V*` and `Q*` linear in those features. The algorithm must return a policy within `1/4` of optimal value. By reduction from Unique-3-SAT, a polynomial-time randomized solver would imply `NP = RP`; under rETH the paper proves a quasi-polynomial-time lower bound. This is a computational-hardness result, not a claim that learning is statistically impossible: the paper contrasts it with polynomial-query statistical learnability. It also leaves open whether its techniques yield an exponential lower bound under rETH. The deterministic transition assumption, constant action count, and access model are central boundaries; this result does not itself establish the same lower bound for stochastic transitions or arbitrary practical RL systems.

### 2. Approximating Edit Distance in the Fully Dynamic Model (arXiv:2307.07175v1; 2023)

[arXiv HTML full text](https://arxiv.org/html/2307.07175v1); locally retrieved PDF: `data/fulltexts/arxiv/2307.07175v1.pdf` (46 pages); extracted text: `data/fulltexts/text/2307.07175v1.txt`.

The paper maintains an approximation to the edit distance between two strings of length at most `n` under arbitrary insertions, deletions, and substitutions at arbitrary positions. Its Theorem 7.10 gives, for integer parameter `2 ≤ b ≤ n`, an `O(b log_b n)` approximation with amortized expected update time `b² (log n)^{O(log_b n)}`; answers are correct with high probability at least `1 - 1/n`. The parameter allows different tradeoffs: subpolynomial approximation and update time, or polylogarithmic approximation with `O(n^ε)` updates for fixed `ε > 0`. These are asymptotic approximation/update guarantees, not measurements of latency on real edit traces. In particular, approximation error, amortized expected work, and high-probability correctness are separate outcomes and should not be collapsed into “fast and accurate.”

### 3. The Space Just Above One Clean Qubit (arXiv:2410.08051v1; 2024)

[arXiv HTML full text](https://arxiv.org/html/2410.08051v1); locally retrieved PDF: `data/fulltexts/arxiv/2410.08051v1.pdf` (43 pages); extracted text: `data/fulltexts/text/2410.08051v1.txt`.

The paper studies `1/2-BQP`, a query-complexity model that starts in a maximally mixed state and receives information about the initial state at the end. It shows that this model can solve several familiar oracle problems, including 2-Forrelation, while sharing limitations with DQC1 (including no Grover quadratic speedup under the analyzed model). Its open-problem section conjectures that `1/2-BQP` cannot solve 3-Forrelation and asks more broadly where the class sits in the Forrelation hierarchy. The paper is theoretical and oracle-relative; it does not make claims about practical quantum-device performance.

### Later full-text follow-ups and status correction

The 2024 3-Forrelation conjecture is no longer an open lead. Uma Girish's [*Fourier Spectrum of Noisy Quantum Algorithms*](https://eccc.weizmann.ac.il/report/2025/154/) proves an `N^{Ω(1)}` query lower bound for 3-Forrelation in `1/2-BQP`. ECCC records the October 2025 report and, importantly, a June 18, 2026 revision that corrects an important issue in proofs of the main theorems. This audit uses the corrected revision as the current evidence. The old conjecture is a useful example of why a candidate question must be rechecked against later papers and revisions before being presented as unresolved.

We also checked two later full-text arXiv papers about dynamic structured edit distance: [*Dynamic Dyck and Tree Edit Distance: Decompositions and Reductions to String Edit Distance*](https://arxiv.org/html/2510.17799) (2025-10-20) and [*Hardness of Dynamic Tree Edit Distance and Friends*](https://arxiv.org/html/2511.09842) (2025-11-13). Their headline tree-edit results are not a direct contradiction. The first gives approximate algorithms (including a randomized `n^{1/2+o(1)}` approximation with `n^{o(1)}` expected amortized updates against an oblivious adversary, and a separate deterministic small-distance guarantee). The second proves conditional lower bounds for exact dynamic weighted tree edit distance and for combinatorial dynamic unweighted tree edit distance, with preprocessing/update/query costs explicitly included; it also acknowledges the approximate algorithm. Thus approximation factor, weightedness, algorithm class, adversary, and query/preprocessing accounting must be aligned before comparing “dynamic speedup.” Neither paper supplies a workload-driven latency/quality benchmark on evolving JSON/XML/LaTeX or repository edit traces.

## Synthesis and bounded research leads

These three in-frame papers do not form one comparable empirical area. Their shared methodological lesson is that headline results are conditional on the computational model and endpoint: RL lower bounds depend on MDP/oracle assumptions; dynamic edit-distance results trade approximation, update cost, probability, and adversary; quantum oracle claims describe query complexity. We therefore retain separate, scoped leads rather than ranking them.

### Lead A — dynamic structured-edit algorithms need demand-matched evaluation

Theoretical support now exists on both sides of a useful comparison: dynamic string edit distance has parameterized approximation/update tradeoffs, while later work transfers those methods to Dyck/tree edit distance and separate exact/combinatorial lower bounds. The sampled and follow-up papers motivate evolving structured data, but do not establish practical latency, memory, or approximation utility on real traces. Test whether the theoretical regimes help on versioned JSON/XML/LaTeX and repository edit sequences. Compare incremental methods with periodic exact/static recomputation under identical workloads; record update/query latency distributions, memory, approximation error against exact snapshots, edit burstiness, and adversary assumptions. The lead is weakened if no method improves the quality-latency-memory frontier over recomputation at realistic sizes; it is strengthened if improvements persist on held-out projects and edit traces. This is not a novelty claim, and the benchmark has not been run here.

### Lead B — characterize which RL hardness assumptions are essential

The sampled reduction proves a strong result under deterministic transitions and a narrow, explicit oracle/feature setup, while retaining polynomial-query statistical feasibility as counterevidence to any broader “RL is hard” slogan. A falsifiable theory program is to vary one assumption at a time—transition stochasticity, feature access/description, action count, and reward-oracle access—and either construct a matching reduction or give an efficient algorithm under the altered model. A claimed extension is falsified by a polynomial-time algorithm satisfying the same objective in that model; a claimed algorithm is falsified by an explicit hard instance or violated assumption. This is a proof agenda, not an empirical claim that the boundary is unknown across the whole RL literature; novelty has not been established.

## Scope and limitations

The three sampled records are the lexical-priority arm of one cell, not a random or representative sample of all 198,690 candidates. The citation follow-ups are purposively selected status checks and do not add sample-frame coverage. All three sampled PDFs were downloaded and extracted locally; follow-up papers were audited from their complete arXiv/ECCC full-text pages, not counted as sampled PDFs. We did not run algorithms, reproduce proofs independently, or complete a broad novelty search. No frequency, prevalence, or cross-domain ranking is inferred.
