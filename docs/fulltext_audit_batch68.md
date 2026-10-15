# Full-text audit batch 68: automatic code generation, 2015–2019

This batch closes the lexical-priority arm for `ai_generated_code × 2015–2019`. The frame’s topic contains distinct forms of code generation: source-to-source HPC migration, specialized mathematical program synthesis, and natural-language code generation. Results are not combined as one effect.

## Sampled full texts

### 1. OMP2MPI: Automatic MPI code generation from OpenMP programs (`1502.02921v2`)

OMP2MPI transforms selected OpenMP parallel-loop patterns into MPI master/worker code. A subset of PolyBench was run on 64 CPU cores of a Bull system. The paper reports that 64-core results exceed 20× speedup over sequential code in most tested cases and exceed 4× over the original OpenMP code; the plots also show scaling at 16, 32, and 64 processors. Correctness was checked on microbenchmarks. This is a 2015 arXiv/CoRR paper, not a peer-reviewed venue paper identified in this audit.

The result is bounded by the supported parallel-loop pattern and benchmark suite. The authors explicitly list unsupported shared-variable uses and additional OpenMP constructs (e.g., critical/atomic cases) as future work. “Correct by construction” should therefore be read as the transformation’s intended property for its supported patterns, not a proof covering arbitrary OpenMP programs.

### 2. Program Generation for Small-Scale Linear Algebra Applications (`1805.04775v1`, SLinGen)

SLinGen takes fixed-size linear algebra computations in a domain-specific language and generates optimized C, optionally with SIMD intrinsics. It evaluates four higher-level linear algebra computations and three applications (Kalman filter, Gaussian-process regression, L1-analysis solver) against libraries, compilers, and prior generated code. On an Intel Sandy Bridge i7-2600, single-threaded, warm-cache tests with the working set fitting in L1/L2, SLinGen reports substantial gains for several routines (for example, average 2× vs MKL and 4.2× vs icc for Cholesky; around 2.5× vs MKL for triangular inverse). The application-level results vary: Kalman filter gains are reported, GPR is similar to MKL, and the L1-analysis solver is evaluated for one iteration.

The paper explicitly calls SLinGen a research prototype restricted to fixed input/output sizes and full storage for structured matrices. It studies one input at a time on one CPU generation; the authors list variable-size support, task parallelism, and batched input as future work. Thus the generated kernels demonstrate the value of specialization for the tested regime, not universal superiority over optimized libraries.

### 3. TreeGen: A Tree-Based Transformer Architecture for Code Generation (`1911.09983v2`)

TreeGen combines Transformer attention with AST/grammar structure. On HearthStone (665 Python card programs), it reports a 4.5 percentage-point gain over the preceding best result using structural preprocessing; it also reports 89.1% on ATIS and 89.6% on GEO, the best among the compared neural models. On these semantic-parsing tasks it is slightly below the non-neural WKZ14 CCG-parser system. HearthStone measures include exact token sequence, BLEU, and a manually assessed variable-renaming-tolerant Acc+; the paper states exactness/Acc+ matter more than BLEU because generated program correctness is important. However, the reported experiments do not execute generated Python against behavioral tests.

**Boundary:** these results establish benchmark-specific gains in structured generation and semantic parsing, not functional correctness on arbitrary tasks, runtime quality, or broad code-writing capability.

## Targeted full-text metric counterevidence

### CodeBLEU: a Method for Automatic Evaluation of Code Synthesis (`2009.10297v2`)

The full primary PDF argues that token BLEU can reward code with logical errors and exact match can penalize semantically equivalent programs. CodeBLEU adds weighted tokens, AST-subtree matching, and data-flow matching. Across text-to-code, Java-to-C# translation, and code-refinement tasks, the reported Pearson correlations with human ratings are 0.977, 0.970, and 0.979; exact accuracy is more correlated than CodeBLEU for the code-refinement task (0.999 vs 0.979). This is useful counterevidence to treating any single score as universally best: metric ranking varies by task. The human-rating study used a random subset of 50 samples per task rated by 10 judges; CodeBLEU remains a similarity metric, not an execution test or proof of functional equivalence.

## Synthesis and falsifiable follow-up

These papers show three different standards for “generated code works”: transformation-level/microbenchmark correctness, measured speed on a narrow specialized numerical domain, and reference similarity for language-generated code. A bounded research question is whether code-generation rankings persist when systems are evaluated on *both* their native metric and held-out behavioral tests under matched budgets. For each task, report compile/pass rate, unit-test or differential-test correctness, numerical tolerances where relevant, runtime/energy, portability across compilers/CPUs, search/training cost, and human preference. The claim weakens if native metrics reliably predict behavioral correctness and deployment performance across task families and held-out platforms.

This is an evidence-bounded synthesis, not a claim that any method fails in its intended regime or that the proposed comparison is novel across the whole field.

## Primary sources

- https://arxiv.org/abs/1502.02921
- https://arxiv.org/abs/1805.04775
- https://arxiv.org/abs/1911.09983
- https://ojs.aaai.org/index.php/AAAI/article/view/6430
- https://arxiv.org/pdf/2009.10297
