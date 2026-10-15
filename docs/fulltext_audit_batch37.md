# Full-text audit batch 37: the topic label is not the research question

Updated 2026-10-12. This batch closes the ten previously unread uniform-random records in the `continual_multimodal_learning` topic-period cells. Each sampled paper was checked against its arXiv full text (HTML or PDF); two already-reviewed records in this 12-paper random draw are included in the cross-paper synthesis below, not counted again. A citation follow-up checked two independent multimodal continual-learning benchmarks, including the 2025 MLLM-CTBench paper. These are audit observations from a small stratified draw, not a prevalence estimate for the 198,690-candidate pool.

## The ten newly audited sampled papers

### 1. Challenges in Representation Learning: A report on three machine learning contests (arXiv:1307.0414v1; 2013)

[Full text](https://arxiv.org/html/1307.0414).

This is a report about contest design, not a continual-learning algorithm. Its multimodal contest accidentally made perfect scores uninformative: contestants matched labels to images, and Hungarian matching let a weak classifier reach 100%; only one entrant submitted a model for verification. The report itself warns that leaderboard competitions are not controlled experiments. This is useful evidence about benchmark validity, but its match to the current topic label is a false positive.

### 2. An Empirical Investigation of Catastrophic Forgetting in Gradient-Based Neural Networks (arXiv:1312.6211v3; 2013)

[Full text](https://arxiv.org/html/1312.6211v3).

This is a direct continual-learning paper. It compares SGD/dropout and four activation functions under sequential task pairs, with 25 random hyperparameter settings per condition. Across three task relationships—input permutations, related sentiment domains, and dissimilar Amazon/MNIST tasks—dropout gives the best new-task/old-task trade-off in the tested setup. Activation rankings vary by task relationship. That is evidence that forgetting and method rankings depend on the task sequence, not that dropout is universally best on modern models or workloads.

### 3. Unifying Visual-Semantic Embeddings with Multimodal Neural Language Models (arXiv:1411.2539v1; 2014)

[Full text](https://arxiv.org/html/1411.2539).

This paper learns a joint image/text representation and a caption decoder, reporting image-sentence ranking and caption-generation results on Flickr8K/Flickr30K. It studies static multimodal representation and generation—not learning a sequence of tasks or retaining old tasks. It therefore belongs in multimodal learning, but not in a narrow continual-learning evidence pool.

### 4. Gated Multimodal Units for Information Fusion (arXiv:1702.01992v1; 2017)

[Full text](https://arxiv.org/html/1702.01992).

The GMU is evaluated on a synthetic modality-selection task and MM-IMDb genre prediction from plot text plus posters. On the one real dataset, its weighted F-score is 0.617 versus 0.600 for linear-sum fusion and 0.597 for concatenation (macro F-score 0.541 versus 0.530 and 0.521). The paper supports a modest, task-specific fusion gain; it does not test continual adaptation, cross-dataset transfer, or whether its learned gate is reliable under distribution shift.

### 5. Attention-Based Structural-Plasticity / Attention-Based Selective Plasticity (arXiv:1903.06070v1; 2019)

[Full text](https://arxiv.org/pdf/1903.06070).

This is a biologically inspired synaptic-importance method evaluated on Permuted MNIST and Split MNIST, using an MLP with two 400-unit hidden layers for the sequential permuted-MNIST experiment. The evidence is small benchmark-level evidence. It cannot be numerically ranked against the 2013 two-task/dropout study without matching architecture, task order, memory, training budget, and metrics; “competitive with state of the art” is not a cross-paper common outcome.

### 6. Disentangle-based Continual Graph Representation Learning (arXiv:2010.02565v4; 2020)

[Full text](https://arxiv.org/html/2010.02565).

This is genuine continual learning, but for knowledge-graph link prediction and information-network node classification. It uses FB15K-237/WN18RR and Cora/CiteSeer/PubMed, with randomly partitioned benchmark data to simulate an incoming stream. The authors report improvements over selected continual-learning baselines, while also noting instability on small CiteSeer. Its outcomes concern graph embeddings, so they should not be pooled with image-classification replay or vision-language instruction tuning.

### 7. UnDIAL: Self-Distillation with Adjusted Logits for Robust Unlearning in Large Language Models (arXiv:2402.10052v2; 2024)

[Full text](https://arxiv.org/html/2402.10052).

This is machine unlearning—removing targeted learned information—not continual learning in the usual “learn new tasks while retaining old tasks” sense. It evaluates GPT-Neo 125M and LLaMA-2 7B, and reports a trade-off between reducing memorization and preserving language utility; the paper explicitly limits its model coverage. Its use of catastrophic-forgetting language made it a lexical match, but it should be routed to privacy/unlearning rather than this topic.

### 8. PDAC: Efficient Coreset Selection for Continual Learning via Probability Density Awareness (arXiv:2511.09487v1; 2025)

[Full text](https://arxiv.org/html/2511.09487).

This is a direct continual-learning memory-selection paper. It evaluates Split-CIFAR10, Split-CIFAR100, and Split-TinyImageNet in offline and streaming settings, comparing against uniform, greedy, and other selection methods. The paper reports better accuracy/selection time for its tested settings; reported run averages use three independent runs in the streaming tables. This is evidence for the method on these image-classification protocols, not for multimodal learning. Its relevant follow-up question is whether gains remain under matched memory, compute, model, and task-order budgets across independent continual-learning regimes.

### 9. How does My Model Fail? ... Physical Plausibility Failure Modes with Matryoshka Transcoders (arXiv:2511.10094v2; 2025)

[Full text](https://arxiv.org/html/2511.10094).

This paper interprets failure features in generated images. It trains a physical-plausibility classifier using 3,410 human-labelled images plus 5,000 MS-COCO plausible images, then uses an MLLM to label learned features. It reports higher feature-relevance scores than its interpretability baselines and analyzes eight image generators. The authors explicitly say these features are not yet integrated into training to reduce failures and may miss rare failure types. It is not a continual-learning paper; its presence reflects broad keyword/topic-screen noise.

### 10. Evaluating Time Awareness and Cross-modal Active Perception ... via 4D Escape Room Task (arXiv:2603.15467v1; 2026)

[Full text](https://arxiv.org/html/2603.15467).

This introduces a simulated, interactive environment with 66 scenes and 1,032 objects, adding transient visual evidence, spatial audio, and misleading sounds to an escape-room task. The reported average escape rate is 72.73% for a GPT-4o agentic setup, 66.67% for Gemini 3 Pro, and 30.30% for Qwen3-Omni-Thinking; the paper notes the GPT-4o result uses separate vision-language and audio APIs, so it is not a like-for-like single-model configuration. This is direct evidence of a benchmark for active, time-sensitive multimodal interaction, but not evidence of real-world or physical-agent transfer.

## Cross-checks that change the interpretation

The phrase “multimodal continual learning has not been benchmarked” would be wrong. CLiMB (2022) already evaluated sequences of vision-language tasks, forgetting, transfer, and task-order effects; it found that common methods often did not deliver positive upstream transfer, and that adapters reduced forgetting in its ViLT setting. [CLiMB full text](https://arxiv.org/html/2206.09059)

The narrower problem has continued to evolve. MLLM-CTBench (2025; arXiv v3 in 2026) covers seven tasks across six domains, evaluates eight continual-learning methods and two task orders, and adds process-level reasoning diagnostics. It reports that model capability and task order affect results, and that algorithm families trade off differently by regime. This is evidence against treating one method ranking as universal; it also means “no multimodal continual-learning benchmark” is not a defensible novelty claim. [MLLM-CTBench full text](https://arxiv.org/html/2508.08275)

Likewise, CLiMB does not settle the more specific question tested by EscapeCraft-4D: active perception with spatial audio, transient clues, misleading audio, and irreversible time constraints. EscapeCraft-4D contributes an evaluation environment for that narrower combination, while remaining a small simulated benchmark and using non-identical model/API setups. The open question is transfer and robustness, not whether any multimodal continual-learning benchmark exists.

## What the 12-paper random draw actually says

The draw is not one coherent literature set. At least six sampled papers directly study sequential/continual learning (1312.6211, 1903.06070, 1905.11614, 2006.03875, 2010.02565, 2511.09487); other sampled items concern a contest report, static image-language representation/fusion, LLM unlearning, image-generation interpretability, and active multimodal evaluation. This is a useful retrieval-quality warning, not a claim about the composition of the full corpus. It also means the 12 items must not be treated as 12 replications of one hypothesis.

Within the actual continual-learning subset, the evidence is consistent on one bounded point: observed gains and forgetting depend on task sequence, benchmark, model, and memory/compute protocol. The 2013 gradient-based study found activation rankings change with task relation; CLiMB found task-order sensitivity and no positive transfer from common methods in its setting; the 2025 MLLM-CTBench reports method/model/task-order interactions; coreset papers test different buffers, datasets, and workloads, so their headline scores do not establish a universal selector ranking.

### Candidate research opportunity (not a novelty claim)

Run a matched, reproducible “method-ranking portability” study for continual learning. Select a small set of representative methods (including replay/coreset and regularization), then hold model, task data, sequence orders, memory, optimizer budget, and compute constant while testing unimodal vision, graph, and vision-language tasks. Report old-task retention, new-task adaptation, transfer, memory, wall-clock cost, and rank stability across at least five seeds. The opportunity is weakened if existing studies already provide this cross-regime, matched-budget design and show stable rankings; this audit found strong within-regime benchmarks but did not establish that none do.

Before scaling the literature miner or claiming field-level frequency, add an explicit “topic relevance” adjudication stage: mark direct fit, adjacent, and false positive; split mixed buckets into problem types; and estimate precision with a labeled random sample. A keyword match or broad taxonomy label is not itself evidence that a paper studies the target question.

## Audit boundary

The current 12-paper draw is complete at the record-disposition level; the two earlier audited items (1905.11614 and 2006.03875) are already in prior ledgers. This batch adds full-text checks for the ten remaining random items and one independent full-text benchmark follow-up, MLLM-CTBench; CLiMB was independently rechecked from its full text. The fixed frame is still only a sample of a much larger candidate pool. No prevalence estimate, global literature-gap claim, or universal continual-learning ranking follows from these records.
