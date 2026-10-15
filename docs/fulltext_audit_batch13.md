# Full-text audit batch 13 — “efficiency” is not one outcome

Updated 2026-10-11. This batch reviews six papers selected from the fixed-frame uniform-random arm, all in the model-efficiency topic but spanning four arXiv submission periods. The papers optimize different resources, so their reported improvements are not pooled or treated as head-to-head results.

## 1. Tensorial compression (2018): good average headline hides architecture sensitivity

**Sample:** Su et al., [Tensorial Neural Networks: Generalization of Neural Networks and Application to Model Compression](https://arxiv.org/html/1805.10352v3), arXiv:1805.10352v3. Read method, CIFAR-10 compression tables, convergence and task-scope sections.

On ResNet-32/CIFAR-10, the uncompressed model is reported at 93.2% test accuracy. In the table that holds sequential compression fixed, at 10% of the original parameter count, tensorial mCP reaches 91.28% versus 88.50% for conventional NN-CP; mTK reaches 81.59% versus 86.73% for NN-TK; and mTT reaches 87.89% versus 87.08% for NN-TT. Thus even under that more controlled comparison, not all tensorized variants win. The paper separately compares sequential and end-to-end training/compression, so it is unsafe to attribute every gain to “tensorization” alone. Other tests include LeNet/MNIST and ResNet-50/ImageNet, but the sharp counterexample above is within the same CIFAR table and parameter rate.

**Bound:** useful evidence that parameter reduction can preserve task quality when the tensor structure/decomposition is appropriate; not evidence that any low-rank/tensor compression recipe does so, nor a direct measurement of wall-clock speed or device energy.

## 2. Post-training INT7 (2020): deployment speed and task accuracy can diverge

**Sample:** Wu et al., [EasyQuant: Post-training Quantization via Scale Optimization](https://arxiv.org/html/2006.16669v1), arXiv:2006.16669v1. Read the calibration algorithm, task tables, and ARM latency tables.

EasyQuant alternates weight/activation scale search, layer by layer, using 50 calibration examples in its own experiments (the TensorRT comparison uses 1,000). On ImageNet classification, INT7 ResNet-50 reaches 75.04% versus 75.20% FP32, while INT7 TensorRT is 72.78%. On VOC2007 MobileNet-SSD detection, however, INT7 EasyQuant is 68.79 mAP versus 72.04 FP32: materially lower despite improving over INT7 TensorRT’s 63.88. On two RK3399 ARM boards it reports lower latency than its INT8 TensorRT baseline for each listed model; e.g. one four-thread setting gives SqueezeNet 44 vs 66 ms and ResNet-50 300 vs 415 ms. The authors also note detection mAP drops sharply below seven bits.

**Bound:** unusually useful because it measures real hardware, not just parameter count or simulated FLOPs. Still limited to the tested CNNs/tasks and two older ARM platforms; the claimed benefit depends on their integer kernel, compiler/runtime, and model workload. Near-FP32 classification does not imply similar preservation for detection.

## 3. LoRA (2021): parameter-efficient fine-tuning is not a smaller base model

**Sample:** Hu et al., [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/pdf/2106.09685v2), arXiv:2106.09685v2; ICLR 2022. Read method, GLUE/large-model tables, adapter latency comparison, and storage/training claims.

LoRA freezes the pre-trained weights and learns small low-rank updates that can be merged into the base weights at inference. On RoBERTa-large/GLUE, it reports 0.8M trainable parameters and average score 89.0, versus 355M parameters and 88.9 for full fine-tuning. However, the paper marks the full-fine-tuning baseline as reported from prior work rather than a matched rerun, so the 0.1-point difference is not a paired comparison. For GPT-3 175B, reported training throughput rises from 32.5 to 43.1 tokens/sec/GPU on V100. Its multi-task storage example is 350 GB for the shared base plus 35 MB per task, rather than storing 350 GB for every fine-tuned instance.

The boundary is crucial: the 175B base checkpoint is still required at deployment. LoRA mainly cuts *per-task trainable state, optimizer/training burden, and incremental storage*; it does not shrink the shared base model or reduce its full-model forward pass. The “no extra inference latency” claim presumes merging the learned update into the base weights. In contrast, the paper measures substantial online latency penalties for sequential adapter baselines at batch size one (e.g. 20.7% and 30.3% in the cited GPT-2-medium setup for two adapter designs).

## 4. Inheritune (arXiv 2024; TMLR 2026): smaller model benefits from a larger model’s learned layers

**Sample:** Sanyal et al., [When Attention Collapses: How Degenerate Layers in LLMs Enable Smaller, Stronger Models](https://arxiv.org/pdf/2404.08634v4), arXiv:2404.08634v4; published in TMLR in February 2026. The final paper body, result tables, ablations, and limitations were checked. Do not treat the v4/TMLR result as knowledge available at the 2024 arXiv cutoff.

The authors report rank-one-like attention in some deeper GPT-2 layers and propose Inheritune: initialize a shallower model with layers inherited from a larger pre-trained model, then progressively train/expand it. For example, a 16-layer GPT-2 Medium initialized this way scores 48.08 average on five listed zero-shot tasks, versus 47.74 for the 24-layer full-size model and 46.84 for a randomly initialized 16-layer model. These models use OpenWebText training; a 16-layer variant is trained for 100K steps while the same-size scratch baseline gets 200K steps. This supports a warm-start benefit and fewer new training steps in the tested configuration—not “a smaller model is free”: acquiring the larger checkpoint and its pretraining cost is outside that comparison. The paper’s stated limitations focus on Pre-LN architectures and a particular midpoint/early-layer initialization strategy.

## 5. MoE-Lens (2025): throughput gains are specific to offline batches, hardware, and request mix

**Sample:** Yuan, Ma, and Talati, [MoE-Lens: Towards the Hardware Limit of High-Throughput MoE LLM Serving Under Resource Constraints](https://arxiv.org/pdf/2504.09345v1), arXiv:2504.09345v1. Read its performance model, evaluation method, benchmark results, and workload discussion.

MoE-Lens targets CPU-GPU hybrid inference when the model and KV cache do not fit in GPU memory. On a dual-socket server with Intel Platinum 8380 CPUs and NVIDIA A40 GPUs (experiments isolated to one socket and GPU), it reports 4.6× average throughput improvement over MoE-Lightning. The headline “up to 25.5×” is workload-specific: the paper attributes it to RAG workloads, where the speedup averages 19.4×; AIME 2024 reaches up to 9.9× (4.7× average). In the general Figure 11 comparison against MoE-Lightning, the maximum is 12.4×; the paper separately reports that the gain is larger with a 210GB than a 70GB KV cache. Thus the max headline is not a general system-wide multiplier. Their explicit target is offline/batched throughput, not interactive per-request tail latency. The evaluated systems use substantial CPU memory (750 GB available) and a particular A40/CPU interconnect profile.

**Bound:** the systems result is a measured improvement on a real server, but transfer to another CPU/GPU/interconnect, memory budget, prompt-generation mix, or latency-first service is not established. It is a serving scheduler result, not evidence that MoE models intrinsically use less hardware.

## 6. Quantization degradation (2026): bit width alone does not predict retained capability

**Sample:** Zhou et al., [Quantization Degradation in Large Language Models: A Signal–Noise Perspective](https://arxiv.org/pdf/2608.08188v1), arXiv:2608.08188v1. Read method, retention tables, task/scale analysis, and signal-noise decomposition.

This study evaluates 76 weight-only quantized configurations across five model families, four quantization methods, four bit-widths, and 11 downstream benchmarks. Its main metric is *de-randomized retention* relative to the paired full-precision score, not raw accuracy. At W3 (3-bit), method choice is large: Llama-2-7B retention is 60.0% with round-to-nearest, 81.6% with GPTQ, and 89.2% with SPQR. Scale matters too: under GPTQ, Qwen3-0.6B W3 overall retention is 30.6%, versus 87.9% for Qwen3-14B. The task types also differ: on the smaller Qwen3 models, knowledge and reasoning retention can be far below commonsense retention. W4 generally retains more than W3; W2 causes severe degradation in the evaluated configurations.

The proposed explanation separates quantization error introduced within a layer from its attenuation/amplification across layers. That is a mechanistic account tested within their model/task setup, not a guarantee that the derived SNR is a deployment quality metric. The benchmark uses fixed small task subsets (e.g. 128 examples per task in the described construction) and evaluation conventions that matter; de-randomized retention can exceed 100% when the quantized model beats the full-precision baseline on a particular finite benchmark.

## Cross-paper synthesis and next test

These six random-frame papers do not support a single claim that “compression makes models cheaper without hurting quality.” They show different, narrower wins:

- Tensorization reduces parameter counts, but outcomes depend on the factorization and training procedure.
- INT7 can improve real ARM latency and preserve ImageNet classification, while detection still loses accuracy.
- LoRA reduces per-task adaptation cost, but keeps the full shared base model and its forward pass.
- Inheritune shortens the training of a small model by borrowing weights from a larger pre-trained one; that inherited compute is not free.
- MoE-Lens increases throughput in offline CPU-GPU batch workloads, with large multipliers concentrated in selected request/hardware conditions.
- LLM quantization quality depends strongly on bit width, quantization algorithm, scale, and task—not bit width alone.

The falsifiable opportunity is an efficiency-accounting benchmark that distinguishes *pretraining/training compute, fine-tuning state, persistent model storage, per-token FLOPs, measured latency/energy, and throughput under a stated workload*. Compare methods on shared models and tasks, report quality against each cost axis, and include the source-model/checkpoint cost for warm-start methods. Pre-register at least one task where the claimed gain should fail (e.g. detection for aggressive quantization; knowledge/reasoning at low bit width; low-memory interactive serving for batch-oriented MoE scheduling). This is a bounded synthesis from six random frame papers, not a prevalence estimate or a novelty claim.
