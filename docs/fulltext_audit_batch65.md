# Full-text audit batch 65: distributed systems, 2010–2014

This batch closes the lexical-priority arm for `distributed_cloud_systems × 2010–2014`. The three sampled works below were selected from the frozen frame by the declared arm; the two additional full texts are targeted counterevidence/follow-ups, not random sample members. “Optimal” and performance numbers are kept within each paper’s stated model and experiment.

## Sampled full texts

### 1. Geodesic stability for memoryless binary long-lived consensus (`1102.4100v1`)

The paper studies binary colorings of the n-dimensional hypercube that respect the two fault-tolerance balls. Instability counts output changes along a geodesic input path, where each sensor coordinate changes at most once. It states the main conjecture `inst(n,t)=2t+1`; the paper gives matching constructions and lower bounds, but its general zig-zag theorem proves the conjecture only for `t=0` and `t=1`, with stronger results for selected parameter cases (Theorems 4.1–4.2). It is not a proof of the full conjecture for every n,t. The paper also notes that unrestricted paths may revisit coordinates and behave differently.

**Boundary:** this is a worst-case geodesic criterion for a memoryless binary rule, not an average churn measure on a workload trace or a general distributed-consensus deployment result.

### 2. Locally Repairable Codes (`1206.3804v2`)

The paper formalizes repair locality as the number of other coded symbols accessed to reconstruct a symbol, and derives a tradeoff between locality, minimum distance, and storage capacity (Theorem 1), with constructions attaining the bound under stated parameter conditions (Theorem 2). The introduction explicitly distinguishes locality from repair bandwidth and from the number of bits read during repair (disk I/O); it notes that low-locality codes can be suboptimal on bandwidth or require more storage than MDS codes.

**Boundary:** the central result is a code-parameter tradeoff, not an end-to-end guarantee for repair time, network traffic, or production reliability. A locality win cannot stand in for those measurements.

### 3. XORing Elephants: Novel Erasure Codes for Big Data (`1301.3791v1`)

This work builds locally repairable codes and evaluates an HDFS prototype (HDFS-Xorbas) against HDFS-RS on Amazon EC2 and a Facebook test cluster. In EC2, across 50/100/200-file experiments and the reported failure events, Xorbas reads 41–52% as much HDFS data to repair the same number of lost blocks and completes repairs 25–45% faster. Its design uses about 14% more storage; the authors estimate this can produce 14.3% more blocks lost under a random failure event. The measured network peaks did not fully saturate the testbed. The protocol is a small controlled prototype experiment, not a randomized production rollout or evidence across modern storage architectures.

**Boundary:** the gains are real for the measured prototype, workload, and failure schedule; translate neither the percentage gains nor the reliability claim directly to production without matched traces, storage overhead, topology, and durability criteria.

## Targeted full-text counterevidence and scope checks

### Average Binary Long-Lived Consensus: Quantifying the Stabilizing Role Played by Memory (2008)

This earlier full text contrasts worst-case geodesic instability with average instability under random walks. A one-bit memoryless rule can be geodesic-optimal at `t=0` yet have average instability `1/n`, while an average-optimal memoryless rule can have average instability `n/2^n`; the criteria rank rules differently. The paper also proves that one bit of memory is sufficient for its optimal average-stability construction. This is a model-level comparison, not a claim about observed sensor deployments.

### Practical Design Considerations for Wide Locally Recoverable Codes (FAST 2023)

Using unavailable-stripe patterns from four Google clusters, this study shows that width/overhead and a distance guarantee alone do not determine practical recovery. In a counterfactual replay, the deployed wide-code configuration recovered none of 278 unavailable stripes before restoration, whereas a Uniform Cauchy LRC simulation with the same width/overhead recovered 92 (33%). Recovery depends on the erasure pattern and local-group layout; the 92/278 result is a replay, not a live randomized replacement. The source also considers operational tradeoffs such as degraded reads and reconstruction costs.

## Bounded synthesis and experiments

1. **Consensus stability depends on the objective.** Worst-case geodesic changes and expected random-walk changes are not interchangeable; memory can change the average-optimal solution. Test matched memoryless and one-bit-memory policies on the same preregistered input paths, reporting both worst-case geodesic flips and workload-weighted mean/tail churn. The claim weakens if rankings remain invariant across objective and path distribution. Keep binary inputs and fault model explicit.
2. **Repair locality is not a sufficient systems metric.** Low symbol-access locality trades against distance/storage and need not minimize bytes read or repair bandwidth. Compare code families at matched durability and storage overhead; report accessed symbols, bytes read, network bytes, repair latency, and loss probability separately.
3. **Wide-LRC reliability depends on actual erasure geometry and layout.** Replay real multi-cluster failure/maintenance traces across code/group layouts at fixed width and overhead; report stripe recovery before restoration, degraded-read cost, bytes moved, and latency. A live randomized deployment would be needed to establish causal production benefit.
4. **Prototype repair savings need overhead-aware, workload-matched replication.** Re-run Xorbas-like and RS-like designs under identical data volume, placement, and both independent and correlated failures; normalize repair I/O and time by lost blocks while including the extra storage’s effect on failure exposure. Include saturated and unsaturated network regimes.

These are evidence-bounded research leads, not novelty or field-wide resolution claims. In particular, this audit does not establish whether later work has resolved the 2011 consensus conjecture in its full generality.

## Primary sources

- https://arxiv.org/abs/1102.4100
- https://arxiv.org/abs/1206.3804
- https://arxiv.org/abs/1301.3791
- https://repositorio.uchile.cl/bitstream/handle/2250/125340/Becker_Florent.pdf?isAllowed=y&sequence=1
- https://research.google/pubs/practical-design-considerations-for-wide-locally-recoverable-codes-lrcs/
- https://storage.googleapis.com/gweb-research2023-media/pubtools/7341.pdf
