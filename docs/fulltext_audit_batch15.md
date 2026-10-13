# Full-text audit batch 15: security and privacy

Updated 2026-10-11. All four papers were selected from the predeclared uniform-random arm of the `security_privacy` topic, one per arXiv submission-period stratum. This is a four-paper audit slice, not a representative estimate of the field. The frame describes arXiv submission date, not necessarily first publication date.

## 1. Secure workflow decentralisation (2010)

[Kaskenpalo, “On Secure Workflow Decentralisation on the Internet”](https://arxiv.org/html/1006.1449v1), arXiv v1; published in EPTCS 27 (2010), pp. 2–16, DOI [10.4204/EPTCS.27.2](https://doi.org/10.4204/EPTCS.27.2).

**What it contributes:** A security-oriented survey and architecture proposal for decentralized workflows. It reviews distributed security building blocks and maps them onto workflow control-flow, data, and resource patterns. The article motivates combining email-like decentralized exchange with workflow semantics.

**What it does not establish:** This is not a measured security evaluation of a deployed workflow system. The text outlines formal/modeling work (including a planned CPN/YAWL direction) rather than reporting a finished implementation tested against attackers. Its security story depends on assumptions such as PKI and trusted key assignment. Treat it as an early design/survey contribution, not empirical evidence that decentralization makes workflows secure.

**Audit judgment:** Useful historical context; no empirical finding extracted.

## 2. On-average KL privacy (2016)

[Wang, Lei, and Fienberg, “On-Average KL-Privacy and its equivalence to Generalization for Max-Entropy Mechanisms”](https://arxiv.org/html/1605.02277v1), arXiv v1; published in *Privacy in Statistical Databases* (2016), pp. 121–134.

**Main result:** The paper defines an expected privacy-loss measure averaged over samples drawn from a specified data distribution and relates it to generalization for a class of Gibbs/posterior-sampling mechanisms. This is deliberately weaker and more distribution-dependent than worst-case differential privacy; it does not promise the same protection for every input or rare/outlier subgroup. The paper develops composition and information-theoretic connections.

**Empirical boundary:** The experiments are two small illustrative simulations (mean release and one-dimensional linear regression), used to estimate expected quantities. They are not privacy attacks on deployed systems, real-data audits, or evidence that the guarantee withstands distribution shift. The theorem is the central evidence; the simulations are illustrations.

**Audit judgment:** The useful distinction is average-case, distribution-conditional privacy versus worst-case DP—not that one notion universally replaces the other.

## 3. IoTGaze (2020)

[Gu et al., “IoTGaze: IoT Security Enforcement via Wireless Context Analysis”](https://arxiv.org/html/2006.15827v1), arXiv v1 (the record says to appear at IEEE INFOCOM 2020).

**Reported prototype evidence:** In a SmartThings testbed, the authors use five device types and 19 event types; train event identification on three weeks and evaluate on a subsequent week. They report 98.46% overall event-identification accuracy, with packet loss/interference among the identified failure causes. They then test 35 installed apps, for which generated IoT contexts matched the discovered wireless contexts in that setup. For three manually injected threat types, each with 100 anomaly instances per app, reported precision is 97.22%/98.55%/98.29% and recall is 94.82%/98.36%/95.20% (spoofing/overprivilege/misbehavior). The paper notes lower recall for spoofing and misbehavior when anomalous sequences resemble normal ones.

**Important denominator distinction:** Separately, the system analyzes 183 public SmartApps and discovers candidate cross-app interaction chains. Those are potential hidden-channel vulnerability paths generated from an app corpus, not 183 independently validated exploit successes. The precision/recall numbers above come from the injected-anomaly test, not that corpus scan.

**Scope limits:** This is a proof-of-concept in a specific SmartThings/ZigBee setup, not evidence of the same accuracy across protocols, device populations, homes, or naturally occurring attacks. The injected cases and small device set make external validation especially important.

**Audit judgment:** Substantive empirical result within a bounded testbed, with positive metrics and a clear replication target; not a field-wide security guarantee.

## 4. “The Cyber Immune System” (2025 arXiv submission)

[Tallam, “The Cyber Immune System: Harnessing Adversarial Forces for Security Resilience”](https://arxiv.org/html/2502.17698v1), arXiv v1.

**What it is:** A narrative analogy/position essay arguing that adversarial pressure can expose weaknesses and spur resilience, drawing a parallel with biological parasites. It offers policy-level recommendations but, in the audited text, no new security mechanism, dataset, or experiment. The DOGE website breach is invoked as a motivating case, not evaluated as a causal study.

**Source-integrity note:** The arXiv record says submitted 2025-02-24, while the paper body is dated “August 24, 2026.” The displayed reference list also has visible duplication/formatting gaps. These are reasons to verify version and bibliography before relying on the essay as a dated scholarly source; they do not, by themselves, establish misconduct or falsity.

**Audit judgment:** Relevant as a hypothesis/opinion piece, not empirical evidence that adversarial pressure improves security.

## Cross-paper synthesis and next test

These four records illustrate why “security paper” is not one evidence class: an architecture survey, a formal privacy definition/theorem with toy illustrations, a constrained IoT prototype evaluation, and a narrative essay answer different questions. The most actionable empirical opportunity in this slice is to test how well IoTGaze-like detection transfers beyond the original devices and injected scenarios, while validating corpus-generated interaction chains as actual exploitable vulnerabilities.

For privacy, a discriminating study would compare worst-case DP and distribution-specific average privacy under both the nominal distribution and predeclared rare-subgroup/shift conditions, reporting utility and attack/leakage outcomes by subgroup. For IoT, replicate with multiple homes, device vendors and protocols; inject realistic packet loss and unseen devices; then have independent assessors validate whether each automatically generated interaction chain is exploitable. Neither proposed study's result is known from this four-paper audit.
