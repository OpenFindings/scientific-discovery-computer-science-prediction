# Full-text audit batch 77 — security and privacy, 2025–2026

## Scope

This closes the frozen six-version cell `security_privacy × 2025–2026-through-10-11`: three lexical-priority papers newly read and three uniform-random records previously audited in batches 15 and 34. New reads are a private joint-independence test, an empirical/theoretical analysis of correlation-induced leakage in local DP, and fully adaptive f-DP privacy filters. The first paper is cross-listed in statistics; its inclusion here reflects the frozen topic label, not a claim that every contribution is a computer-systems study.

The new PDFs total 6,371,314 bytes / 121 pages. Six provenance/reconciliation rows are in `data/fulltext_review_ledger_batch77.jsonl`.

## New full-text reads

### Differentially Private Joint Independence Test (2503.18721v3)

The paper develops a differentially private permutation test using d-variable HSIC (dHSIC), with privacy/level/consistency results and minimax separation guarantees. Its DP bootstrap counterpart has non-vanishing sensitivity in this construction and can have inconsistent power; the authors explicitly do not generalize that negative result to all bootstrap-based kernel tests. Experiments include 500 repetitions for level and 200 for power across selected Gaussian settings, plus a causal-inference dataset analysis. In its comparison, a sequence of pairwise DP-HSIC tests spends privacy budget across tests and can add substantial noise; the direct joint dHSIC method is particularly strong when dependence is primarily joint rather than pairwise. This is evidence about detecting dependence under a DP release, not a direct measure of how much an attribute-inference adversary learns from locally perturbed records.

### The Hidden Cost of Correlation: Rethinking Privacy Leakage in Local Differential Privacy (2508.12539v1)

This paper evaluates GRR, RAPPOR, OUE, OLH, and the Exponential mechanism on four real-world datasets, and proposes a framework for correlation-induced privacy leakage (CPL) under general approximate `(ε,δ)`-LDP. It finds that common symmetric summaries such as Pearson correlation and mutual information can miss the direction and mechanism-specific amount of attribute-inference leakage. Importantly, its conclusion says severe CPL was rare in the studied data; it does not claim correlation routinely defeats LDP. Results are conditioned on the authors' distributional estimates and attack setup; the paper explicitly says mismatch between assumed and actual data distributions can make CPL suboptimal and leaves this for future work. Several experiments use GRR after an initial comparison and replicate source records to improve conditional-distribution estimation, so the real-data results should not be treated as an independently collected, population-representative attack-rate study. The paper says artifacts would be made available “soon”; no package was linked in the reviewed PDF.

### $f$-Differential Privacy Filters: Validity and Approximate Solutions (2602.06756v2)

The paper proves that the natural path-wise `f`-DP filter can be invalid under fully adaptive mechanism selection when possible trade-off functions are not Blackwell-ordered. It provides necessary/sufficient validity conditions and an approximate GDP-filter construction for subsampled Gaussian mechanisms in asymptotic low- and high-subsampling regimes. It explicitly cautions that the CLT approximation can be optimistic at realistic rates: at `q=0.1`, the authors report underestimation of privacy loss; the empirical CDF discrepancy in a displayed simulation is about 0.0125. Its tightness comparison is against a structurally matched single-order RDP baseline, not multi-order RDP. This is a mathematical accounting boundary, not proof of a production DP deployment being vulnerable.

## Reconciled random arm

Three prior random-arm audits are reconciled without counting new reads:

- `2502.17698v1`, “The Cyber Immune System,” is a position essay, not an evaluated defense. A date inconsistency is recorded in its earlier audit; that is a provenance concern, not evidence that its claims are false.
- `2503.02097v1`, “Bomfather,” instruments a single Go container build to map file/library accesses. Provenance inventory is not itself a privacy guarantee or demonstrated attack reduction; it was previously marked a privacy-topic retrieval false positive.
- `2506.20828v3`, “Practical and Accurate Local Edge Differentially Private Graph Algorithms,” reports graph-specific utility under local edge-DP. Edge adjacency is a different protection unit from user-level LDP and the paper's single-machine distributed simulation is not a multi-machine deployment. It is not directly comparable to attribute-level CPL.

## Findings and falsifiable leads

### Finding 157 — Test whether private dependence detection improves directed leakage control

The sampled papers provide adjacent components, not an established integrated solution: dHSIC can test higher-order independence under a DP release; the LDP study finds that symmetric correlation metrics can fail to characterize directed, mechanism-specific attribute leakage; and the LDP study's estimates depend on distributional assumptions that can drift. The research lead is to test whether a private dependence screen can safely guide *which* attribute pairs/groups receive stronger perturbation or a smaller release budget, while measuring directed CPL and utility under held-out and shifted distributions. This is not a claim that private dependence testing or correlation-aware privacy is new. Prior work includes private conditional-independence tests and a survey of correlated-data DP; the novelty boundary is a specific calibrated screen-to-budget pipeline with adversarial leakage outcomes.

**Test:** On at least two multi-attribute datasets plus synthetic higher-order dependence, compare (a) Pearson/MI policy, (b) DP-dHSIC screening, (c) an oracle dependence graph, and (d) a uniform LDP baseline. Train/hold out the distribution used for calibration, then inject temporal/domain shift and asymmetric attribute-inference attacks. Measure type-I error/FDR of selected dependencies, directed CPL, utility, and privacy guarantee under each policy. The lead weakens if dependence-screened policies do not beat uniform LDP on a pre-registered utility-at-fixed-leakage curve, or if distribution shift destroys calibration.

### Finding 158 — Keep fully adaptive privacy filters inside their proved operating regime

The f-DP paper supplies a sharp caution: exact path-wise composition is not automatically a valid stopping filter under arbitrary adaptive mechanism choice, and its faster approximate GDP proposal is justified asymptotically near subsampling rates `q→0` or `q→1`, not at all realistic intermediate rates. Its own simulation shows optimistic accounting at `q=0.1`. The bounded research lead is an auditable regime-aware accountant that detects whether assumptions (mechanism family, Blackwell ordering, adaptivity, sampling rate, and approximation error) hold, then falls back to a valid conservative bound when they do not. The theorem and limitation are already identified by the paper; this is an engineering/validation target, not a new mathematical theorem claim.

**Test:** Implement the exact-validity conditions and asymptotic approximation guard in a reference accountant; generate adaptive heterogeneous mechanism sequences spanning ordered/unordered trade-off curves and `q` from sparse to intermediate to near-one. Compare predicted bounds against high-precision privacy-loss distributions and a valid multi-order RDP accountant. Require no underestimation outside the declared asymptotic tolerance; measure utility loss from fallback. The lead weakens if existing production accountants already enforce equivalent checks or the proposed guards do not prevent underestimation.

## Limitations

This is one frozen six-version cell and only three new full texts. These papers use distinct threat models: private statistical testing, attribute leakage under local DP, and adaptive composition accounting. They must not be collapsed into one privacy metric. The real-data CPL study covers four datasets and a particular attacker/distribution setup; the dHSIC simulations cover selected distributions; the f-DP approximation has explicit asymptotic limitations. Follow-up review is targeted, not a systematic review of privacy accounting or correlated-data DP.
