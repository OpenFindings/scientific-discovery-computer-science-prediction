# Full-text audit batch 10 — fixed-frame random arm

Updated 2026-10-11. This batch adds four papers selected from the saved uniform-random arm, all in the 2015–2019 submission stratum. The notes below are based on the full text, including methods/results and stated limits; they are not claims about prevalence in the 198,690-paper candidate pool.

## 1. Cross-lingual transfer without shared vocabulary

**Paper:** Wu and Dredze, [Emerging Cross-lingual Structure in Pretrained Language Models](https://arxiv.org/pdf/1911.01464v3), arXiv:1911.01464v3. Sections 3–4, Table 1, and conclusion.

The authors train bilingual masked-language models and test zero-shot English-to-French/Russian/Chinese transfer on XNLI, NER, and dependency parsing. Their “no anchors” condition removes shared subword vocabulary yet retains shared prediction parameters. On average, removing lexical anchors changes XNLI by about −1.1 points, parsing by −0.9, and NER by −2.4; the authors note NER can even improve by about one point when averaged across the three target languages. Adding dictionary-derived anchors helps more for distant pairs (over three points on Chinese XNLI and NER), so anchors help but are not necessary in this setup. By contrast, making the bottom six Transformer layers language-specific causes much larger average losses: −22.6 XNLI, −38.7 NER, and −17.8 parsing. Changing pretraining domain from Wikipedia to Common Crawl also costs about 6.2 average NER points, compared with about 1.4 XNLI and 2.5 parsing.

**Interpretation and limits:** Shared upper Transformer structure and corpus/domain match look more consequential here than identical token strings alone. This is a controlled result on bilingual models (8 layers, 12 heads, 768 hidden), three transfer tasks, and three English-to-target pairs—not proof that vocabulary overlap is irrelevant for multilingual production models. The “no anchors” setup still shares other parameters, uses language-specific BPE, and retains a shared softmax; extra anchors help especially on distant pairs. NER corpus provenance also differs by language/task.

**Falsifiable follow-up:** At fixed compute and data, cross shared-layer depth, shared-vocabulary fraction, and matched/mismatched corpus domain across multiple language pairs and tasks. Test whether domain match and upper-layer sharing explain more variance in transfer than anchor count, with distant/low-resource language pairs predeclared as moderators.

## 2. Overfitting is a warning sign, not a complete privacy meter

**Paper:** Yeom et al., [Privacy Risk in Machine Learning: Analyzing the Connection to Overfitting](https://arxiv.org/pdf/1709.01604v5), arXiv:1709.01604v5, IEEE CSF 2018 (venue stated in the paper). Sections 2–5 and 6.1–6.4.

The formal analysis connects generalization error with membership-inference advantage and, under conditions on the target attribute’s influence, attribute inference. Experiments cover linear/tree models on Eye, IWPC (4,819 patients after missing-row removal), and Netflix data, plus CNNs on sampled MNIST/CIFAR-10/CIFAR-100. A simple threshold membership attack using one model query obtains recall above .99 and precision .505/.694/.874 on those three image datasets, close to a much more expensive shadow-model attack on the paper’s comparison. Attribute inference is not uniform: the attack gains on the two IWPC genomic attributes as overfitting rises, but the tested Netflix movie-rating attribute was not effectively inferred. The multi-query membership-to-attribute reduction beats direct inference on IWPC, while it is often slightly worse than the naive reduction on Netflix. The constructed colluding training-algorithm/adversary example reaches membership advantage at least .98 on sufficiently large CNNs with only 0.014, 0.047, and 0.031 accuracy loss on MNIST/CIFAR-10/CIFAR-100.

**Interpretation and limits:** Generalization gap can be a practical risk indicator for the tested attacks, but it is not a complete privacy guarantee or risk score. The authors construct a counterexample where a colluding, malicious learning rule leaks membership even while remaining stable / generalizing; attribute inference also depends on influence and the target attribute. Several demonstrations require assumptions such as access to training loss/distribution or model inversion, and the collusion result assumes a malicious training pipeline and sufficiently large CNN. The experiments use selected datasets and models, not a representative survey of deployed systems.

**Falsifiable follow-up:** On the same datasets and models, compare generalization gap, stability, attribute influence, and explicit privacy attacks under benign and adversarial training algorithms. Measure calibration of each risk proxy on held-out datasets; test whether gap-only triage misses high-leakage, low-gap cases.

## 3. Learned code mutants: syntax is not semantic validation

**Paper:** Tufano et al., [Learning How to Mutate Source Code from Bug-Fixes](https://arxiv.org/pdf/1812.10772v2), arXiv:1812.10772v2. Sections III–V, Table II, and validity threats.

The method mines about 787,178 GitHub bug-fixing commits, extracts roughly 2.3 million fixed-to-buggy transformation pairs, abstracts identifiers/literals, clusters transformations, and trains sequence-to-sequence models. The evaluation partitions each dataset 80/10/10 into train/validation/test. In the test data, exact reconstruction of the original buggy code ranges from 9% to 45% across models (e.g. 45% for M1, 9% for M2); syntactic correctness is reported as above 98% overall in the abstract, but only 94–98% for the specialized cluster models in the RQ2 summary. Some models have substantial “bad prediction” rates (31%, 27%, and 54% for GMident, GMident-lit, and M3 in Table II). Manual analysis used two of three author-judges per example with conflict resolution.

**Interpretation and limits:** The paper supports learning realistic-looking mutation patterns from fixes; it does not show that every syntactically valid mutant produces a useful test, a semantically distinct behavior, or a detected fault. The authors explicitly assessed behavior by inspecting mutated methods in isolation, which can misjudge behavior in system context. The corpus is mined rather than curated, large commits are excluded, and the main focus is Java methods of at most 50 tokens (larger 50–100-token methods reach about 6% perfect predictions under the same setup). The 9–45% range is model-dependent, not one pooled success rate.

**Falsifiable follow-up:** Re-evaluate learned mutants in their original projects, compile and execute them, and compare mutation score / generated-test yield against standard and domain-specific operators at equal budgets. Report syntax, compile, behavioral difference, fault realism, and test-detection as separate outcomes.

## 4. Multi-agent proximal planning: strong numerical evidence, no global-optimum guarantee

**Paper:** Bento et al., [Proximal Operators for Multi-Agent Path Planning](https://arxiv.org/html/1504.01783v1), arXiv:1504.01783v1. Sections 3–6 and Appendix A.

The paper extends collision-free trajectory proximal operators to arbitrary dimensions and introduces automatically assigned space-time landmarks. A Java implementation compares ADMM and TWA on synthetic scenarios. On the 3D CONF1 setup, TWA’s convergence time appears polynomial in agent count and parallel execution shows roughly 2× speedup with eight cores. Across 1,000 random initializations for this one scenario, objective values are described as similar/good. Six small landmark scenarios use two agents/four landmark trajectories and 100 restarts; a demonstration includes 10 agents and roughly 100 landmarks.

**Interpretation and limits:** This is evidence that the operators can be useful on the evaluated synthetic optimization problems, not that they guarantee globally optimal or physically validated robot plans. The paper explicitly says the proximal algorithms can get stuck in local minima. Several results are demonstrations/synthetic cases, and the smooth-trajectory discussion handles piecewise-linear paths by adding effective robot radius and fitting a polynomial; this is a modeling approximation that needs application-specific validation. The experiments do not establish performance on real robot hardware or broad obstacle-rich environments.

**Falsifiable follow-up:** Compare against current multi-agent planners on shared 2D/3D instances while varying density, obstacles, dynamics, and initialization. Report collision/constraint violations, objective gap against a lower bound, runtime, and success across many seeds; test whether restart/initialization policy changes the apparent scaling or success rate.

## Cross-paper synthesis from this batch

These four papers share no single scientific mechanism, so their results should not be pooled. They do share a useful evaluation lesson: a convenient proxy (shared token strings, train/test generalization gap, syntactic correctness, or objective value on a synthetic case) does not by itself establish the downstream outcome of interest. Each proxy needs an outcome-specific check and a clearly bounded claim. The four structured follow-up questions are in `data/research_findings_batch11.jsonl`.
