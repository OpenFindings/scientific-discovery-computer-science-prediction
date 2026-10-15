# Full-text audit batch 43: distributed-system performance claims use different evidence

Updated 2026-10-12. This batch closes the seven remaining uniform-random records in `distributed_cloud_systems` across the four sampled time bands. Three papers concern consensus/security, one asynchronous key generation, two distributed systems/runtime theory, and one edge-AIGC simulator. Their headline performance claims are not commensurable: they range from theorems, through machine microbenchmarks, to simulation and initial design proposals.

## Seven sampled full texts

### 1. Causality, Influence, and Computation in Possibly Disconnected Dynamic Networks (arXiv:1206.1290v1; journal 2014)

[Author full text](https://cgi.csc.liv.ac.uk/~michailo/Documents/Papers/Journals/jpdc14.pdf) · [journal record](https://doi.org/10.1016/j.jpdc.2013.07.007).

The work relaxes per-round connectivity in adversarial synchronous dynamic networks. Its models instead require temporal influence/coverage conditions over bounded windows; under those assumptions, information dissemination and computation remain possible even when every instantaneous graph can be disconnected. The paper develops termination criteria and protocols for counting and gossip/token dissemination, including optimality in specified cases. This is a formal worst-case model, not a trace-driven evaluation of mobile networks; the temporal-connectivity conditions and what nodes know are central premises.

### 2. DART-MPI: An MPI-based Implementation of a PGAS Runtime System (arXiv:1507.01773v1; 2015)

[Full text](https://arxiv.org/pdf/1507.01773v1).

DART implements a PGAS runtime over MPI-3 one-sided communication. The paper does not stop at an architecture sketch: it measures blocking/nonblocking puts and gets and low-level kernels on a Cray XE6, comparing its runtime overhead with native MPI. Reported extra latency is on the order of roughly 80–130 ns for the measured operation classes, with message-protocol changes visible around 4 KB. This is a real machine measurement, but it is platform- and primitive-specific; it does not by itself establish application-level speedups or programmer-productivity benefits on contemporary systems.

### 3. TrueChain: Highly Performant Decentralized Public Ledger (arXiv:1805.01457v3; 2018)

[arXiv record/full text](https://arxiv.org/abs/1805.01457).

This is an initial system-design account of TrueChain/Minerva, combining hybrid consensus, permissioned-chain processing elements in a permissionless design, sharding, speculative execution, and an ASIC-resistant mining proposal. Importantly, the full text reports two very different throughput figures: about 80 TPS when committee votes use the full proof-of-work gossip network, then over 2,000 TPS in a beta-net deployment using a private committee gossip design with gossip degree below one-sixth of committee size. That is a reported >25× contrast inside one paper, but not a clean controlled estimate: the paper does not specify a matched workload/configuration or give a detailed reproducibility, latency, or security evaluation for the two numbers. The authors explicitly describe throughput-versus-security tradeoffs as the gossip degree changes and note eclipse-attack risk for poorly connected private gossip. This is a promising design clue, not proof that topology alone caused a 25× gain.

### 4. GHAST: Breaking Confirmation Delay Barrier in Nakamoto Consensus via Adaptive Weighted Blocks (arXiv:2006.01072v1; 2020)

[arXiv full text](https://arxiv.org/abs/2006.01072).

GHAST organizes blocks as a tree-graph and adaptively changes block weights to preserve progress under attacks. Under the paper's model—with maximum message latency d and adversarial compute power bounded away from 50%—it proves confirmation with confidence at least 1−ε after O(d log(1/ε)) time. The “3d versus roughly 360d” comparison is specifically the no-observable-attack case against Bitcoin's six-block confirmation at the same confidence, not an all-conditions deployment benchmark. The theoretical latency result and the live network's throughput, propagation, and operational risks are separate evidence questions.

### 5. Reaching Consensus for Asynchronous Distributed Key Generation (arXiv:2102.09041v3; PODC 2021)

[arXiv full text](https://arxiv.org/abs/2102.09041) · [PODC record](https://doi.org/10.1145/3465084.3467914).

The A-DKG protocol tolerates f<n/3 Byzantine parties, has a constant expected number of asynchronous rounds and Õ(n³) expected communication, assuming a public-key infrastructure. Relative to prior protocols described by the authors, the claimed improvement is asymptotic (from Ω(n) rounds and Ω(n⁴) communication). The contribution is protocol analysis, not a production-system latency benchmark; “constant expected rounds” under asynchronous scheduling should not be translated directly into a fixed wall-clock deadline.

### 6. Revisiting Lower Bounds for Two-Step Consensus (arXiv:2505.03627v2; PODC 2025)

[Full text and PODC publication details](https://arxiv.org/html/2505.03627).

The paper explains an apparent contradiction between Lamport's classical process-count lower bound for fast consensus and practical protocols such as Egalitarian Paxos: the classic bound demands fast decisions in a broader set of scenarios than some practical applications need. With a more pragmatic condition—one process may decide quickly for general initial values, while all correct processes must decide quickly when they start with a common proposal—the authors prove matching tight bounds. For an f-resilient e-two-step **decision task**, n≥max(2e+f, 2f+1); for an atomic **consensus object**, n≥max(2e+f−1, 2f+1). Assumptions are partially synchronous crash-prone processes and reliable links; the task/object distinction changes the threshold by one. The paper refines the specification/lower-bound trade-off rather than showing that an implementation has lower observed latency.

### 7. Unleashing the Power of Tree-of-Thoughts for Edge-Enabled AIGC Service Provisioning (arXiv:2605.19108v1; 2026)

[arXiv full text](https://arxiv.org/html/2605.19108).

This paper studies assigning parts of a Tree-of-Thoughts generation DAG between user devices and edge servers. It first measures output-token count, generation delay, and quality using Qwen 2.5-7B-Instruct on creative-writing tasks; it then evaluates a diffusion-based soft actor-critic (DSAC) placement policy in simulations. The abstract reports up to 8.32% lower total delay than PPO, 11.57% than SAC, and 36.09% than DDQN, plus over 80% lower latency than a fully local baseline in simulated settings with quality constraints. Those are maxima over the tested settings, not average universal gains; the evidence is simulation grounded in one model/task family, not a live multi-edge deployment or a broad measure of generated quality.

## Bounded synthesis and research lead

The cell provides a useful audit lesson, not one pooled performance result: DART-MPI reports measured nanosecond-scale overheads on a Cray XE6; TrueChain reports a >2,000 TPS beta-net point but without a matched comparative protocol; GHAST and A-DKG supply model-based asymptotic/probabilistic guarantees; two-step consensus tightens a formal lower bound after changing the specification; and the edge-AIGC result is simulator-based. A number from one evidence class cannot confirm or refute a result in another, and even a live measurement can be too thinly specified to support broad comparative claims.

One sharper, still unverified lead emerges within TrueChain: the paper contrasts roughly 80 TPS using public-network gossip for BFT voting with >2,000 TPS after introducing private committee gossip, while explicitly warning that connectivity choices trade throughput against security/eclipsing risk. A proper test would hold hardware, workload, transaction mix, committee size, and adversary constant while varying gossip topology and measuring TPS, confirmation-latency tails, safety/liveness failures, and attack surface. The published two figures alone do not establish that causal effect.

**Falsifiable research lead (not a novelty claim):** test whether system papers' headline performance wording is calibrated to their strongest evidence. Sample distributed/cloud/edge papers by year and subfield; independently code the claim (e.g. “fast/high-throughput”), evidence class (theorem, microbenchmark, trace replay, simulation, deployment), baseline quality, workload diversity, and reporting completeness (workload, hardware/network, repetitions, latency distribution, security/adversary conditions). The lead is weakened if blinded annotators find that broad claims are generally accompanied by diverse, representative, sufficiently specified measurements and external replication. This audit has not yet been run; this batch is a set of motivating cases, not its population estimate.

## Audit boundary

All seven random papers in `distributed_cloud_systems` are now reviewed/dispositioned. Venue data is verified for the 2014 journal paper and two PODC papers as linked; not for the other sampled papers. This is not an exhaustive history of consensus, PGAS, or edge-AIGC; no live protocol deployment, cryptographic re-proof, independent reproduction, or systematic citation search was performed.
