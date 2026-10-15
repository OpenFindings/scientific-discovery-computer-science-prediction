# Full-text audit batch 18: what “software testing works” means across eras

Updated 2026-10-11. Four papers were audited from the saved fixed-frame, uniform-random `software_testing` arm: one each from 2010–2014, 2015–2019, 2020–2024, and 2025–2026. The older arXiv HTML endpoints initially failed, but readable author/institution or proceedings PDFs were found; all four are full-text audits. This is a four-paper stratified slice, not an estimate of the field or a systematic review.

## 1. Input-output Conformance Testing for Channel-based Service Connectors (2011)

[Kokash et al., arXiv:1108.1862v1](https://arxiv.org/abs/1108.1862); readable [CWI institutional PDF](https://ir.cwi.nl/pub/18673/18673A.pdf), published in EPTCS 60 (2011), pp. 19–35.

The approach maps Reo coordination-connector models into process algebra (mCRL2), exposes input/output events, and reuses LTS/state-space generation and JTorX/ioco testing. The paper gives worked specification-versus-incorrect-implementation examples, including connectors whose observable output behavior diverges. It argues that the translation makes existing model-based testing tools applicable without requiring a separate hand-authored test model.

**Boundary:** the reported demonstrations are model-level examples. The authors say conversion of BPEL through Reo and mCRL2 requires every translation to preserve semantics, which may not be feasible; a more natural adapter to execute generated tests against the distributed Java implementation was still ongoing. The paper proposes compositional scaling as an expectation and timed/symbolic ioco as future work; it does not provide a real deployment study or measured large-model scaling result.

**Audit judgment:** a formal test-generation construction with illustrative fault detection, not evidence of operational defect yield or practical scale.

## 2. Semantics-based Automated Web Testing (2015)

[Guo, Ouyang & Siy, arXiv:1508.03905v1](https://arxiv.org/abs/1508.03905); full paper in [EPTCS 188](https://cgi.cse.unsw.edu.au/~eptcs/paper.cgi?WWV2015.7.pdf=), pp. 59–74.

TAO combines context-free-grammar test generation, denotational-semantics test oracles, Selenium/JUnit execution, and grammar-directed delta debugging (GDD). In a preliminary study over five buggy Java arithmetic programs, 1,000 generated expressions exposed failure patterns; mean failing-input length reduction was 81% (per-program values 79–87%). In the parking-calculator case study, the authors generated 500 JUnit web scripts and report an 11.24% average failure ratio. A second set of 200 executable Selenium scripts contained 28 failing scripts; GDD reduced failing scripts by an average of 22%, with time-boundary/fee-cap errors among the reported faults.

**Counterweight:** those metrics do not establish broad web-app effectiveness. The production-facing evaluation is one parking calculator, the scripts derive from one manually modeled grammar/semantics, the 500-script failure ratio is not an independently confirmed real-world defect rate, and the 22% reduction is modest relative to the 81% arithmetic-input result. There is no broad comparison against alternative generators or oracle strategies in the reported evaluation.

**Audit judgment:** concrete evidence that grammar-aware oracles can expose and shrink failures in this one modeled application; transfer to other sites and models remains untested.

## 3. Disentangling Flaws in Linux DCTCP (2022)

[Misund & Briscoe, arXiv:2211.07581v1](https://arxiv.org/html/2211.07581v1), especially §§2–6 and the experimental appendices.

This report uses controlled Linux TCP experiments to disentangle interacting implementation and algorithm issues. A PRR implementation discrepancy interacting with TCP Segmentation Offload can discard send allowance, briefly stall transmission, then create bursts and under-utilization. Aligning the code with RFC 6937 removes that particular symptom in the illustrated data-center and wide-area configurations. Critically, the repair uncovers a distinct latecomer-fairness issue; removing an alpha-to-zero toggle can improve a selected steady-state utilization result while trapping flows in poor competition equilibria and weakening the scalable-congestion response. AQM marking based on queue sojourn time can also favor large bursts; the report tests alternative marking approaches.

**Counterweight:** the authors explicitly say it is unclear how much the PRR issue affects prior studies and production, and call for comparisons using realistic traffic. Results depend on Linux implementation details, TSO, chosen capacity/RTT/AQM, and two-flow competition; they are not a universal DCTCP performance estimate. “Patch fixes the bug” must not be summarized as “patch fixes DCTCP fairness.”

**Audit judgment:** a strong example of sequential causal debugging: isolate and repair one defect, then re-run the full outcome suite because the repair can reveal masked problems.

## 4. Can LLMs Recover Program Semantics? (2025)

[Feng & Saha, arXiv:2511.19130v1](https://arxiv.org/html/2511.19130v1), §§3–6 and Tables 1–8.

The study uses 170 C programs from three sources, four obfuscation transformations (680 transformed variants), three LLMs, and baseline versus KLEE-artifact fine-tuning conditions. It reports compilation, a normalized “semantic score,” and code-quality metrics. The body qualifies the abstract’s broad claim that KLEE artifacts “consistently” improve outcomes: in the base-model compilation table, GPT’s arithmetic success is 75.8% with KLEE artifacts versus 93.9% without, and Codestral is 72.7% versus 93.9%; other model/transformation cells move in the opposite direction. The base semantic table also reports arithmetic scores of 51.17 versus 54.59 for Codestral (with/without KLEE), while GPT is 54.80 versus 47.13. The effects are model- and transformation-dependent, not uniformly positive.

**Construct-validity and selection caveats:** the paper’s semantic score compares KLEE test/path counts between the original and output, which is a proxy and not a proof of behavioral equivalence. The methods exclude some path-explosion cases and programs exceeding context limits, so the benchmark favors cases tractable to the chosen pipeline. Readability is separately measured and can be high even when semantic preservation is weak. Thus compile success, test-count similarity, readability, and behavioral equivalence must not be collapsed into one “deobfuscation success” number.

**Audit judgment:** useful controlled benchmark evidence for heterogeneous model × transformation effects, but its abstract-level universal wording is stronger than the tables support. Strict equivalence and out-of-project generalization remain open.

## Cross-paper finding and next discriminating test

These four papers are not a single technological lineage: formal conformance testing, grammar/oracle-based web testing, network-stack debugging, and LLM deobfuscation use different targets. The shared, actionable issue is outcome definition. A passing model relation, a generated failing test, a fixed single-flow symptom, compilation, KLEE path-count similarity, and true behavioral equivalence answer different questions. The newer papers especially show why “tool assisted” cannot stand in for “better”: DCTCP’s first fix exposed a fairness problem, and KLEE assistance moves some LLM/model/transformation cells down as well as up.

**Falsifiable follow-up:** preregister a common evaluation matrix for automated testing/repair tools that reports, separately: (1) artifact validity/compilation, (2) oracle agreement or formal conformance, (3) independently confirmed unique faults, (4) behavioral equivalence on exhaustive or held-out tests where feasible, (5) severity-weighted outcomes, (6) time and compute cost, and (7) transfer to unseen projects/configurations. Cross tool assistance on/off with multiple models, project families, transformation types, and realistic deployment conditions. The “assistance generally helps” hypothesis is weakened if gains disappear or reverse on held-out projects, strict equivalence, or severity-weighted defect outcomes despite better proxy scores.

This is a bounded measurement-design finding from four sampled full texts, not a field-wide trend, pooled effect, or novelty claim.
