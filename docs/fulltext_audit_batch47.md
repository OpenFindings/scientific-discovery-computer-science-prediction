# Full-text audit batch 47: forgetting depends on memory access and on what is measured

Updated 2026-10-12. This batch closes three previously unread lexical-priority records in `continual_multimodal_learning × 2020–2024`. The topic label is only a retrieval aid: one paper studies online visual few-shot learning and two study LLM fine-tuning. Their reported outcomes are not pooled or directly compared.

## Sampled papers

### 1. Lifelong Wandering: A realistic few-shot online continual learning setting (arXiv:2206.07932v1; 2022)

[arXiv record and full text](https://arxiv.org/abs/2206.07932); locally retrieved PDF: `data/fulltexts/arxiv/2206.07932v1.pdf` (5 pages; SHA-256 recorded in the download manifest).

The paper builds an online, few-shot stream from RoamingRooms/Matterport3D: four environments per episode, 100 frames per environment, 40% labelled examples, batch size one, and no separate training/evaluation phase during the stream. It measures both online accuracy and degradation on previously seen environments. Its table gives CPM 73.26 ± 5.11 online accuracy with 31.11 ± 7.65 forgetting; OAP, a simpler online-averaged-prototype method, gives 69.23 ± 5.57 and 5.91 ± 3.39; LwF gives 56.03 ± 6.79 and 2.38 ± 4.82. In this protocol, stronger online adaptation can cost retention, and OAP is a better balance than CPM by the paper's two reported endpoints. The authors also state that replay-based methods are omitted because storage/privacy makes that setting less realistic. This is a small workshop benchmark with a frozen ResNet-12 feature extractor at evaluation and four environments per episode, not a general result about current multimodal or language models.

### 2. Analyzing and Reducing Catastrophic Forgetting in Parameter Efficient Tuning (arXiv:2402.18865v1; 2024)

[arXiv HTML full text](https://arxiv.org/html/2402.18865); locally retrieved PDF: `data/fulltexts/arxiv/2402.18865v1.pdf` (17 pages).

I-LoRA combines two LoRA learners with experience replay: historical examples are stored in an episodic buffer and mixed with the current task; an embedding-preservation term links a fast learner to an exponential-moving-average slow learner. It uses Llama-2-7B and eight listed domain tasks (the table caption inconsistently calls these “nine” benchmarks), 5,000 training and 500 evaluation examples per task, and reports average accuracy and backward transfer. I-LoRA has the highest listed average accuracy on seven of the eight table columns, but it does not win every task: EWC leads MeetingBank (35.9 vs. I-LoRA 30.6). Its backward-transfer values remain negative after most task sequences; e.g., MeetingBank is −12.7, compared with −10.2 for EWC and −10.1 for PP. Thus the results support improved retention/adaptation on these Llama-2 tasks, not elimination of forgetting. The paper's headline “up to 11%” should not be treated as a universal gain or a common cross-paper effect size. The authors say theoretical analysis of mode connectivity remains future work.

### 3. Controlled Low-Rank Adaptation with Subspace Regularization for Continued Training on Large Language Models (arXiv:2410.16801v2; 2024)

[arXiv HTML full text](https://arxiv.org/html/2410.16801); locally retrieved PDF: `data/fulltexts/arxiv/2410.16801v2.pdf` (15 pages).

CLoRA constrains the direction of LoRA updates through orthogonality regularization against a pre-defined subspace, without keeping a replay buffer. In its one-stage Llama-2-7B fine-tuning experiments, CLoRA's effect changes with the regularization size `k` and task: larger `k` helps the commonsense setup, while the math results peak around `k=128` and fall at `k=256`. Importantly, some of the paper's capacity/forgetting analysis defines forgetting as a relative output-change proxy, not as the same old-task accuracy/BWT endpoint used by I-LoRA. In its separate continual-learning tables with T5-large, CLoRA scores 79.0 average final-task accuracy on the standard benchmark, ahead of O-LoRA's 75.8, but on the large-task benchmark scores 68.1 versus O-LoRA's 69.6 and below per-task fine-tuning's 78.1. This is direct counterevidence to an unconditional “CLoRA is best” reading. The authors list random regularizer initialization and proxy measurement of capacity/forgetting as limitations.

## Synthesis and bounded research lead

These papers expose two linked design choices that are usually hidden by a single “forgetting” headline: whether the method may retain/replay old data, and whether retention is measured by old-task accuracy, backward transfer, or a parameter/output-change proxy. The online visual study excludes replay on realism grounds; I-LoRA depends on a historical-example buffer; CLoRA avoids that buffer but uses a different update constraint and, in one analysis, a different forgetting proxy. The models, modalities, training streams, and metrics differ, so these observations do not establish a ranking between papers or prove that any prior literature lacks a matched comparison.

## Bounded, falsifiable next experiment

On one fixed continual LLM task sequence and base model, compare a replay method (including I-LoRA-style replay), a replay-free regularizer (including CLoRA/O-LoRA), and sequential fine-tuning at pre-registered historical-data budgets of zero, small, and larger buffers. Match trainable parameter count, current-task examples, optimizer steps, and accelerator-time budget as closely as implementation permits; repeat task orders and seeds. Report per-task old/new accuracy, BWT/forgetting, learning of the incoming task, buffer bytes/privacy exposure, training/inference cost, and output-change proxy separately. The memory-conditional lead is weakened if the same method remains best on retention and adaptation across buffer budgets under common metrics; it is strengthened if rankings or the retention/plasticity frontier change with memory allowance. This experiment has not been run here, and the design is not a novelty claim.
