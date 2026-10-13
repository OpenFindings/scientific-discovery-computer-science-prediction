# Full-text audit batch 34: privacy claims, threat models, and evidence that actually tests them

Updated 2026-10-12. This batch closes the seven previously unread uniform-random `security_privacy` frame keys across 2010–2026. Five were readable as full text, one is officially withdrawn, and one remained abstract-only after direct arXiv PDF/HTML retrieval failed. The withdrawn and unavailable records are dispositions, not completed full-text audits. I then checked two independent federated-learning attack papers to look for counterevidence to the sampled system papers' privacy implications. This is a fixed-frame slice, not a systematic review or prevalence estimate.

## The seven sampled records

### 1. Selection of Model in Developing Information Security Criteria for Smart Grid Security System (arXiv:1109.2697v1; 2011)

[arXiv record](https://arxiv.org/abs/1109.2697); [full text hosted with the proceedings paper](https://www.researchgate.net/publication/51937328_Selection_of_Model_in_Developing_Information_Security_Criteria_on_Smart_Grid_Security_System); [DOI](https://doi.org/10.1109/ISPAW.2011.12).

This is requirements elicitation and model selection, not a tested security control. The authors compare development/analysis models, select Quality Function Deployment (QFD), and use focused-group discussion to identify 16 requirements, including confidentiality, integrity, availability, privacy, key management, network issues, and constrained devices. The paper does not report an attack experiment, deployed smart-grid system, validated measurement of consumer trust, or quantitative ranking of the criteria. Its conclusion explicitly frames the output as conceptual mapping rather than fully documented use cases. Treat it as an early requirements paper, not evidence that the listed criteria improve security.

### 2. General Privacy-Preserving Verifiable Incentive Mechanism for Crowdsourcing Markets (arXiv:1311.5417v3; 2014)

[Official arXiv record](https://arxiv.org/abs/1311.5417v3).

The exact sampled manuscript is officially marked withdrawn. The arXiv record says the author withdrew it because of a crucial sign error in Equation 1 and Figure 1. Its old abstract's claimed parity with the non-private mechanism must not be used as a valid result. This is important corpus hygiene: title/abstract retrieval can make a withdrawn result look like affirmative evidence.

### 3. A privacy-preserving system for data ownership using blockchain and distributed databases (arXiv:1810.11655v1; 2018)

At the time of batch 34, the PDF/experimental HTML fetch had failed, so that batch dispositioned it as abstract-only. A later retry retrieved the exact v1 PDF; the full-text audit and correction to the ledger are in [batch 70](fulltext_audit_batch70.md#uniform-random-records-previously-reviewed). The paper describes a prototype stack and student/medical use cases, but does not report a quantified privacy attack, formal privacy proof, performance/scalability benchmark, or field evaluation. It is therefore an audited architecture/prototype proposal, not measured evidence of privacy protection at scale.

### 4. Demystifying Swarm Learning: A New Paradigm of Blockchain-based Decentralized Federated Learning (arXiv:2201.05286v2; 2022)

[Exact full text](https://arxiv.org/html/2201.05286v2).

The authors evaluate decentralized model training on three public tasks and compare accuracy, resource cost, fairness, and behavior under label pollution. Raw training data stay at the nodes, but model parameters/updates are exchanged; the paper does not provide a formal differential-privacy guarantee or an update-leakage attack evaluation. Thus “data stays local” is a data-location property, not by itself a quantified privacy guarantee.

There is useful positive evidence and a concrete reversal. With half of one node's labels deliberately corrupted, Swarm Learning is close to centralized learning on two tasks, but on the IMDB task it falls from centralized accuracy 0.8646 to 0.7955. The authors' broader “most scenarios” summary needs that task dependence attached. The experiments use three/four learning nodes and one blockchain service node; the authors identify limits to node-count generalization and note their proprietary blockchain implementation prevents independent inspection of internal message handling. These results support a bounded robustness/overhead study, not a blanket privacy or poisoning-resistance claim.

### 5. Tangent differential privacy (arXiv:2406.04535v1; submitted 2024; published in JML in 2025)

[Exact arXiv full text](https://arxiv.org/html/2406.04535v1); [published author copy](https://web.stanford.edu/~lexing/tdp.pdf).

This is a theoretical privacy definition tied to local/tangent changes around a particular data distribution, with bounds derived for specified risk-minimization/entropic-regularization conditions. It is not an empirical attack-defense comparison. Its distribution-specific assumptions and sensitivity notion are not interchangeable with standard record-level global ε-DP, nor with the edge-level LEDP guarantee in the next paper. Comparing the symbols “epsilon” across those notions without aligning adjacency, neighboring inputs, mechanism, and threat model would be invalid.

### 6. Bomfather: An eBPF-based Kernel-level Monitoring Framework for Accurate Identification of Unknown, Unused, and Dynamically Loaded Dependencies in Modern Software Supply Chains (arXiv:2503.02097v1; 2025)

[Exact full text](https://arxiv.org/html/2503.02097v1).

This is a security/supply-chain retrieval false positive for a privacy-specific question. It traces file access during a Go 1.21.0 compiler build in a container and reports 185,184 file-access events, 10,032 source files, 26 shared libraries, and 979 assembly files, using eBPF and hashes/Merkle trees to record provenance. That one build demonstrates a monitoring workflow; it does not establish vulnerability prevention, semantic dependency correctness across build systems, or a privacy guarantee. It should remain in the security umbrella inventory but not in a privacy-effect synthesis.

### 7. Practical and Accurate Local Edge Differentially Private Graph Algorithms (arXiv:2506.20828v3; 2025)

[Exact full text](https://arxiv.org/html/2506.20828v3); [artifact DOI](https://doi.org/10.5281/zenodo.15741879).

This paper has an explicit formal target: local edge differential privacy for graph edges, and algorithms for k-core decomposition and triangle counting. The authors report improved approximation factors on selected real-world graphs and show utility changing with ε. That is materially different from merely keeping raw data local in Swarm Learning. The evaluation's “distributed” framework is a simulation on one machine, not a multi-machine deployment; its strongest gains also vary by graph, with the authors noting less improvement on many low-core graphs. It is promising algorithmic evidence under a defined edge-adjacency model, not an end-to-end distributed privacy-system validation.

## Independent counterevidence: updates can leak even when raw examples stay local

### Gradient Disaggregation (ICML 2021)

[PMLR paper record](https://proceedings.mlr.press/v139/lam21b.html).

The authors show that a central server can sometimes separate user updates from repeated sums of updates by reconstructing participation patterns using device analytics. They report settings with up to thousands of participants and improved downstream inference on the disaggregated updates. The paper is a direct counterexample to treating aggregation or local raw-data storage alone as proof that individual information cannot be inferred. Its threat assumptions and attack results should still be matched to any target deployment; it is not evidence that every federated system is vulnerable in the same way.

### Active membership inference under local differential privacy (ICML 2023)

[Full PMLR paper](https://proceedings.mlr.press/v206/nguyen23e/nguyen23e.pdf).

This is a stronger stress test: the server is actively dishonest and can modify the model parameters sent to a client. Across CelebA, ImageNet, and CIFAR-10, the authors report attack success at least 0.77 for ε ≥ 5, approaching 0.99 for ε ≥ 9 under their studied BitRand mechanism; at lower privacy budgets, attack rates fall but task accuracy can also be severely damaged. Under a different LDP mechanism (OME), they report roughly 90% attack success on CelebA and CIFAR-10. These are adversarial benchmark results under the paper's stated setup, not a universal refutation of LDP: the attack assumes a malicious server, targets membership, and results depend on mechanism, task, and utility. The key lesson is that naming a formal privacy mechanism is not a substitute for testing the actual adversary and leakage objective.

## What we can and cannot say now

The concrete finding is not “privacy research has failed” or “nobody measures privacy.” It is that this sampled security/privacy label combines at least five different claims: requirements coverage, data ownership/access governance, raw-data locality, formal DP under distinct adjacency notions, and supply-chain provenance. These have different adversaries and outcomes, so a single “privacy-preserving” tag or pooled score is misleading. The independent FL attacks make one especially useful gap testable: for decentralized-learning systems that exchange model updates, pair the stated data-governance mechanism with an explicit server threat model and membership/reconstruction attacks, while reporting task utility and resource cost.

This is a candidate research direction, not a novelty claim. The sample contains only five readable full texts, one withdrawn record, and one unavailable full text; it cannot establish how common these omissions are across the wider corpus. The independent attacks concern federated learning and do not directly test Swarm Learning's implementation.

**Falsifiable follow-up:** On matched decentralized-learning tasks, compare (a) raw-data-local training without formal DP, (b) the exact DP mechanism with its adjacency and accountant, and (c) secure aggregation under both honest-but-curious and actively malicious servers. Measure membership-inference and reconstruction success, task accuracy, communication, and compute over multiple seeds. Pre-register attacks, participation/analytics side channels, and utility floor. The proposed gap weakens if existing work already reports this matched matrix with independent replications and the attack outcomes do not distinguish the protection classes.

## Sampling update

All seven previously unread random keys for `security_privacy` are now dispositioned or reviewed. The batch-34 snapshot had one abstract-only item, but a later retry retrieved and audited its v1 PDF (see batch 70); five other records were full-text audited and one was officially withdrawn. The withdrawn record is not counted as a full-text audit. Citation follow-ups are supplemental and do not change the random sample denominator.
