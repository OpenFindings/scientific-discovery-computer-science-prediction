# Citation follow-up: smart-home anomaly detection and cross-app chains

Updated 2026-10-11. These are citation/topic follow-ups to batch 15, not additional members of its fixed random sample and not direct replications of IoTGaze.

## 1. HomeGuardian (2022): similar task, different sensors and assumptions

[Dai et al., “HomeGuardian: Detecting Anomaly Events in Smart Home Systems”](https://onlinelibrary.wiley.com/doi/10.1155/2022/8022033), *Wireless Communications and Mobile Computing* (2022).

HomeGuardian combines predicted event timing/state with environmental context from related devices, then classifies events from Home Assistant logs. It uses a mixture of real and virtual devices, with virtual activity based partly on CASAS HH114. The authors create abnormal examples by forging sensor events through a ZigBee gateway/MITM scenario, then report high aggregate F1.

**The table changes the headline:** the per-device table has temporal-context F1 values from 0.33 (LS002) to 0.91 (T102), with several device types notably lower than the abstract's “above 0.90 for all device types” summary. The reported high number is not an across-the-board result for every feature configuration: the table separates context-only and classifier variants, and its extracted HTML header/column layout is malformed. Any reuse of its headline should first resolve the original PDF/table columns. Evaluation uses a chronological 80/20 split of one testbed log and simulated injections; it is not a held-out-home or naturally occurring attack study.

One useful negative/qualifying observation is in the method itself: event intervals varied randomly in their collected data and could spike under disconnection or downtime, so the authors state raw interval length was inappropriate as a standalone detection criterion. This is a concrete reason to stress-test timing features under missingness and operational disruption.

**Audit judgment:** Relevant independent design/evaluation, but not a direct IoTGaze replication: it reads platform logs and predicts contexts rather than inferring event sequences from encrypted wireless traces. High aggregate claims need careful table-level interpretation and the testbed/injected-attack boundary.

## 2. PrivacyGuard (PoPETs 2025): broader cross-app privacy-chain analysis

[Wang, Luo, and Li, “PrivacyGuard: Exploring Hidden Cross-App Privacy Leakage Threats In IoT Apps”](https://petsymposium.org/popets/2025/popets-2025-0040.php), PoPETs 2025, pp. 776–791, DOI [10.56553/popets-2025-0040](https://doi.org/10.56553/popets-2025-0040).

PrivacyGuard models cross-app trigger-condition-action chains and estimates privacy-leakage risk. Its abstract reports analyses of 2,101 SmartApps, 2,788 IFTTT rules, and 2,086 OpenHAB rules; it reports that 7.67% of constructed two-app chains could leak at least one privacy category, with over 80% of identified leaks concerning localization/tracking or activity profiling. The official proceedings page marks its artifact “Available, Functional, Reproduced.” This is meaningful artifact-evaluation evidence, but not by itself an independent replication of the paper's scientific conclusions.

This is closer to IoTGaze's cross-app-chain motivation than HomeGuardian, but the evaluated outcome differs: PrivacyGuard analyzes modeled privacy leakage, while IoTGaze mines physical-channel interaction chains and separately evaluates injected anomaly detection. The percentages and chain counts should not be compared directly.

**Audit judgment:** A more recent, broader-dataset line of evidence shows that cross-app-chain risks remain an active, testable topic. It does not establish that IoTGaze's individual 183-app candidate chains are exploitable, nor that the two systems validate the same threat model.

## Cross-study synthesis: what is now more specific

Across IoTGaze, HomeGuardian, and PrivacyGuard, “smart-home anomaly/security detection” divides into at least three tasks: infer events from encrypted radio metadata, classify abnormal platform-log events using temporal/environmental context, and statically/model-check cross-app chains for privacy risk. Their headline metrics are not commensurable. The sharpest shared research question is therefore not a leaderboard comparison, but whether each representation preserves value under its own realistic shift: packet loss/unseen devices for wireless inference; outages, household changes and naturally arising attacks for log-based anomaly detection; and expert-validated false-positive/false-negative rates for generated app-chain risks.

**Falsifiable next study:** Reimplement or obtain the three pipelines and evaluate them on a common set of independently annotated smart-home scenarios, while retaining each method's native input. Split by home/site and device/vendor, inject naturalistic and adversarial events, and have blinded experts adjudicate alerts and candidate chains. Report per-threat precision/recall, false alarms per home-day, latency, untestable cases, and resource cost. A shared testbed would permit a meaningful comparison of coverage and operating burden, not force unlike scores into one ranking.
