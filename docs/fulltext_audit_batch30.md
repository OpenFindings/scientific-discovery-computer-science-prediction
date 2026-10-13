# Full-text audit batch 30: newer security evidence stops at different stages of the pipeline

Updated 2026-10-12. This batch completes the six previously unread uniform-random records in the `software_supply_chain` sample cell. Alongside batch 29's four records, all 12 keys for this broad label are now audited or explicitly represented. The six papers here span hardware attack/defense, route privacy, practitioner discussion, CI workflow history, and network anomaly detection; they are not a common effect-size family.

## 2015–2019

### 1. Hardware Trojan Attacks on Neural Networks (2018; sampled v1)

[Exact sampled PDF](https://arxiv.org/pdf/1806.05768v1), attack setup, experimental results, and conclusion.

The authors propose attacks that modify selected hidden-layer neurons in a CNN so a trigger input is classified as an attacker-chosen class. They evaluate MNIST and CIFAR-10 networks under targeted/untargeted and crafted/random-trigger variants. In the paper's headline MNIST case, about 0.03% of neurons in layer five are changed; the test set does not expose the trigger behavior. The attack's required modification fraction varies substantially by layer, target, and dataset; CIFAR-10 generally requires more changes than MNIST.

**Boundary:** this is a simulated/injected-model experiment, not a Trojan found in fabricated chips or a field attack. Test-data invisibility under the reported evaluation is not proof that production monitoring cannot detect it. The proposed combined adversarial-training/side-channel defense is future work, not a validated mitigation in this paper.

### 2. Opening the Doors to Dynamic Camouflaging: Harnessing the Power of Polymorphic Devices (2018; sampled v2)

[Exact sampled PDF](https://arxiv.org/pdf/1811.06012v2), threat model, attack experiments, PPA estimates, and conclusion.

This paper proposes using reconfigurable MESO spin devices to make circuit functionality change after fabrication/test and at runtime, aiming to impede IP reverse engineering at the foundry, test facility, and end-user stages. The paper reports simulation-based resilience against SAT and test-data-mining attacks and a case study on error-tolerant image processing. Its selected ISCAS-85 comparison estimates much lower area and power than the compared CMOS LUT-based dynamic obfuscation, but delay is about 96% higher on average. The article itself says performance is a cost and leaves system-level control circuitry and non-error-tolerant/mission-critical use to future work.

**Boundary:** these are device/circuit simulations and synthesis-level estimates, not fabricated full-chip results or an independent red-team evaluation. Security conclusions are threat-model and attack-family dependent; the performance tradeoff makes the method a poor fit for delay-critical designs.

## 2020–2024

### 3. Routing with Privacy for Drone Package Delivery Systems (2022; sampled v2)

[Exact sampled PDF](https://arxiv.org/pdf/2203.04406v2), privacy-risk model, heuristics, and case studies.

The authors define a route-conditioned probability that a passive observer can infer which vendor served a customer, then optimize privacy against average delivery wait time. Aggregating pickups, increasing drone capacity, or making decoy stops can lower modeled inference risk, but route geography changes the tradeoff: in some topologies both privacy and efficiency improve; in others privacy costs time. The four geographic case studies use Boston distances, six orders, assumed 20 m/s drone speed, one minute per stop, and compare heuristics against exhaustive Pareto fronts for six orders.

**Boundary:** the model assumes a passive observer knows only the broadcast route and drone model, fixed collected batches (not online arrivals or dynamic rerouting), one vendor per customer and unit payloads; it omits range, battery, and payload effects. Wait time is modeled from travel distance and omits pickup/drop-off service time. This is a useful formal planning result, not observed privacy protection or customer-welfare evidence from deployed operations.

### 4. S3C2 Summit 2023-06: Government Secure Supply Chain Summit (2023; sampled v1)

[Exact sampled HTML](https://arxiv.org/html/2308.06850v1), methods, topic sections, executive summary, and panel questions.

This paper summarizes a one-day discussion with 17 practitioners from 13 government agencies. Researchers took notes under Chatham House rules and wrote a thematic summary about SBOMs, dependency choice, provenance, attestations, LLMs, and build/deploy. The discussion reports that SBOM generation is moving faster than tools for consuming SBOMs and producing actionable incident response; participants also raise ambiguity in self-attestation and the difficulty of using provenance alone as a security signal.

**Boundary:** these are attributed themes from a small, selected practitioner panel—not a representative survey, measured SBOM adoption rate, or causal assessment of whether SBOMs reduce compromise. The paper itself leaves SBOM use cases and benefits as open questions.

## 2025–2026-through-2026-10-11

### 5. An Empirical Study of the Evolution of GitHub Actions Workflows (2026; sampled v3)

[Exact sampled HTML](https://arxiv.org/html/2602.14572v3), dataset, results on workflow changes/security-related edits, threats to validity, and conclusion.

This mixed-method study examines 267,955 workflow histories and 3,418,911 workflow files across 49,258 public GitHub repositories from 2019–2025. It reports that workflow files are modified about every 159 days on average; security-relevant changes include more precise commit-hash pinning and permission refinements, while workflow dependency automation and reusable Actions create a control-versus-reuse tradeoff. A before/after analysis finds no conclusive change in workflow-edit frequency around LLM coding tools.

**Boundary:** the repository cohort is restricted to active projects with at least 300 stars and 300 commits; 11.54% of histories with invalid workflow files are excluded, and only primary branches are analyzed. Workflow edits are not security incidents or proof that least-privilege changes prevented attacks. The LLM comparison is observational and explicitly cannot establish no effect—agent use is only partially observable and the period has confounders.

### 6. When Relationships Break: Interpreting Network Traffic Anomalies via Dependency Violations (2026; sampled v1)

[Exact sampled HTML](https://arxiv.org/html/2608.26831v1), method, two IDS datasets, scenario results, and threats to validity.

XION learns dependencies among numeric flow features using benign training data, then scores violations for both anomaly detection and post-alert analysis. On CIC-IDS-2018 and CIC-UNSW-NB15, its detection is broadly comparable to Isolation Forest, with lower inference time in the evaluated scenarios (up to 7× in the reported comparison). It identifies distinct patterns: large coordinated feature breaks for DDoS/DoS, more gradual changes for Slowloris, and localized signals for SSH brute force. The weaker SSH case is useful counterevidence to a simplistic “dependency breaks explain every attack” claim.

**Boundary:** both datasets are pre-collected CIC flow benchmarks; the paper discusses known traffic-capture, flow-construction, and label issues. It uses aggregated numeric features, not packet/protocol content; real network transfer, concept drift, encrypted traffic, and known-cause controlled testbeds remain future work. “Interpretable patterns” are aligned with known attack descriptions but are not yet a demonstrated improvement in analyst decisions or incident response.

## Cross-period synthesis and candidate opportunity

Across the full 12-record cell, evidence runs from formal security properties and simulated attacker models to repository histories, benchmark traffic, and practitioner themes. A recurring gap is between an intermediate security signal (a workflow permission edit, an SBOM/provenance artifact, a model's benchmark detection score) and the downstream outcome of interest (prevented compromise, faster remediation, lower customer harm). This is not evidence that these controls fail: the studies were designed to answer narrower component questions, and some offer strong in-scope evidence. It is a candidate opportunity for an outcome-linked evaluation.

**Falsifiable design:** prospectively evaluate a staged CI/security intervention across repositories, with preregistered comparison groups or a stepped-wedge rollout. Link workflow/SBOM/provenance changes to validated vulnerability exposure, time-to-remediation, exploit/incident outcomes, false-positive burden, and developer effort; independently adjudicate incidents and report adoption/compliance as mediators rather than substitute outcomes. The opportunity weakens if existing multi-organization studies already link these controls to reliable downstream outcomes with strong causal identification, or if the proposed intervention yields no measurable risk/response improvement under realistic adoption.

**Sampling boundary:** this closes one broad, 12-key topic cell within the fixed 214-key frame. It does not estimate prevalence across all 198,690 arXiv-CS candidates or across all security/supply-chain literature.
