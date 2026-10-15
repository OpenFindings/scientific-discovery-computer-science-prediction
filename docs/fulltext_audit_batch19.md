# Full-text audit batch 19: the changing meaning of “AI-generated code”

Updated 2026-10-11. Four fixed-frame uniform-random papers were audited, one from each arXiv submission period, under `ai_generated_code`. This is deliberately a screen-audit as well as a technical audit: the old random items are deterministic code generators, not AI systems. That distinction is itself important—otherwise a lexical topic screen can manufacture a false historical “AI trend.”

## 1. Automated Code Generation for Lattice QCD (2014)

[Barthou et al., arXiv:1401.2039v1](https://arxiv.org/pdf/1401.2039), §§3–6.

QIRAL generates OpenMP C from a domain-specific language embedded in LaTeX for lattice-QCD algorithms. It makes algorithm composition easier and uses manually optimized/specialized libraries for hot matrix-vector kernels. The evaluation compares iterative methods across architectures and compares generated QIRAL code with tmLQCD for the same CGNR + Schur algorithm. QIRAL is competitive or faster on several tested architectures, and scales well to 60 Xeon Phi cores; however, on Nehalem-EX it is more than twice as slow as tmLQCD because that QIRAL build lacks SSE SIMD intrinsics. The authors explicitly note that the best method cannot be selected from per-iteration time alone: full convergence time and architecture matter.

**Boundary:** the result is a specialized, high-performance scientific compiler/toolchain with hand-tuned libraries, not an ML-generated-code experiment. Results cover one scientific domain and specific machines/algorithms. Multi-node communication generation and more SIMD/library tuning remain future work.

## 2. Modeling Variability in Template-based Code Generators (2016)

[Greifenberg et al., arXiv:1606.02903v1](https://arxiv.org/pdf/1606.02903), especially §5 and Table 1.

The paper organizes a family of model-to-code generators into reusable layers, with explicit template regions and refinements, then compares a conventional copy-paste variant against its composition approach in one industrial Java generator. For two generator variants, template lines of code fall from a combined 7,823 to 6,231 (about 80%); helper lines fall from 1,858 to 1,009 (about 54%), or about 63% if unused copied helper methods are excluded. The paper also observes that the number of DEFINE blocks is comparable, so the benefit does not uniformly appear in every complexity measure.

**Boundary:** this is code-generator engineering and reuse, not AI or LLM generation. It is one real-world generator and one additional variant; the principal outcome is artifact size/structure, not generated-program correctness, developer effort, defect rate, or long-term maintenance. It is evidence for a reusable organization technique under that case, not a generalized productivity estimate.

## 3. InverseCoder: Self-improving Instruction-Tuned Code LLMs (2024)

[Wu et al., arXiv:2407.05700v2](https://arxiv.org/html/2407.05700v2), §§3–6 and Appendices A/C.

Inverse-Instruct extracts clean code snippets from an existing GPT-4-generated instruction/code corpus, asks a code LLM to produce ten natural-language instructions per snippet, uses the same model’s YES/NO pseudo-probability to select one, then fine-tunes on those pairs plus the original corpus. This yields 90,363 self-generated pairs. With three base-model families, the paper reports pass@1 changes against its WizardCoder-GPT4 starting point on HumanEval+/MBPP+, MultiPL-E, and DS-1000. Gains are real but not uniform by model × benchmark: for example, DeepSeek-Coder 6.7B rises from 77.4 to 79.9 on HumanEval+ and 67.5 to 69.0 on MBPP+, while the CodeLlama-Python 7B DS-1000 average falls from 40.2 to 39.9; individual library/language cells also move down. Ablations find that adding multiple generated instructions per code response can hurt and repeated self-improvement rounds do not significantly improve performance.

**Counterweight:** the main controlled comparison to the starting model is useful, but the method inherits a GPT-4-generated source corpus and uses the model itself to select generated instructions, so this is not fully self-sourced training. The evaluation uses benchmark pass@1 and decontamination checks, not repository-level maintenance or secure correctness. Some comparisons to other published models use reported leaderboard/paper results rather than a common retraining and inference budget. Appendix self-consistency is also not the same as an independently verified semantic guarantee.

## 4. SWE-Refactor: Repository-Level LLM Refactoring (2026)

[Xu et al., arXiv:2602.03712v1](https://arxiv.org/html/2602.03712v1), §§3–6 and stated limitations.

SWE-Refactor mines 1,099 developer-written Java refactorings from 18 projects (922 atomic, 177 compound) and verifies instances using compilation/tests and AST-based refactoring detection. The success criterion requires both passing tests/compilation and performing the requested refactoring. On the reported 200-instance GPT-5.1-Codex subset, success is 151/200 overall: 138/167 atomic (82.6%) versus 13/33 compound (39.4%). DeepSeek-V3 has 457/1,099 successful cases overall in the benchmark table. Failures often perform only part of a compound transformation or a different edit. This is notably stricter than merely producing compilable code or passing behavioral tests.

**Boundary:** Java only; method-level refactorings; 1,099 examples remain limited for exhaustive coverage; automated mining/detection tools can miss or misclassify examples despite manual inspection of 200 sampled instances. The Codex 39.4% headline is on the 33 compound cases in a 200-item evaluation subset, not 39.4% of all 177 compound benchmark records. Results are benchmark- and model-snapshot-specific.

## Cross-period interpretation

The sampled topic label hides a major change in what “generated code” means. In 2014, a deterministic DSL compiler translates scientific notation into optimized OpenMP and relies on hand-tuned kernels; in 2016, generator composition reduces duplicated template/helper code; in 2024, an LLM creates synthetic natural-language training instructions for code; in 2026, LLMs perform behavior-preserving repository refactorings under tests plus AST checks. Their outcomes—runtime, source-line counts, benchmark pass@1, and exact transformation plus test success—cannot support a single continuous performance curve.

**Bounded discovery:** the fixed-frame random sample confirms that a topic label such as `ai_generated_code` can conflate pre-LLM program synthesis/code generation with modern generative AI. A historical comparison that does not manually adjudicate the mechanism risks attributing old deterministic compiler results to “AI.” Separately, the 2026 benchmark demonstrates that passing tests is not sufficient to establish task completion when the requested operation itself must occur.

**Falsifiable follow-up:** reclassify all `ai_generated_code` candidates with explicit mechanism labels (deterministic compiler/generator, symbolic synthesis, statistical ML, LLM code completion, LLM agent editing) and independently audit a random sample in each arXiv-era/topic cell. For performance claims, compare within mechanism-specific outcomes: generated artifact validity, exact requested transformation, semantic preservation, runtime/quality, human effort, and held-out-project transfer. The screen-drift concern is weakened if blinded reviewers find that old and new records consistently study the same mechanism; it is strengthened if old-period matches are overwhelmingly deterministic tools and recent matches LLM-based systems.

This four-paper slice is not a prevalence estimate, meta-analysis, or claim that a specific method is globally novel.
