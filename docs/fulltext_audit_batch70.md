# Full-text audit batch 70: security/privacy, 2015–2019

This batch closes all six sampled records in the `security_privacy × 2015–2019` frame cell: three uniform-random papers previously reviewed in batches 10, 15, and 34, plus three lexical-priority papers audited here. The previously unavailable blockchain/SSI paper was retried and its exact v1 PDF is now audited. The cell mixes machine-learning membership risk, distributional privacy, event-based microgrid optimization, vehicular credential infrastructure, and blockchain data ownership; their outcomes are not pooled into a single privacy effect.

## Lexical-priority full texts

### 1. Towards Deploying a Scalable & Robust Vehicular Identity and Credential Management Infrastructure (`1601.00846v1`)

The authors implement a vehicular public-key infrastructure (VPKI) with separate ticket/pseudonym, revocation, and identity-resolution functions. Its design addresses an honest-but-curious infrastructure and uses fixed, policy-aligned pseudonym lifetimes to avoid the trivial linkage created when a vehicle receives uniquely timed credentials. The evaluation is a controlled virtualized setup: 10,000 emulated vehicle threads across 25 client VMs, two-core 2.0 GHz server VMs, and 400 emulated threads per client VM. It reports about 500 ms to obtain 100 pseudonyms and compares favorably to prior systems under a similar setup; one PCA crash reportedly does not disrupt the measured response.

**Boundary:** the experiment deliberately eliminates network propagation delay, does not include vehicle-side public/private key generation (assumed offline), and uses a testbed rather than a field deployment. The paper itself identifies access-network effects as future work. The reported four-fold acceleration is therefore meaningful for its matched laboratory comparison, not proof of end-to-end latency or real-road scalability. The fixed-lifetime policy also trades reduced timing linkability against credential overprovisioning and contact frequency.

### 2. Assessing the Privacy Cost in Centralized Event-Based Demand Response for Microgrids (`1703.02382v3`)

This paper quantifies privacy cost as loss in the objective value of a differentially private centralized demand-response optimization. Its evaluation is simulation on a Canadian-benchmark 4-bus feeder rated 8.7 MVA, with 4 MVA generation and up to 1,500 simulated customers. It varies customer type, utility-demand correlation, participation, generation capacity, and privacy level. In the reported mixed-customer case with 500 customers, the paper reports a privacy-cost value of 0.59 at ε=1 and about 0.63 at ε=0.1; some homogeneous-privacy scenarios approach a cost of 1 as customer count grows. In a separate variable-privacy simulation, the reported cost fluctuates around 0.4. These results demonstrate that privacy/utility tradeoffs can be sensitive to system and population assumptions, rather than yielding one universal “cost of DP.”

**Boundary:** the customer demands/utilities and grid conditions are simulated, not measured from a deployed utility; the results are tied to the chosen feeder, objective, Laplace-based mechanism, and definitions. They do not establish that the same ε-to-utility curve holds for other grid topologies, operational data, or privacy mechanisms. The numerical claims are model-specific evidence, not a general estimate of microgrid privacy cost.

### 3. Towards Measuring Membership Privacy (`1712.09136v1`)

The paper proposes Differential Training Privacy (DTP), with pointwise DTP (PDTP) as a practical proxy, and evaluates relationships to three membership attacks. On neural networks trained on its Purchase data, attack accuracy ranges from 0.6257 to 0.8533; per-record PDTP correlation varies by attack (0.4864, 0.5052, and 0.7653). The authors report correlation 0.8936 between PDTP and the maximum per-record success across the three attacks, and a concrete counterexample: one record is at baseline for the distance-based attack but reaches 0.94 accuracy under the untargeted attack. This is direct evidence that an assessment against one attack can miss record-level exposure to another.

The evidence is not one-sided: the paper reports useful predictive association, formal DTP/PDTP definitions, and conditions under which training stability can relate the metrics. However, the same paper notes that DTP can require searching all possible queries, PDTP checks only the target record’s own feature vector, and stability is unknown for several important classifier families in its table (including neural networks and logistic regression). Its predictive results use specified data, models, shadow-model procedures, and attacks; “DTP > 1 means do not publish” is a proposed decision rule, not a universal privacy guarantee.

## Uniform-random records previously reviewed

- **On-Average KL-Privacy and its equivalence to Generalization for Max-Entropy Mechanisms** (`1605.02277v1`; batch 15): proves results for a stated Gibbs/max-entropy mechanism class and illustrates them with two simulations. Its distribution-dependent expected privacy loss is not worst-case DP, and the paper does not establish subgroup-tail behavior under distribution shift.
- **Privacy Risk in Machine Learning: Analyzing the Connection to Overfitting** (`1709.01604v5`; batch 10): reports that generalization error predicts membership-inference advantage in selected settings, while attribute-inference outcomes differ by target. The attack and benchmark assumptions bound the conclusion.
- **A privacy-preserving system for data ownership using blockchain and distributed databases** (`1810.11655v1`; previously batch 34 abstract-only): a full-text retry succeeded. The paper describes a prototype architecture using BigchainDB, MongoDB, a private Ethereum node, APIs, and uPort, with student/medical-record use cases. Its proposed data records are plaintext but de-identified; access controls and separation of identity records are design assumptions. It does not report a quantified re-identification attack, a formal privacy proof, performance/scaling measurements, or field evaluation. This is an architecture proposal/prototype, not empirical evidence that the system protects data at scale.

## Findings and next tests

The strongest cross-paper lead in this cell is about *what a privacy-risk score has actually been validated to predict*. The 2017 DTP study finds that prediction quality varies by attack and contains an individual-record counterexample; the 2017 overfitting study ties selected attacks to generalization; later SHAPr work evaluates record-level scores against two concrete attacks over ten datasets but explicitly says the absence of a demonstrably optimal attack prevents universal “any-MIA” validation. A separate 2019 study finds subgroup membership vulnerability can exceed aggregate attack accuracy in its selected image/tabular experiments. Together, these results motivate a bounded, attack- and subgroup-aware validation protocol; they do not establish that current metrics are useless or that no such protocol exists elsewhere.

Two independent systems leads should remain separate from the metric result: (a) measure VPKI end-to-end behavior with realistic access-network latency, vehicle key generation, and field-like request/load traces; (b) test the simulated microgrid ε/utility-cost curves against utility traces and alternative feeders/mechanisms. Both papers provide useful positive evidence within their stated setup, while the proposed replications target the unmeasured transfer boundary.

## Sources

- https://arxiv.org/abs/1601.00846v1
- https://arxiv.org/abs/1703.02382v3
- https://arxiv.org/abs/1712.09136v1
- https://arxiv.org/abs/1605.02277v1
- https://arxiv.org/abs/1709.01604v5
- https://arxiv.org/abs/1810.11655v1
- Targeted follow-ups: https://arxiv.org/abs/2112.02230v2 and https://arxiv.org/abs/1911.09777

This closes one six-record cell in a fixed, retrieval-prioritized frame. It is not a prevalence estimate, systematic review, independent reproduction, or novelty claim.
