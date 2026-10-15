# Full-text audit batch 29: the security/supply-chain tag mixes unlike problems

Updated 2026-10-12. This audit reads four unread uniform-random keys from `software_supply_chain`, one each in 2010–2014 and 2015–2019 (two keys). It does not claim to finish the topic cell; six other unread keys remained in this cell after this batch (audited in part in batch 30). The papers themselves range from smartcard command interleaving to OS sandboxing, database inference control, and package-ecosystem evolution, so the retrieval label is not a coherent outcome family.

## 2010–2014

### 1. Interleaving Commands: a Threat to the Interoperability of Smartcard Based Security Applications (2012; sampled v1)

[Exact sampled PDF](https://arxiv.org/pdf/1205.0900v1), especially the experimental setup and results.

The authors test two commercial smartcards from different manufacturers through a Crypto Probing System that can generate alternate APDU command sequences. In one case, commands from another signing session interleave with an Infineon signing workflow and the signature process completes without an error; on the other card, a sequence containing undefined/modified commands also terminates without warning. This is a concrete interoperability failure mode that is not covered merely by certification of each card in its original target environment.

**Boundary:** only two devices and a signing workflow are tested. It demonstrates a plausible class of unsafe interaction, not prevalence across smartcards or a deployed exploitation rate; the paper itself describes improved testing coverage as future work.

### 2. The RAppArmor Package: Enforcing Security Policies in R Using Dynamic Sandboxing on Linux (2013; sampled v3)

[Exact sampled HTML](https://arxiv.org/html/1303.4808v3), sections 2–6 and security-unit-test appendix.

This is an implementation/experience paper about using operating-system controls (AppArmor profiles, process privileges, and resource limits) to sandbox R, including untrusted contributed code and shared-service workloads. Its appendix gives executable-style checks for blocked system-file/home-directory access, memory/CPU limits, and a fork bomb. The author explicitly calls the package a proof of concept and says the paper is meant to raise awareness, not solve R security generally.

**Boundary:** the unit tests show policy behavior for selected attacks, not a comprehensive security audit, escape-rate benchmark, or cross-platform solution. The approach is Linux/AppArmor-specific and requires careful policy configuration.

### 3. Secure Logical Schema and Decomposition Algorithm for Proactive Context Dependent Attribute Based Access Control (2014; sampled v2)

[Exact sampled HTML](https://arxiv.org/html/1402.5742v2), algorithm, theorem, examples, and conclusion.

The paper formalizes “security-dependent sets” of attributes whose association should not be inferable, then decomposes a logical database schema into role-specific external schemas. It states and proves that the resulting schema blocks inference of those specified associations. The contribution is a formal guarantee under a supplied schema, functional dependencies, and policy sets.

**Boundary:** the assurance is conditional on the policy author correctly identifying sensitive attribute associations and supplying the intended dependencies. The paper proposes future modules for applying/checking the method in DBMSs; the inspected work does not report a production implementation, query-performance cost, or user study.

## 2015–2019

### 4. An Empirical Comparison of Dependency Network Evolution in Seven Software Packaging Ecosystems (2017; sampled v1)

[Exact sampled HTML](https://arxiv.org/html/1710.04936v1), methodology, results, threats to validity, and conclusion.

The study compares Cargo, CPAN, CRAN, npm, NuGet, Packagist, and RubyGems using Libraries.io metadata (CRAN metadata is separately extracted), with ecosystem snapshots through April 2017. It finds growth in packages/dependencies and a high prevalence of transitive dependencies; fragility and update concentration differ substantially by ecosystem. For example, four of seven ecosystems appear to restrain fragility better than the others; npm, NuGet, and Cargo are singled out for high impact/growth in the reported analysis.

**Boundary:** this measures technical dependency-network structure, not attacks, vulnerabilities, or supply-chain compromise. Removed packages may be missing; vendored and dynamically defined dependencies are excluded; the data are historical and ecosystem policy affects comparisons. It cannot be pooled with smartcard attack demonstrations or sandbox-policy unit tests as a common “security effectiveness” score.

## Cross-paper finding: “security/supply chain” conflates threat surfaces and evidence types

Even four neighboring sampled records answer very different questions: can commands cross-interleave on two physical smartcards; can OS policies block selected R-process actions; can a theorem guarantee non-inference given correctly specified sensitive sets; and how do dependency graphs evolve across seven historical package ecosystems? Their endpoints—silent operation anomalies, selected policy tests, a conditional theorem, and graph statistics—are not interchangeable. This does not make the umbrella retrieval useless, but it means candidate discovery must assign a threat surface and outcome class before synthesis.

**Falsifiable follow-up:** independently annotate at least 100 records from this topic by asset/threat surface (package provenance, dependency risk, runtime isolation, hardware/firmware, privacy/inference, or other) and evidence design (theorem, lab exploit, incident dataset, test suite, observational ecosystem analysis, deployment evaluation). Then estimate label agreement and test whether conclusions change after stratifying. The taxonomy concern weakens if independent reviewers consistently assign one comparable outcome family and within-family measures align.

**Sampling boundary:** four of the twelve fixed random-frame entries in this cell are audited in this batch; no prevalence claim is made. Six keys remained unread at this point. Other random items, especially the newest period, are not represented here yet.
