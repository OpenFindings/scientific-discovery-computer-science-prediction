# Full-text audit batch 72: program repair and verification, 2025–2026

This closes the six sampled records in `program_repair_verification × 2025–2026-through-10-11`: three newly audited lexical-priority papers and three exact-version random-arm papers reconciled to earlier full-text reviews. These papers measure different outcomes and are not pooled.

## Three new full-text audits

### Understanding the Effectiveness of LLMs in Automated Self-Admitted Technical Debt Repayment (`2501.09888v1`)

The study mines GitHub history and builds 58,722 Python and 97,347 Java SATD-repayment examples. Its ten-stage filtering pipeline uses an LLM relevance filter; the paper manually labels 100 candidate examples per language for validation and reports precision/recall of 0.830/0.867 for Python and 0.926/0.806 for Java for its selected filter. This supports scale, but does not imply error-free labels: remaining false positives and missed cases affect the gold data, and repository-history reconstruction does not establish that a later developer edit was caused by an SATD comment.

Whole-file BLEU-style scores can prefer an unchanged input over a useful patch, so the authors introduce diff-based BLEU/CrystalBLEU and LEMOD, which compares changed lines with the later developer patch. Best reported exact-match rates are 10.1% for Python and 8.1% for Java. However, line overlap with one later developer change is still not a semantic correctness oracle, and this study does not run functional tests on generated repairs. The paper also notes possible pretraining contamination, excludes some SATD cases through filtering, and limits repair to within-method context. Its metric contribution is useful for measuring patch overlap, not proof that a repair is behavior-preserving or correct.

### Benchmark Dataset Generation and Evaluation for Excel Formula Repair with LLMs (`2508.11715v1`)

FoRepBench contains 618 generated examples filtered from 1,095 executable candidates; its manually reviewed real-world seed contains only 59 forum examples. The paper reports broader function/error diversity in the generated set, but more localized edits and shallower semantic transformations than in the seed set. In the paired evaluation, GPT-4.1 execution-match is 0.80 on FoRepBench versus 0.41 on the seed; GPT-4o is 0.73 versus 0.35, Phi-3 0.58 versus 0.24, and Mistral 0.51 versus 0.19. This is direct within-paper evidence that synthetic scale and lexical diversity did not reproduce the difficulty of the small curated seed.

Two human annotators have Cohen’s κ=0.60; the LLM validator agrees with each at κ=0.42 in the results table. The conclusion instead says κ=0.25, an internal numerical discrepancy retained here rather than resolved by choosing one value. Human review also rejects some examples that execute but are contextually implausible. The study is scoped to English, single-sheet Excel contexts; it does not prove the synthetic set is useless, nor establish that all generated benchmarks are easier.

### A Survey on Large Language Model Impact on Software Evolvability and Maintainability (`2601.20879v1`)

This systematic review searches ACM Digital Library, IEEE Xplore, and Scopus for the years 2020–2024, screens 711 records, and synthesizes 87 primary studies. It finds mixed reported benefits and risks and notes that long-term/structural outcomes are less commonly measured than short-term tasks. Its date window is important: it cannot support a present-day claim that longitudinal work is absent, because several directly relevant 2026 studies appeared after its search period. The review is evidence of the literature through 2024 and a useful map of constructs, not a census of research available by October 2026.

## Uniform-random sampled records reconciled to earlier audits

- **Evaluating the Generalizability of LLMs in Automated Program Repair (`2503.09217v1`; batch 8):** semantics-preserving transformations to 438 single-function Defects4J bugs reduce mean correct/plausible fixes across 11 open models by 49.48%/42.90%; repair context helps selected setups, but 10/12 model/prompt setups remain below original-set performance. This is benchmark-shift evidence, not a real-world repair-rate estimate or an independent replication.
- **Ownership Refinement Types for Pointer Arithmetic and Nested Arrays (`2604.22361v1`; batch 27):** the paper proves soundness for its stated type system and evaluates a finite designed nested-array benchmark. The theorem and crafted suite do not establish coverage of arbitrary unsafe programs; the method requires additional annotations and runtime varies by workload/solver.
- **Agentic Proving for Program Verification (`2605.23772v1`; batch 27):** the headline end-to-end success is conditional on two prompt runs; after removing four benchmark-issue tasks the paper reports 98.1%, and it flags ground-truth issues in 80/161 tasks plus ambiguity between natural-language intent and formal specifications. Proof/compilation success is not by itself evidence that the specification captures user intent.

## Findings and next tests

Three bounded findings and falsifiable tests are in `data/research_findings_batch72.jsonl`. The strongest cross-paper correction is that the broad statement “long-term effects of AI-generated code have not been studied” is no longer tenable: the 2026 SLR is cutoff at 2024, and newer papers analyze two-year IDE telemetry, SATD lifecycles, and explicitly attributed AI-authored commits. The more defensible open question is whether AI assistance causes changes in semantically verified quality and maintenance burden under matched, longitudinal comparisons. Existing studies do not jointly answer that: the IDE study explicitly disclaims causal attribution and uses activity proxies; the SATD study measures admitted comments and has repository-age/detector limitations; the large GitHub study lacks a clean human-authored comparison and measures static-analysis-detectable code issues.

An additional design lead is difficulty-aware benchmark validation. FoRepBench’s synthetic set is substantially easier than its small real seed; the sampled SATD-repair and transformed-Defects4J work show separate limits of reference-patch metrics and distribution shift. This is not a novelty claim: PatchDiff and other benchmark-validity research already test plausible-but-incorrect patches. A useful next test must compare synthetic and real tasks under matched difficulty strata and use executable tests plus independent semantic review, with held-out repositories and confidence intervals.

## Sources

- https://arxiv.org/abs/2501.09888v1
- https://arxiv.org/html/2508.11715v1
- https://arxiv.org/abs/2601.20879v1
- https://arxiv.org/abs/2503.09217v1
- https://arxiv.org/abs/2604.22361v1
- https://arxiv.org/abs/2605.23772v1
- Targeted counterevidence and follow-ups are individually versioned in `data/research_followups_batch72.jsonl`.

This is one six-record cell in a stratified sample from a much larger arXiv-CS candidate pool. It is not a representative survey of the whole pool, an independent reproduction, or a global novelty determination.
