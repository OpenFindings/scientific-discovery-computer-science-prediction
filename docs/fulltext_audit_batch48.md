# Full-text audit batch 48: uncertainty is not yet a calibrated code-review risk score

Updated 2026-10-12. This batch closes the three remaining lexical-priority records in `ai_generated_code × 2020–2024`: one study of uncertainty and generated-code failures, one broad code-LLM instruction-tuning benchmark, and one study of code-change tasks. These papers cover related reliability questions but do not use a common task or outcome, so no metrics are pooled.

## Sampled papers

### 1. Look Before You Leap: An Exploratory Study of Uncertainty Analysis for Large Language Models (arXiv:2307.10236v4; first arXiv submission 2023; journal publication 2025)

[arXiv HTML full text](https://arxiv.org/html/2307.10236v4); locally retrieved PDF: `data/fulltexts/arxiv/2307.10236v4.pdf` (18 pages).

The study compares single-sample, perturbation, and multiple-sample uncertainty estimates. For code, it evaluates HumanEval (164 problems) and MBPP (1,000 problems; a smaller subset is used for some closed-model runs), and treats “completely correct” versus “not completely correct” as a binary outcome. Sample-based estimates generally rank errors better than single-inference estimates, but the AUC varies by model and dataset: for example, a method that is strong on HumanEval can fall near chance on MBPP. The authors explicitly find that partial errors are harder to detect: 40.4% of GPT-3.5's MBPP errors pass at least one test, compared with 27.3% for GPT-4o and 32.4% for GPT-4o mini. Distance choice also matters; code-specific CodeBLEU often works better than embedding cosine distance, but CodeBLEU can overreact to semantically harmless identifier changes. This measures ranking/discrimination (AUC), not probability calibration, safe thresholds, security severity, or the cost of routing uncertain code to a reviewer. The record was first submitted to arXiv in July 2023; the checked v4 is dated 2025-01-05 and the DOI record places the IEEE Transactions on Software Engineering article in 2025 (51(2):413–429). The sampling cell follows initial arXiv year, not later journal year.

### 2. Astraios: Parameter-Efficient Instruction Tuning Code Large Language Models (arXiv:2401.00788v1; 2024)

[arXiv HTML full text](https://arxiv.org/html/2401.00788v1); locally retrieved PDF: `data/fulltexts/arxiv/2401.00788v1.pdf` (25 pages).

Astraios releases 28 OctoCoder models spanning four scales (1B, 3B, 7B, 16B) and seven tuning choices (six PEFT variants plus full fine-tuning), evaluated across five tasks/eight datasets. Full fine-tuning generally performs best; LoRA often offers the strongest cost/performance trade-off, while PEFT rankings depend on model scale. Code generation/repair is assessed with HumanEvalPack Pass@1, robustness with ReCode perturbations, and security with the Asleep-at-the-Keyboard benchmark. The authors report reduced robustness and security for larger models in their tested settings; the security analysis narrows to 40 automatically testable scenarios from a larger benchmark. The work therefore supplies important counterevidence to “larger is always safer/more robust,” but does not test whether uncertainty scores identify those vulnerabilities or predict which failures matter most.

### 3. Exploring the Capabilities of LLMs for Code Change Related Tasks (arXiv:2407.02824v1; 2024)

[arXiv HTML full text](https://arxiv.org/html/2407.02824v1); locally retrieved PDF: `data/fulltexts/arxiv/2407.02824v1.pdf` (33 pages).

The authors evaluate code-review generation, commit-message generation, and just-in-time comment updates. The data include review/diff pairs, millions of commit/message examples, and 98,622 comment updates; reported outcomes are BLEU/B-Norm/GLEU and exact comment accuracy, with a human evaluation for commit messages. In-context examples usually improve results, but gains are non-monotonic: more examples can force truncation and lower performance. LoRA generally beats prefix tuning, and code-change-specialized small model CCT5 can outperform untuned or prompted LLMs; LLM-PEFT performance is comparable to CCT5 on several comparisons. The paper's code-change outcomes are primarily text-overlap or exact-comment metrics, not whether a review catches a real defect, whether a fix passes tests, or whether a generated change introduces a vulnerability. Thus its “best model” results are bounded to the chosen tasks and metrics.

## Synthesis and bounded research lead

The positive evidence is real but narrower than a general “model confidence tells us whether code is safe” claim. Uncertainty scores can discriminate fully correct from not-fully-correct generated programs better than chance in many tested settings, especially with multiple samples; meanwhile partial test-passing errors remain difficult, performance changes by model/dataset/distance, and code-change quality is usually judged with text references. Astraios adds direct robustness/security outcomes but does not connect them to uncertainty. This leaves an actionable, testable question: does an uncertainty score help allocate human review across functional, code-change, and security outcomes once error severity and task distribution are held out?

## Bounded, falsifiable next experiment

For a preregistered set of code-generation, repair, and code-change tasks, save model outputs and uncertainty estimates before running execution-based tests, mutation tests, vulnerability tests, and blinded maintainer review. Split by repository/project and time, and report separately by model family/scale, perturbation type, error severity, and comment-only versus executable-code changes. Evaluate discrimination (AUC), calibration (Brier score/reliability curves), selective risk at fixed review budgets, missed critical defects, and reviewer minutes per confirmed issue; compare against pass@1, token confidence, and static-analysis baselines. The lead is weakened if uncertainty does not improve calibration or critical-defect yield over these controls at the same review budget, and strengthened if it reliably improves held-out triage across project and task types. This study has not been run here, and its novelty is not established.
