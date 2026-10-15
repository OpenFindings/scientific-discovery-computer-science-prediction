# Full-text audit batch 66: compilers and programming languages, 2015–2019

This batch audits the three lexical-priority entries in `compilers_programming_languages × 2015–2019` from the frozen frame. The papers span energy/performance autotuning, reproducible systems-ML evaluation, and formal complexity semantics. Their results are not pooled: one is a narrow hardware benchmark, one is primarily a platform proposal, and one is a formal theorem.

## Sampled full texts

### 1. OMP2HMPP: Compiler Framework for Energy-Performance Trade-off Analysis of Automatically Generated Codes (`1506.02833v1`)

OMP2HMPP translates OpenMP code into multiple HMPP/GPU variants, compiles and executes them, then measures runtime and energy to expose tradeoffs. On a subset of PolyBench kernels on one blade with two quad-core Intel Westmere CPUs and two Nvidia Tesla M2050 GPUs, the paper reports an average 31× speedup and 5.86× operations-per-watt improvement over the original OpenMP version. The report also states that generated code approaches hand-coded HMPP/CUDA performance. Energy includes active/idle CPU, memory and GPUs, but excludes chassis components outside the blade.

The work is explicitly bounded by a narrow benchmark/platform setup. Its search may grow exponentially with OpenMP blocks; the implementation caps configurations at 21 per simple block and identifies redundant-variant pruning as future work. The results therefore support feasibility on the measured kernels, not expected gains on arbitrary applications or modern accelerators.

### 2. Introducing ReQuEST: an Open Platform for Reproducible and Quality-Efficient Systems-ML Tournaments (`1801.06378v1`)

ReQuEST proposes an open tournament and scoreboard using Collective Knowledge workflows and artifact-evaluation practices to compare complete ML systems across models, frameworks, datasets, devices, and quality/efficiency metrics. The paper shows a proof-of-concept live scoreboard and frames broader standardization, regular tournaments, and platform coverage as goals/future work. It is a platform vision plus initial demonstration, not a controlled evaluation showing that the approach itself improves reproducibility or eliminates comparison bias.

**Boundary:** a shared workflow can make artifacts and measurements more inspectable, but does not by itself make different datasets, hardware, software stacks, or objectives comparable. A tournament must still pin workload, metrics, environment, and artifact versions.

### 3. The Weak Call-By-Value λ-Calculus is Reasonable for Both Time and Space (`1902.07515v1`)

The authors prove a strong invariance result for deterministic weak call-by-value λ-calculus, using β-reduction count as time and maximum intermediate-term size as space: simulations between that calculus and Turing machines have polynomial time overhead and constant-factor space overhead for computations returning encoded Boolean values. The stated theorem assumes time and space bounds in Ω(n). The paper supplies Coq formalization for its sections 2 and 3.

The claim is about this evaluation strategy and these formal cost measures; it is not a theorem for unrestricted/full λ-calculus or a performance result for a production compiler. The authors explicitly say that implementation questions remain and that their construction is not a uniform canonical implementation.

## Bounded synthesis and testable leads

1. **Automatic optimization gains are hardware-, workload-, and search-budget-dependent.** Replicate compiler autotuning on a preregistered suite of kernels and full applications across at least two CPU/GPU generations. Report the full Pareto frontier for runtime, energy with a clearly specified meter boundary, compilation/search time, and missed configurations under fixed search budgets. The claim weakens if the reported gains generalize across held-out workloads and platforms without material search cost.
2. **Reproducibility platforms need outcome evaluation, not only artifact infrastructure.** Compare a ReQuEST-style workflow with ordinary paper-level reproduction on blinded teams and matched systems benchmarks. Measure artifact execution success, result variance, time-to-reproduction, and rank stability under platform/workload changes. A platform contribution is effective only if these outcomes improve, not merely because code and metadata are published.
3. **Formal complexity guarantees and practical implementation quality are separate questions.** Implement the paper’s weak-CbV simulation and alternative machines in a common proof/benchmark harness, checking theorem assumptions and measuring actual time/space constants on finite workloads. Keep formal asymptotic guarantees separate from implementation efficiency; do not extrapolate this theorem to other evaluation strategies without proof.

These are bounded research leads, not claims that the sampled works are incorrect or that their contributions have not been adopted or extended.

## Primary sources

- https://arxiv.org/abs/1506.02833
- https://arxiv.org/abs/1801.06378
- https://arxiv.org/abs/1902.07515
- https://popl20.sigplan.org/details/POPL-2020-Research-Papers/51/The-Weak-Call-By-Value-Calculus-is-Reasonable-for-Both-Time-and-Space
