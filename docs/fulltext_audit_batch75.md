# Full-text audit batch 75 — software supply chain, 2020–2024

## Scope

This closes the frozen six-version cell `software_supply_chain × 2020–2024`: three lexical-priority papers newly read here and three uniform-random records previously read in batches 7 and 30. The papers span malicious-package measurement, drone-delivery route privacy, a practitioner summit, LLM analysis of security incident reports, heuristic detection of risky npm dependency updates, and naming/reuse of pre-trained models. The cell's labels and outcomes are too different for a pooled rate.

New exact-version PDFs were downloaded and extracted (94 pages total). Six provenance/reconciliation rows are in `data/fulltext_review_ledger_batch75.jsonl`.

## New full-text reads

### An Empirical Study on Using Large Language Models to Analyze Software Supply Chain Security Failures (2308.04898v1)

This evaluates GPT-3.5 and Bard against a manual/CNCF characterization of 69 reported incidents or vulnerabilities. GPT's accuracy by label was 59% for compromise type, 88% for intent, 74% for nature, and 52% for impacts; Bard's was 28%, 88%, 69%, and 45%. Manual impact-label agreement was itself low (mean Cohen's κ=0.34). The open-ended mitigation suggestions received a mean 3.83/5, but the paper says performance depended on how much the source reports described the incident. Prompts were iteratively tuned on the newest 20% of articles; the same prompt was then used for Bard despite Bard's prompt-length limit. The authors explicitly conclude these models should assist, not replace, analysts. This is an early bounded evaluation, not current-model performance.

### Lessons from the Long Tail: Analysing Unsafe Dependency Updates across Software Ecosystems (2309.04197v1)

Despite its plural title, the study is a purposive sample of 1,500 npm libraries and 88,416 pull requests. Of 63,829 update-related PRs, six regex-detected code/manifest features flagged 12,465 “unsafe” updates across 1,027 libraries. At least one such update appeared in 81% of top-tier libraries, 80% of middle-tier, and 44% of bottom-tier libraries; 70%, 71%, and 79%, respectively, were merged. Crucially, the authors state the lightweight feature method does not confirm that a flagged update is malicious. Thus the result establishes broad prevalence of flagged coding patterns under that operational definition, not a malware or exploitable-vulnerability rate. The authors identify actual unsafe practice, exploitability, and developer motivations as follow-up questions.

### Naming Practices of Pre-Trained Models in Hugging Face (2310.01642v3)

The study combines a survey of 108 Hugging Face users with mining of 14,296 popular model packages and DARA, a classifier for mismatches between model architecture and metadata. Respondents describe model names as carrying semantic details useful for reuse, unlike conventional package names. DARA's 5-fold results are highly label-dependent: the body/table reports up to 99% model-type accuracy, but the abstract says 94%; architecture accuracy is 72%, and task top-1 accuracy is 72.3% in Table 14 while the narrative reports approximately 76.3%. Those are internal inconsistencies in the exact v3 PDF. Task top-1 F1 is 56.5%. The classifier evaluation uses an 80/20 shuffled split; the authors report class imbalance, missing/unloadable models, and Hugging-Face-specific data. This exact arXiv v3 was revised in August 2025 and published in EMSE 2025, although the frozen frame places the work by its 2023 first-submission date and the study data run through 2024. DARA detects metadata disagreement; it does not establish that a model is safe, performs as advertised, or has trustworthy provenance.

## Reconciled random arm

The three random-arm records were already audited and are reconciled without counting new reads: 2002.01139v2 reports MALOSS's suspicious-package pipeline and 339 new suspicious packages, 278 of which maintainers confirmed/removed, while warning that this is not unbiased ecosystem prevalence and the detector is evadable; 2203.04406v2 models route-conditioned customer/vendor privacy for drone package delivery in six-order Boston scenarios, not software artifact security; 2308.06850v1 summarizes a one-day panel of 17 government practitioners from 13 agencies on SBOMs and secure supply chains, not a representative or causal evaluation. Their distinct constructs are retained rather than mislabeled as equivalent “supply-chain outcomes.”

## Findings and falsifiable leads

### Finding 153 — “Security evidence” needs a typed outcome ladder

The cell mixes news-reported incidents, human-coded intent/impact, regex-flagged code changes, suspicious-package detections, maintainer-confirmed package removals, and model-metadata inconsistencies. Those are not interchangeable labels. In the LLM study, impact is both the weakest GPT dimension (52%) and the least consistent human-coded dimension (κ=0.34). In the npm update study, 12,465 feature-flagged PRs are explicitly not confirmed malicious; in the older random-arm MALOSS paper, analyst/maintainer confirmation is a distinct subsequent stage. A defensible research database should preserve these as different levels—signal, analyst assessment, confirmed malicious artifact, vulnerable/reachable code, and observed downstream impact—and report the transition/uncertainty between them. This is a bounded synthesis, not a claim that attack measurement or human-in-the-loop analysis is new.

### Finding 154 — AI-model packages require artifact-aware checks, but name/architecture checks are not security assurance

The sampled Hugging Face study shows that model artifacts expose reuse-relevant metadata and that one architecture-derived classifier performs strongly for broad model type but substantially less well for architecture/task. A 2025 developer-discussion study reports security concerns across system/software, tools/ecosystem, model, and data categories, while a 2026 research agenda says cross-ecosystem measurement and real-world exploitability remain unresolved. Together these motivate a typed, artifact-aware provenance/evaluation layer that checks names, config, weights, data lineage, and actual use. They do not prove current registries are unsafe or that DARA prevents attacks. The 2025 study's manually coded 753 posts are a thematic sample, not a prevalence estimate; the 2026 agenda is a proposed program, not a completed experiment.

## Next tests

1. Build a two-ecosystem incident corpus with separately adjudicated evidence levels (regex/heuristic signal, human-reviewed behavior, confirmed malicious artifact, reachability, and downstream impact). On a blinded sample, estimate precision/recall and reviewer agreement at each transition; measure whether LLM-generated labels preserve source citations and abstain when reports are underspecified. The lead weakens if signal labels reliably predict confirmed impact and reviewers agree across dimensions.
2. For model registries, evaluate a held-out-by-architecture and held-out-by-time benchmark. Compare name-only, config-only, weights/graph, signed provenance, and combined checks for metadata accuracy, model/task mismatch detection, actual artifact provenance, and downstream task performance. Include at least two registries and open-world unknown labels. The lead weakens if the architecture/name signal alone robustly predicts provenance and runtime behavior.

## Limitations

This is one fixed six-paper cell, only three of which were newly read. The random-arm records are heterogeneous but were preserved for sample integrity. The follow-up search is targeted rather than systematic; findings are leads, not prevalence estimates or global novelty claims. The PTM tool results are based on a particular registry/dataset and shuffled validation, and the LLM incident study predates current model generations.
