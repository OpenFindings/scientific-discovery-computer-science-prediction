# Full-text audit batch 20: structure-preserving abstractions in programming systems

Updated 2026-10-11. Four fixed-frame uniform-random `compilers_programming_languages` records were reviewed, one per submission period. These papers address different tasks—program proofs, energy analysis, adaptive communication, and memory tiering—but together motivate a bounded design hypothesis: automation becomes more capable when the representation retains the structure the target question needs. This is a cross-paper synthesis to test, not a universal law.

## 1. Structural Induction Principles for Functional Programmers (2013)

[Caldwell, arXiv:1312.2696v1](https://arxiv.org/abs/1312.2696); author-hosted [full PDF](https://www.cs.uwyo.edu/~jlc/papers/TFPIE13.pdf), §§3–5 and Appendix A.

The paper gives a Haskell algorithm that derives a structural-induction principle from an algebraic data-type declaration. The generated cases follow the type constructors and include an induction hypothesis for recursive fields, including parameter-swapping recursive types such as `SwapTree a b`. The author describes its place in a functional-programming course and gives examples of induction proofs and exam questions.

**Boundary:** this is a construction and teaching account, not a controlled education study. The generator had not yet been used in that course when the paper was written; quizzes/exams were proposed to evaluate student learning later. Mutually recursive types are said to be a straightforward generalization but are omitted from the course implementation; lazy Haskell's bottom value requires an extra case beyond finite constructor structure.

## 2. Inferring Parametric Energy Consumption Functions: ISA vs LLVM IR (2015)

[Liqat et al., arXiv:1511.01413v1](https://arxiv.org/abs/1511.01413); [author/institution full PDF](https://software.imdea.org/~umer/publications/fopara15.pdf), §§2–6, Tables 1–2.

The static analyzer estimates energy as a function of input size, mapping measured ISA-instruction energy onto LLVM IR blocks and analyzing those blocks via a Horn-clause representation. LLVM IR retains type and data-shape information that lower-level ISA has lost. On one benchmark group, ISA estimates are more accurate (reported mean errors 3.9% vs 9% for LLVM IR); on a second group involving structured data, ISA cannot infer useful functions for some benchmarks, whereas LLVM IR analyzes all of that group with about 3% mean error and roughly 5–6 seconds analysis time. The result is a concrete precision-versus-analyzability trade-off, not a single winner.

**Counterweight:** the experiments use XC programs and XCore hardware, with an existing measured ISA energy model and a mapping layer. The LLVM mapping is approximate and loses some precision. The authors explicitly warn that using average per-instruction energy can make a purported upper-bound analysis underestimate actual worst-case energy; a sound worst-case guarantee would require suitable upper bounds in the energy model. Transfer to other architectures/toolchains is not demonstrated here.

## 3. Multiparty Session Types for Safe Runtime Adaptation (2021)

[Harvey et al., arXiv:2105.06973v1](https://arxiv.org/abs/2105.06973); full [ECOOP proceedings/extended paper PDF](https://simonjf.com/writing/ensemble.pdf), §§3–5.

EnsembleS combines an actor language with multiparty session types and explicit connect/disconnect actions. The protocol representation preserves who may communicate, message kinds, and the legal order of actions while actors are discovered or replaced at runtime. The authors implement a DNS-resolution case study with runtime discovery of root and zone servers, and formalize a core calculus with type-safety/progress results. The paper also reports an artifact and code-generation/typechecking pipeline.

**Boundary:** the DNS scenario demonstrates feasibility, not deployment reliability, fault rates, or throughput under changing production topology. The formal calculus deliberately omits some implementation details and focuses on dynamic protocol typing. The paper says runtime performance results for the inherited Ensemble runtime are in separate prior work; it does not establish an adaptation-overhead figure in this study. Guarantees concern conformance to the specified communication protocol, not that a discovered service is honest, available, or semantically correct.

## 4. Tidying Up the Address Space / HADES (2025)

[Banakar et al., arXiv:2510.19765v1](https://arxiv.org/html/2510.19765v1), §§2–6.

HADES tracks access at object/pointer granularity, groups hot and cold objects into separate address-space regions, and then lets existing page-level reclamation backends operate on the reorganized pages. In the reported setup—CrestDB, ten pointer-based concurrent data structures, one 16-core Xeon Gold host, and YCSB A/B/C—the paper reports 2×/3×/4× improvements in page utilization after classification, up to 70% lower memory usage, and an average 2.5% throughput reduction plus 5% latency increase from instrumentation. In a 12-GB-footprint YCSB-C experiment with about 4 GB actively used, the paper reports that backends can reclaim toward 4 GB without the performance penalties observed in the unorganized baseline.

**Counterweight and applicability boundary:** this is a controlled benchmark/custom key-value-store setup, not evidence that arbitrary production applications will get the headline memory reduction. HADES requires pointer stability to be dispensable, unique ownership of managed objects, explicit annotations, and no reliance on pointer arithmetic/contiguous layout; it targets C++/Rust-like operator-overloading support. The instrumented path has measurable throughput/latency costs, even though the abstract highlights 3% overhead. The paper does not cover aliases or arrays/matrices that violate these assumptions.

## Bounded cross-paper finding

Across these four sampled papers, a plausible design principle recurs: preserve task-relevant structure at the level where the reasoning/action happens. Type constructors make proof obligations derivable; LLVM IR retains array/type information that ISA discards; session types retain distributed message order during runtime discovery; object-level hotness can make page-level reclamation more effective. But no common outcome can be pooled: these are different guarantees and utilities, and their reported evidence ranges from formal proof to a single case study to a controlled hardware test.

**Falsifiable next test:** for several classes of tools, compare a structure-preserving representation against a deliberately coarsened representation while holding algorithms, inputs, compute budget, and target outcome fixed. For program analysis, compare type/shape-aware IR with ISA-only features on unseen array-using programs; for adaptive services, compare protocol-typed discovery against interface-only discovery on held-out protocols and injected topology changes; for memory tiering, compare object-aware versus page-only classification on applications that both satisfy and violate pointer/ownership assumptions. Measure task success, soundness/correctness violations, runtime/memory overhead, and transfer. The hypothesis is weakened if extra structural information does not improve the relevant outcome or if its collection/maintenance costs erase the gain.

This is a four-paper hypothesis-generating slice, not an independent replication, field-wide trend, or novelty claim.
