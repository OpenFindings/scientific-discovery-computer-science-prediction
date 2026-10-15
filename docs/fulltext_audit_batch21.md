# Full-text audit batch 21: efficiency claims are conditioned on service guarantees

Updated 2026-10-11. Four fixed-frame uniform-random `distributed_cloud_systems` records were reviewed, one per submission period. Their outcomes are not comparable as one metric: pausing VMs, building energy control, proposed GPT-cloud schedulers, and multi-model LLM serving optimize different services. The useful cross-paper question is whether resource savings/capacity are reported at an explicit and comparable service-quality boundary.

## 1. Take a Break: Cloud Scheduling Optimized for Real-Time Electricity Pricing (2013)

[Lučanin and Brandić, arXiv:1307.7037v1](https://arxiv.org/abs/1307.7037); [full arXiv PDF](https://arxiv.org/pdf/1307.7037), §§III–V and conclusion.

The OpenStack prototype predicts expensive hours from historical hourly electricity prices, then pauses an opted-in VM for four hours per day. In the 24-hour empirical comparison, one single-threaded synthetic Fibonacci workload received four fewer CPU hours (17.6% fewer calculations); measured total energy fell about 5.3% and calculated electricity expense about 6.9%. The authors' larger production projection is synthetic: with an idealized 200-W peak/0-W idle server it estimates 17.1% energy and 26.63% price savings, while availability falls to 83.3%. The proposed environmental/carbon accounting is also an estimate based on grid factors, not a direct carbon measurement.

**Boundary:** the empirical run is one workload on one VM/server over one day. Results depend on historical predictability of hourly price peaks and on a service contract that permits downtime. The larger headline numbers assume a highly energy-proportional or suspendable server and simplified transitions. The paper itself calls for more parallel, memory-, I/O-intensive, and website workloads.

## 2. An Internet of Things Framework for Smart Energy in Buildings (2015 venue; 2016 arXiv submission)

[Pan et al., arXiv:1603.08025v1](https://arxiv.org/abs/1603.08025); [full journal PDF](https://mason.gmu.edu/~jpan22/papers/0.iot.2015.pdf), §§II–IV and conclusion.

The paper analyzes nearly one year of energy traces from one LEED-Gold campus office building, then presents a location-aware IoT control framework and prototype. Its building-level traces show that static controls need not track occupancy. Its system experiment follows one user's location over 24 hours and compares recorded device energy after the prototype policy with estimated “normal,” “luxury,” and “frugal” modes; the authors report the prototype consumption as close to the estimated frugal mode.

**Boundary:** distinguish the year-long observational building analysis from the short user-scale prototype demonstration. The paper does not report a randomized or long-term building-wide causal estimate of energy savings. The prototype comparison includes estimated mode baselines and a particular user's location/device scenario; effects can differ by building and occupant habits. The arXiv submission is 2016, but the audited journal article appeared in 2015.

## 3. Resource Management for GPT-Based Model Deployed on Clouds (2023)

[Dang, Xu, and Ye, arXiv:2308.02970v1](https://arxiv.org/abs/2308.02970); [full arXiv PDF](https://arxiv.org/pdf/2308.02970), §§1–5.

This paper defines resource/QoS concerns, proposes a framework with profiling, scheduling, allocation, synchronization, and QoS components, and gives pseudocode for utilization-oriented, load-balancing, and power-oriented placement. It is useful as a design proposal and explicitly points to the need for standardized benchmarks and broader evaluation metrics.

**Boundary:** the full text presents no executed benchmark comparing these algorithms, no measured serving outcomes, and no validated resource-demand predictor. The pseudocode depends on functions such as `estimateResourceDemand()` and `estimatePower()` without an empirical validation in this paper. Therefore it supplies candidate objectives and architecture, not evidence that the proposed scheduling improves utilization, latency, energy, or cost.

## 4. Towards Resource-Efficient Serverless LLM Inference with SLINFER (2025)

[Xu et al., arXiv:2507.00507v2](https://arxiv.org/abs/2507.00507); [full arXiv HTML](https://arxiv.org/html/2507.00507), §§III–IX, especially IX-A–IX-I and discussion.

SLINFER shares CPU/GPU capacity among infrequently invoked small- and mid-sized models while checking time-to-first-token (TTFT) and inter-token latency (TPOT) service-level objectives. On a testbed with four 32-core Intel Xeon 6462C CPU nodes and four A100-80GB GPU nodes, its 128-model cases report 47–62% more SLO-met requests than the tuned `sllm+c` baseline and 86–154% more than `sllm`; the exact percentages vary by model size and comparator. Workloads combine Azure LLM token lengths with a 30-minute Azure serverless trace segment sampled to 32/64/128 functions. Under the tested mixed 3B/7B/13B setting, sharing increases capacity; in the paper's LongBench sensitivity case CPUs do not meet the TTFT target, and the authors note that older CPUs without AMX, long inputs, tight SLOs, or larger models narrow or remove CPU-sharing benefits. At 128 13B models, all systems exhaust the available nodes.

**Boundary:** this is a substantial systems evaluation, but its headline is SLO-met request capacity under selected workloads, baselines, hardware, model sizes, and SLO definitions—not lower joules or dollars per equivalent answer. The Azure trace segment is sampled and models are replicas mapped onto it; real deployments may differ in arrivals, model mix, generation quality, and hardware. Gains shrink as load/model size saturates the testbed, and CPU benefits depend on recent AMX-equipped machines and moderate latency targets.

## Bounded cross-paper finding

The recurring issue is not that any one efficiency result is necessarily wrong; it is that “more efficient” has different denominators and accepted service losses. The 2013 cloud experiment trades away availability and computation, with the largest energy/cost numbers projected under idealized hardware. The 2015 building paper's trace analysis and one-user prototype do not establish long-term building-wide causal savings. The 2023 paper supplies schedulers without an experimental comparison. SLINFER measures accepted requests under explicit TTFT/TPOT targets on a particular cluster and workload, not energy per completed equivalent task. Those are distinct evidence classes and must not be plotted as a single historical trend.

**Falsifiable next test:** for each system, preregister the service envelope first—availability/completion, latency distribution, output quality or task correctness, and workload mix—then compare resource use and cost against a tuned baseline at matched service quality. Sweep the service envelope to produce a Pareto curve (resource per successful task versus service degradation), use held-out real traces and hardware, and include transition/idle energy and rejected/timed-out requests. The proposed common hypothesis is weakened if savings/capacity gains disappear at matched service quality, fail on held-out workloads, or are outweighed by omitted transition, measurement, and operating costs.

This is a four-paper hypothesis-generating slice from a predeclared random frame, not an estimate of field prevalence, a meta-analysis, or a novelty claim.
