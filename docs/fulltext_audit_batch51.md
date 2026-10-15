# Full-text audit batch 51: selective learning, birthday repetition, and stochastic routing

Updated 2026-10-12. This batch closes the three lexical-priority items in the frozen `algorithms_complexity × 2015–2019` cell. The topic label is broad; the papers concern different theoretical problems and their outcomes are not pooled. All three exact-version PDFs were retrieved and reviewed; two purposively selected later full-text follow-ups were checked to adjudicate open-question status.

## Sampled papers

### 1. A Birthday Repetition Theorem and Complexity of Approximating Dense CSPs (arXiv:1607.02986v1; first submitted 2016)

[arXiv record](https://arxiv.org/abs/1607.02986); [ICALP 2017 proceedings record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2017.78); local PDF: `data/fulltexts/arxiv/1607.02986v1.pdf` (45 pages); extracted text: `data/fulltexts/text/1607.02986v1.txt`.

The paper proves exponential decay in the birthday-repeated game's value, roughly in `kl/n`, under stated game regularity and alphabet assumptions, and applies the theorem to fine-grained dense Max-k-CSP hardness, Sherali–Adams algorithms, Lasserre integrality gaps, and Densest k-Subhypergraph. It resolves a 2014 question, but its own conclusion records remaining gaps: low-value games, tight dependence on the soundness gap and alphabet parameter, and the `k`-dependence of running time.

The low-value question needs a status qualification. Young Kun Ko's 2018 ECCC report proves bounds for a *refined* birthday repetition, where vertices are independently included rather than choosing uniformly among fixed-size subsets; it also proves repeated-repetition decay for projection games. That is meaningful related progress, not a direct proof of the exact 2016 statement for the original fixed-size operator and general games. The open-problem status should therefore be tracked by operator, game class, and target bound rather than copied forward as either fully open or fully solved.

### 2. A Theory of Selective Prediction (arXiv:1902.04256v3; first submitted 2019)

[arXiv record](https://arxiv.org/abs/1902.04256); local PDF: `data/fulltexts/arxiv/1902.04256v3.pdf` (14 pages); extracted text: `data/fulltexts/text/1902.04256v3.txt`.

The sequence is arbitrary but fixed before the randomized learner acts; after seeing a prefix, the learner chooses exactly one future window and predicts a statistic of that window. For the mean of bounded observations, expected squared loss is `O(1/log n)` with a matching lower bound; smooth statistics and bounded concatenation-concave statistics receive related guarantees. The paper also introduces “fitting unseen data” with a model class and states an open question about the dependence of excess risk on the class size.

This is not the standard selective-classification/abstention problem. The learner chooses *when* and *which future window* to predict, and the adversarial sequence is not adaptive to that choice. If the adversary knows the chosen time or window in advance, the paper shows even mean prediction can suffer constant loss.

### 3. Algorithms and Adaptivity Gaps for Stochastic k-TSP (arXiv:1911.02506v1; first submitted 2019; ITCS 2020)

[arXiv record](https://arxiv.org/abs/1911.02506); [ITCS 2020 proceedings and abstract](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2020.45); local PDF: `data/fulltexts/arxiv/1911.02506v1.pdf` (25 pages); extracted text: `data/fulltexts/text/1911.02506v1.txt`.

For Stoch-Reward k-TSP, each vertex has an independent, explicitly given discrete reward distribution; reward is observed on visiting, and the objective is expected tour length to collect reward at least `k`. The paper proves a non-adaptive `O(1)` approximation, resolving the prior `O(log k)` adaptive / `O(log² k)` non-adaptive gap. It also proves a constant adaptivity gap for its Stoch-Cost k-TSP model, where independent stochastic vertex costs are added to tour length. Polynomial-time algorithms are obtained when distribution supports are polynomial-size. Independence, the metric tour structure, and the particular threshold/sum objectives are assumptions—not incidental implementation details. The paper itself contrasts stochastic Orienteering, for which it cites a superconstant adaptivity gap; that neighboring result blocks generalizing “constant gap” to stochastic routing as a whole.

## Findings and status updates

1. **Resolved selective-learning question (status correction, not a new open problem).** Qiao and Valiant's 2019 paper asks whether the excess risk for selecting a model to fit a future window can depend much more mildly on model-class size. Their 2021 COLT paper, *Exponential Weights Algorithms for Selective Learning*, proves expected excess risk `O((log log |L| + log log n)/log n)` for a non-adaptive learner and gives an almost matching lower bound in key regimes. It also shows a distinct bounded-recall restriction has a worse, nearly tight `O(sqrt(log |L|/log n))` dependence. Thus the 2019 question is resolved for the unrestricted selective-learning model, while memory/recent-window constraints have a different tradeoff. This does not establish a result for ordinary abstaining classifiers.

2. **Birthday-repetition status is definition-sensitive.** The 2018 refined-operator result establishes nontrivial value reduction and repeated decay for projection games, including when the original game has a low value, but changes the subset-sampling distribution and has game-class/parameter conditions. It is evidence that the 2016 open direction advanced, not evidence that every form of the original fixed-size, general-game low-value theorem is settled. A question registry should retain the exact operator, game class, and asymptotic target as fields.

3. **Stochastic k-TSP yields a narrow adaptivity result, not a routing-wide rule.** The constant adaptivity results rely on independent per-vertex uncertainty and the k-threshold objectives. A bounded theory lead is to characterize which dependence structures (starting with pairwise or negative dependence) preserve a constant adaptivity gap, and to identify the first condition permitting a growing gap. The test is a theorem or an explicit family of instances under precisely stated distributional assumptions. Existing stochastic-Orienteering counterevidence means the lead must compare objective and feasible-policy definitions, not just reuse the word “routing.” No new theorem or novelty claim is made here.

## Scope and limitations

The three sampled papers are purposive lexical-priority items from one topic-period cell, not a representative estimate of CS research. The two later works were selected as citation follow-ups, not as a systematic census. No proof was independently reconstructed, no algorithms were implemented, and the stochastic-k-TSP extension above remains a research lead. The full 198,690-record corpus is still not full-text audited.
