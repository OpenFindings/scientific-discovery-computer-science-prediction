# Full-text audit batch 73: model efficiency, 2015–2019

This closes the six-record `model_efficiency × 2015–2019` frozen sample cell. Three lexical-priority papers are newly audited; one previously unaudited uniform-random paper is audited; two random-arm papers are reconciled to earlier audits. The papers optimize different objectives and are not pooled into a single effect estimate.

## Newly audited lexical-priority papers

### Adaptive Training of Random Mapping for Data Quantization (`1606.08808v2`)

ATQ adapts the offset in cosine-based binary hashing and evaluates retrieval mean average precision on CIFAR-10 and MNIST (spelled “MINIST” in parts of the paper). It compares random-quantization and spectral-hashing baselines while varying code bits, data samples, and neighbors. On CIFAR-10, ATQ and CQ generally rank above the tested alternatives; on MNIST, Spectral Hashing is often strongest. The paper itself describes noticeable result fluctuations as the number of sampled points changes. Its evidence is therefore an unsupervised retrieval result on two image datasets and selected random subsets—not a general efficiency, energy, or downstream-classification result. No confidence intervals or repeated-run uncertainty estimates are reported in the inspected evaluation.

### A Survey of Model Compression and Acceleration for Deep Neural Networks (`1710.09282v9`)

This is a broad narrative survey of pruning/quantization, low-rank factorization, compact/transfer filters, and knowledge distillation; the arXiv record begins in 2017 and v9 was revised in 2020. It discusses accuracy, compression, and speedup measures and identifies hardware-aware methods as an important direction. It is useful historical context, not a systematic review with a reproducible database search/screening protocol, and it predates many current edge and foundation-model deployments. In particular, the survey’s model-size or operation-count summaries should not be read as universal predictions of wall-clock latency or energy on a specified device.

### Structured Multi-Hashing for Model Compression (`1911.11177v1`)

SMH maps model weights through structured multi-hash matrix products to reduce the number of trainable variables while retaining memory locality. The paper reports, among other results, 75% fewer variables with no CIFAR-10 ResNet-32 accuracy loss and a 10×-compressed ResNet-32 above 90% accuracy; it also reports EfficientNet-family cases where a larger starting model compressed to a smaller model’s parameter count can outperform the smaller baseline. Crucially, the paper says parameter-count/accuracy behavior tracks more closely in ResNets than in EfficientNet or MobileNet. The authors argue that structured locality avoids material inference-latency overhead, but the central reported comparisons are accuracy against variable/parameter budget; they are not a broad, device-by-device energy and end-to-end latency evaluation. Compression ratios are not interchangeable with speedups.

## Newly audited uniform-random paper

### Shallow-Deep Networks: Understanding and Mitigating Network Overthinking (`1810.07052v3`; ICML 2019)

The authors attach internal classifiers to VGG, ResNet, Wide-ResNet, and MobileNet, then use confidence thresholds for early exits on CIFAR-10, CIFAR-100, and Tiny ImageNet. Their practical exit policy selects the threshold on a small unlabeled holdout and measures inference cost in FLOPs. Table 3 shows substantial task/model variation: with joint SDN training, examples include 50%-budget accuracies of 93.2% vs a 93.1% VGG baseline on CIFAR-10, 72.5% vs 70.9% on CIFAR-100, and 56.2% vs 58.6% for ResNet on Tiny ImageNet. A separate label-aware “ideal” exit analysis is an upper bound, not a deployable policy. Added heads increase parameter/storage cost even where the per-sample FLOP cost of the heads is small. The study is limited to CNN image classification, uses FLOPs rather than a cross-device latency/energy matrix, and does not evaluate distribution shift. Its single backdoor mitigation case is not a general security guarantee.

## Previously audited uniform-random papers reconciled (not new reads)

- **Flexible Deep Neural Network Processing (`1801.07353v1`; batch 11):** on the paper’s ImageNet/AlexNet setup, the flexible ensemble trades average runtime from 11.67 ms to 6.51 ms for a very small top-1 accuracy decrease from 0.6043 to 0.6032. It uses a training-data threshold grid and a single weighted objective; its hardware/software and architecture coverage are narrow.
- **Tensorial Neural Networks: Generalization of Neural Networks and Application to Model Compression (`1805.10352v3`; batch 13):** the ResNet32/CIFAR-10 results at a nominal 10% parameter budget depend on the decomposition: TNN-mCP 91.28% vs NN-CP 88.50%; TNN-mTK 81.59% vs NN-TK 86.73%; TNN-mTT 87.89% vs NN-TT 87.08%, with the uncompressed model at 93.2%. Variable count is not a latency/energy measurement.

## Findings and next tests

The structured findings in `data/research_findings_batch73.jsonl` separate (a) nominal compression/operation budgets from physical target-device performance, (b) model/dataset-dependent rankings, and (c) the calibration and distribution assumptions of early exit. The important counterevidence is that hardware-aware evaluation is not new: SqueezeNext (2018) uses accelerator simulation to report speed and energy, and MultiTASC (2023) reports device-specific latency/SLO evaluation across mobile devices and a server. The next study is therefore a matched, reproducible comparison of these sampled method families at fixed quality and target-device budgets, not a claim that hardware-aware evaluation has never been done.

## Sources

- https://arxiv.org/abs/1606.08808v2
- https://arxiv.org/abs/1710.09282v9
- https://arxiv.org/abs/1911.11177v1
- https://arxiv.org/abs/1810.07052v3
- https://arxiv.org/abs/1801.07353v1
- https://arxiv.org/abs/1805.10352v3
- Counterevidence follow-ups are listed in `data/research_followups_batch73.jsonl`.

This closes one cell of a stratified sample from 198,690 arXiv-CS candidates. It is not a representative whole-corpus estimate, a hardware-independent ranking, or a global novelty determination.
