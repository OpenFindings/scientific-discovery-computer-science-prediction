# Full-text audit batch 24: the “optimization/causal” screen is not one research lineage

Updated 2026-10-11. Audited all nine still-unread fixed-frame uniform-random records in `optimization_causal_science` for the 2015–2019, 2020–2024, and 2025–2026 arXiv-submission periods (three records per period), then returned to read both remaining 2010–2014 records. Together with the early-period item already audited in batch 10, this completes all 12 random-frame entries for this topic. The sample is heterogeneous by design of the title/abstract screen: active label acquisition, causal graph recovery, privacy inference, sequence design, commercial treatment assignment, image-domain generalization, scientific system identification, and a tutorial/theory note all appear under this one retrieval label.

## 2010–2014 records (early-cell completion)

### 10. An Active Learning Algorithm for Ranking from Pairwise Preferences with an Almost Optimal Query Complexity (2010 arXiv; v11 dated 2011)

[Ailon, arXiv:1011.0108v11](https://arxiv.org/abs/1011.0108); [full arXiv PDF](https://arxiv.org/pdf/1011.0108v11), §§1–4.

The paper studies ranking from pairwise preference queries, allowing non-transitive/noisy preferences. It reduces the number of queried pairs from the quadratic all-pairs universe to `O(n polylog(n, ε⁻¹))` for relative regret about `1+ε` against the same downstream learner with all pair labels, with a more explicit `O(ε⁻⁶ n log⁵ n)` bound for the decomposition subroutine. The theoretical guarantee is label/query efficiency—not a claim that noisy human preference labels become objectively correct. The paper illustrates the reduction with a regularized large-margin/SVM learner.

**Boundary:** the guarantee is relative to the loss of the comparison learner and relies on the paper's decomposition/local-chaos argument; it is not an absolute ranking-accuracy guarantee for arbitrary preferences. The full preference-aggregation problem is NP-hard (MFAST), and the authors distinguish query complexity from computation/solver cost. This is a theory-and-algorithm paper, not a user study measuring actual human annotation time or preference stability.

### 11. Visual Causal Feature Learning (2014)

[Chalupka, Perona, and Eberhardt, arXiv:1412.2309v2](https://arxiv.org/abs/1412.2309); [full arXiv PDF](https://arxiv.org/pdf/1412.2309v2), §§2–5 and Appendix 6.

The paper defines a causal macro-feature over image micro-variables and proves a Causal Coarsening Theorem: under its specified generative-model family, for almost all compatible distributions the partition induced by causal interventions is a coarsening of the observational partition. Intuitively, correlated pixel patterns can split observations into finer groups than the true causal classes. The proof assumes, among other model conditions, that target behavior follows the image and is not represented in the image; estimating class effects still requires intervention/causal data on representatives. Experiments include a synthetic grating task, where a manipulator's failure falls from about 40% initially to about 6% after iterative training, and an MNIST task with Amazon Mechanical Turk judgments to train minimal digit manipulations.

**Counterweight and boundary:** the authors explicitly choose simple CV examples to establish theoretical and algorithmic feasibility, not to engineer an advanced vision system. The synthetic grating data are generated from the assumed model; MNIST manipulations are a proof-of-concept on handwritten digits, and the manipulation distance grows as error decreases. Observational correlations alone do not automatically identify a manipulable visual cause: the paper's theorem is model-relative and its workflow uses causal labels/intervention results. The theorem's “almost all” statement is about a measure over the paper's generative models, not a guarantee for every real image distribution. arXiv v1 was submitted 2014-12-07 and v2 revised 2015-06-04; strata use first submission year.

## 2015–2019 records

### 1. MaxiMin Active Learning in Overparameterized Model Classes (arXiv first submitted 2019; v2 dated 2020)

[Karzand and Nowak, arXiv:1905.12782v2](https://arxiv.org/abs/1905.12782); [full arXiv HTML](https://arxiv.org/html/1905.12782v2), §§2–7.

The method queries the unlabeled example that most increases a minimum-norm interpolant's norm, with a second score based on the empirical unlabeled-data distribution. The paper proves that in a one-dimensional binary piecewise-constant setting, a two-layer ReLU minimum-norm learner reduces to bisection; its stated label complexity is `O(k log N)` for `k` appropriately sized pieces. Simulations show the function-norm criterion concentrates near decision boundaries, while the data-based criterion also selects examples representing clusters. A small MNIST demonstration uses a binary split of 1,000 vectorized images and compares test error against random query selection.

**Boundary:** the clean query bound assumes a one-dimensional, binary, piecewise-constant target with regularly sized regions. The paper itself says computational complexity can be a serious bottleneck for larger pools and leaves multiclass, regression, and other learner classes open. The MNIST run is illustrative, not a broad benchmark across datasets or annotator costs. arXiv first-submission year and v2 date differ; the frame uses the former.

### 2. Gradient-Based Neural DAG Learning / GraN-DAG (2019 arXiv; ICLR 2020)

[Lachapelle et al., arXiv:1906.02226v2](https://arxiv.org/abs/1906.02226); [full arXiv PDF](https://arxiv.org/pdf/1906.02226v2), §§2–5 and appendices.

GraN-DAG replaces discrete DAG search with non-convex continuous optimization and neural conditional models. Its experiments report structural Hamming distance (SHD) and structural intervention distance (SID), the latter tied more directly to downstream interventional adjustment errors. In the tested synthetic graph regimes it generally performs strongly against continuous baselines and is competitive with CAM/GSF; the authors provide comparisons and publicly available implementation. The paper also has real-data experiments, but the setting with identifiable synthetic nonlinear Gaussian additive-noise models is the clearest basis for exact graph recovery.

**Boundary and counterweight:** observational graph recovery is not possible in general without identifying assumptions; the paper assumes no hidden variables and focuses experimentally on nonlinear Gaussian additive-noise models. The optimization is non-convex and converges to stationary points, whereas the identifiability proposition is a population-optimum statement. Neural flexibility is not a guarantee of correct causal structure. Runtime is also material: the appendix reports roughly 10 minutes versus 1 minute for NOTEARS on 20-node graphs and about 4 hours versus 1 hour on 100-node graphs on the stated setup; GPU reduces the 100-node GraN-DAG time by about half. A method can improve graph metrics while costing substantially more compute.

### 3. An Active Learning Approach for Reducing Annotation Cost in Skin Lesion Analysis (2019)

[Shi et al., arXiv:1909.02344v1](https://arxiv.org/abs/1909.02344); [full arXiv PDF](https://arxiv.org/pdf/1909.02344v1), §§2–4 and Table 1.

The approach combines uncertainty/informativeness and representativeness for selecting labels, then adds pixel-space aggregation of within-class images. On two ISIC 2017 skin-lesion classification tasks, the paper reports results at 50% and 40% of its available labeled pool, respectively. For task 1, selection plus aggregation reports 0.860 accuracy versus 0.863 for the authors' full-data ResNet-101; task 2 reports 0.908 versus 0.903. Against its same-budget random baseline, the method improves several metrics, but effects are not uniform across measures.

**Counterexample and boundary:** the `SA + Mix-up` row is sharply worse on several metrics (task-1 accuracy 0.467 versus 0.860 for SA+AS; task-2 sensitivity 0.124 versus 0.756), so adding a familiar augmentation is not automatically beneficial. The evaluation uses two tasks from one challenge/archive pool, with 3,582 training images and fixed validation/test sets; it does not establish the same label savings for other clinics, prevalence, devices, or prospective readers. The paper's “state of the art” comparison excludes some leaderboard entries because they use extra demographics or substantially different external data, a necessary comparability caveat.

## 2020–2024 records

### 4. Distribution Inference Risks: Identifying and Mitigating Sources of Leakage (2022)

[Hartmann et al., arXiv:2209.08541v1](https://arxiv.org/abs/2209.08541); [full arXiv PDF](https://arxiv.org/pdf/2209.08541v1), §§III–VI.

The paper distinguishes distribution/property inference from individual-record membership inference, analyzes several leakage sources, formalizes a broader adversary class, and releases attack code. In one constructed four-party example (512 records per party), a causal model using the true causal parent avoids an inference signal that an associational model using a spuriously correlated feature exposes. Under a changed test correlation, the associational ERM is best on the in-distribution validation data but worst on the shifted test data; the causal ERM has the reverse ordering, with IRM between them. This is a concrete, mechanistic counterpoint to treating in-distribution accuracy as a privacy or robustness proxy.

**Boundary:** the causal-protection argument is conditional on knowing/learning the true causal feature structure and addresses a defined distributional-membership attack. The detailed example is synthetic, with specific structural equations, sample sizes, and party knowledge; it does not establish that causal learning generally prevents model leakage or does so without utility costs in arbitrary real deployments. More data can even increase leakage for some of the paper's modeled mechanisms.

### 5. Consistent Training via Energy-Based GFlowNets for Modeling Discrete Joint Distributions (2022)

[Ekbote et al., arXiv:2211.00568v2](https://arxiv.org/abs/2211.00568); [full arXiv PDF](https://arxiv.org/pdf/2211.00568v2), §§3–5 and Tables 1–2.

Joint Energy-Based GFlowNets train a sampler and energy model together. In a ten-round antimicrobial-peptide active-learning simulation, 1,000 candidates per round are scored by an oracle and scores above 0.75 are labeled positive. The endpoint emphasizes multiple objectives: DynaPPO has the highest reported performance score (0.938), while JEB-GFN is more diverse (31.83 versus 22.34 for GFlowNet-AL) but has somewhat lower score (0.922 versus 0.932) and lower novelty (24.26 versus 28.44). Thus the paper's result is a Pareto/tradeoff story, not “best on every outcome.”

**Boundary:** this active-learning evaluation uses a computational oracle/predictor and historical sequence data, not prospective wet-lab validation of the proposed sequences. The paper itself restricts generated objects to discrete values and leaves mixed discrete/continuous sequence generation open. A high oracle score, diversity, and biological efficacy are separate claims.

### 6. Improve ROI with Causal Learning and Conformal Prediction (2024)

[Authors, arXiv:2407.01065v1](https://arxiv.org/abs/2407.01065); [full arXiv HTML](https://arxiv.org/html/2407.01065v1), §§IV–V and Table II/Figure 6.

The proposed rDRP combines direct-ROI prediction with Monte Carlo dropout uncertainty and conformal calibration; calibration is applied to DRP's uncertainty term, not all estimators. Offline evaluation uses three public uplift datasets under sufficient/insufficient data and with/without covariate shift. It also reports four five-day online randomized tests on a short-video incentivized-advertising platform: users are randomly assigned to DRP, rDRP, or a random control at the same reward budget. Authors report significant rDRP revenue improvement over random control in three settings (the exception is sufficient data without shift). This is stronger real-outcome evidence than offline AUCC alone.

**Boundary and counterweight:** the paper's strongest operational claim is not uniform: the no-shift/sufficient-data online setting is explicitly the exception. The deployment is one platform and one advertising mechanism; tests last five days and full group sizes/uncertainty details are not stated in the retrieved description. Also, the conformal calibration construction only applies to the DRP family under the paper's formulation; it is not a generic guarantee for any causal/uplift learner.

## 2025–2026 records

### 7. “Casual Inference” via Style Bias Deconfounding for Domain Generalization (2025)

[Li et al., arXiv:2503.16852v1](https://arxiv.org/abs/2503.16852); [full arXiv HTML](https://arxiv.org/html/2503.16852v1), §§III–VI and Tables I–IX. The paper's title/index term spells “Casual” in place of “Causal.”

SDCL models style as a confounder, clusters styles with a style-guided expert module, and applies a back-door-style feature fusion module. It reports classification and segmentation results across digit, PACS, driving-scene, cross-device cardiac, and cross-modality abdominal-imaging benchmarks. Ablations generally improve the selected base systems—for example, PACS single-domain classification rises from 68.07 to 71.00 in one table, and the full method improves several baselines.

**Counterevidence and boundary:** gains are not universal in every dataset/domain cell. For example, with UDP on PACS single-domain classification, the art-domain score falls from 78.61 to 75.40 after SDCL even as the four-domain average rises; on abdominal cross-modality segmentation, some added modules barely move or can lower a specific direction's score. The paper offers benchmark-based evidence for the proposed representation/intervention mechanism, not randomized interventions on real-world style causes or a proof that the learned latent style variables are the true causal variables. Results vary with expert count/location, fusion coefficient, domain split, and baseline.

### 8. Weak Form Scientific Machine Learning: Test Function Construction for System Identification (2025)

[Tran and Bortz, arXiv:2507.03206v1](https://arxiv.org/abs/2507.03206); [full arXiv PDF](https://arxiv.org/pdf/2507.03206v1), §§2–5 and Appendices.

This paper selects the support radius for single-scale local weak-form test functions using an estimated quadrature/integration error. It evaluates four canonical ODEs (logistic growth, Duffing, Lorenz, and FitzHugh–Nagumo), noise levels, polynomial orders, and temporal resolutions, with 100 independent trials per setting. Relative to a multiscale-global basis, the local method is often faster; in the reported IRLS comparisons it is roughly 60–70% faster on several systems.

**Counterexample and boundary:** the estimated critical radius does not always align with minimum parameter error. Under OLS at higher noise, it deviates for logistic growth and FitzHugh–Nagumo; IRLS corrects the logistic quadratic-bias case but does not fully correct the cubic FitzHugh–Nagumo case at high noise. MG's orthonormalization can also improve conditioning and convergence in some high-noise Lorenz/IRLS comparisons despite added SVD cost. The evidence is simulation over four canonical dynamical systems; the paper does not show transfer to noisy real experimental time series in this evaluation.

### 9. A Unified Theory for Causal Inference: Direct Debiased Machine Learning via Bregman–Riesz Regression (2025)

[Kato, arXiv:2510.26783v1](https://arxiv.org/abs/2510.26783); [full arXiv PDF](https://arxiv.org/pdf/2510.26783v1), §§1–5 and conclusion.

This ten-page note connects Riesz regression, covariate balancing, density-ratio estimation, TMLE, and matching through targeted Neyman estimation and Bregman–Riesz regression. It defines an average treatment effect estimand and states familiar identification assumptions, including unconfoundedness, positivity, and bounded outcomes. It recommends a practical combination of entropy balancing for the Riesz representer and TMLE for the final estimator.

**Boundary:** the note explicitly summarizes and synthesizes Kato's 2025 companion papers; its cited theoretical details and simulations live in those other works. It is not an independent new empirical head-to-head showing that one method improves ATE accuracy on fresh data. Its algebraic unification also depends on model/loss choices (the note distinguishes linear-model/Riesz and logistic/KL cases). Counting it as a new trial or independent replication would inflate evidence.

## What the nine papers support—and what they do not

The screen label `optimization_causal_science` is a retrieval bucket, not a valid single outcome family. Even the nine papers above measure incompatible quantities: label-query count/test error; SHD/SID; skin-lesion accuracy, sensitivity and specificity; attack accuracy/leakage; peptide score/diversity/novelty; ad revenue/AUCC; OOD accuracy or Dice; parameter error/runtime; and ATE-estimator relationships under identification assumptions. A cross-era graph of any one of those metrics would be invalid without narrowing the task and denominator first. arXiv submission periods also do not equal venue year (GraN-DAG was submitted in 2019 and appeared at ICLR 2020; MaxiMin v2 is dated 2020 after a 2019 submission).

There are also real positive and negative controls within this slice: online randomized revenue tests in rDRP support a setting-specific operational gain, while a fourth setting does not show the same significant improvement; causal graph recovery's strong synthetic results rely on identifiability/model assumptions and cost more runtime; skin-lesion label savings are promising on two tasks but a mix-up variant collapses on several metrics; and peptide optimization trades score against diversity/novelty. These differences motivate the following bounded tests rather than a broad “causal AI works” conclusion.

**Falsifiable test A (topic taxonomy):** use a fresh stratified sample from the 18-subfield frame; blinded coders label each full text with task family, estimand, evidence type, data source, metric and denominator, and causal-identification assumptions. Compare title/abstract-only grouping against full-text coding using agreement, false cross-family synthesis rate, and the number of apparent temporal trends that disappear after task-level stratification. The retrieval-bucket hypothesis is weakened if the broad screen label reliably predicts a common estimand and metric family.

**Falsifiable test B (sample-efficiency evidence):** for active-learning or generative-design papers, compare methods at matched oracle/label budgets and report both the task-specific quality metric and all claimed secondary objectives (error/clinical sensitivity-specificity; reward/diversity/novelty; or revenue). Include multiple datasets, seeds, and an independent real outcome when feasible. The proposed reporting concern is weakened if single headline metrics preserve method rankings across budgets, secondary outcomes, and external evaluation.

This batch audit reads 11 new frame items; with the previously reviewed item, all 12 random-arm records for this topic are now audited. It is not a review of all candidates in the 198,690-paper pool, a meta-analysis, a trend estimate, or a novelty claim.
