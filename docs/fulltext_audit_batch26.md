# Full-text audit batch 26: “reasoning and agents” spans incompatible outcomes

Updated 2026-10-11. Completed the 11 unread uniform-random records in `reasoning_and_agents`, across the four fixed arXiv-submission strata. The 2015–2019 cell is now complete with the 2015 multi-agent path-planning paper already audited in batch 10 plus the two papers below. This is the declared random sample for one screen label, not a representative sample of all reasoning/agent research.

## 2010–2014

### 1. Variance-Based Rewards for Approximate Bayesian Reinforcement Learning (2012)

[Sorg, Singh, and Lewis, arXiv:1203.3518v1](https://arxiv.org/abs/1203.3518); [full arXiv PDF](https://arxiv.org/pdf/1203.3518v1), §§2–5.

The authors add a bonus based on posterior variance in a mean-MDP planner, so observations can reduce uncertainty across state/action pairs linked by a structured prior. The theory gives prior-dependent sample-complexity bounds; for a prior over deterministic worlds, a single sample can identify an observed state/action transition. In a 4×4 Hunt-the-Wumpus task, averaged over 500 episodes, the variance bonus obtains mean reward 0.508, compared with 0.293 for the `1/n` bonus, 0.291 for `1/√n`, 0.266 for mean-MDP without bonus, and 0.183 for BOSS. The comparison tunes bonus parameters and supplies the same prior to competitors.

**Boundary:** the gain is shown in two constructed environments, not a broad real-world benchmark. The theorem is tied to a correct Bayesian prior/model and its assumptions; results with uninformative Dirichlet priors are similar to established bonuses, while the notable advantage is for structured priors. The Wumpus reward is task-specific and the bonus is not always optimal: the agent can keep exploring pits after finding the Wumpus.

### 2. Identifying Reasoning Patterns in Games (2012)

[Antos and Pfeffer, arXiv:1206.3235v1](https://arxiv.org/abs/1206.3235); [full arXiv PDF](https://arxiv.org/pdf/1206.3235v1), §§2–4 and conclusion.

The algorithm inspects multi-agent influence diagrams (MAIDs) for four graphical reasoning patterns—direct effect, manipulation, signaling, and revealing/denying information—and removes decision nodes that do not participate in any pattern. The intended benefit is a smaller game to solve for Nash equilibrium; the graph-search and d-separation subroutines are polynomial-time. The paper demonstrates the interpretation on a constructed principal–agent game and gives structural arguments about possible reductions.

**Boundary and counterevidence:** the claimed potential for exponential savings is not an empirical runtime result in this paper. No benchmark suite measures equilibrium solver speed or quality. The authors say their strictly graphical tests can miss simplifications that depend on chance/utility parameters and identify parameter-aware analysis and experimental investigation as future work. A node that looks strategically relevant in the graph may still be behaviorally irrelevant under the actual parameter values.

### 3. Simple Regret Optimization in Online Planning for Markov Decision Processes (2012)

[Feldman and Domshlak, arXiv:1206.3382v2](https://arxiv.org/abs/1206.3382); [full arXiv HTML](https://arxiv.org/html/1206.3382v2), §§3–7.

BRUE separates sample effort spent identifying a good action in downstream states from effort estimating that action's value to predecessor decisions. Under finite MDP assumptions it proves exponential-rate reduction of simple regret and action-selection error, an endpoint more directly tied to the decision to execute than cumulative reward collected during simulated planning. The empirical study tests sailing grids of size 5×5 through 40×40 and random trees (1000 random starting states for sailing; 500 trees per random-tree setting), against UCT and ε-greedy+UCT. The authors also study a “learning by forgetting” variant.

**Boundary:** exponential convergence is an asymptotic/theoretical rate, not a promise of low regret after a small fixed budget; the paper itself analyzes a transition period before the bound becomes useful. Sailing uses a chosen finite horizon based on grid size, and the other tests are random game trees. These controlled MDP experiments do not show transfer to unknown real environments, partial observability, or human-agent interaction.

## 2015–2019

### Previously reviewed frame item: Proximal Operators for Multi-Agent Path Planning (2015)

[Bento et al., arXiv:1504.01783v1](https://arxiv.org/abs/1504.01783); existing full-text audit: [batch 10, section 4](</Users/amao/Documents/ChatGPT/ScientificDiscovery/docs/fulltext_audit_batch10.md:35>).

This is not counted again in this batch. Its synthetic numerical work reports roughly 2× speedup with eight cores in one 3D scenario and recognizes local minima; it offers no global-optimum guarantee or real-robot validation. It is an optimization/planning objective, not the same outcome as the MDP simple-regret result above.

### 4. Goal Inference Improves Objective and Perceived Performance in Human-Robot Collaboration (2018)

[Nikolaidis et al., arXiv:1802.01780v1](https://arxiv.org/abs/1802.01780); [full arXiv PDF](https://arxiv.org/pdf/1802.01780v1), §§3–5 and limitations.

In a virtual task-allocation study, 234 Mechanical Turk participants were recruited and 196 remained after attention-check and experiment-error exclusions. Participants selected a goal task, but the human avatar trajectory was predefined. More adaptive virtual robots were faster: reactive versus fixed improved task time by 0.52 seconds, and oracle-predictive versus reactive by 0.69 seconds; the Bayesian-predictive robot was 0.34 seconds slower than oracle-predictive. Participants also preferred and rated more adaptive robots more highly.

**Counterevidence and boundary:** one stated expectation was not supported: Bayesian inference did not reduce the number of robot-completed tasks versus the oracle; it completed 1.7 more on average, a small difference across 39 one-agent tasks. The authors speculate that erroneous inferred goals may have caused the robot to take over other tasks, but say the mechanism needs follow-up. It is a virtual task with scripted avatar motion and an assumption of optimal human planning, not a physical deployment; the paper itself notes some manufacturing contexts may favor robots that lead rather than adapt.

### 5. Toward a Computational Theory of Evidence-Based Reasoning for Instructable Cognitive Agents (2019)

[Tecuci et al., arXiv:1910.03990v1](https://arxiv.org/abs/1910.03990); [full arXiv PDF](https://arxiv.org/pdf/1910.03990v1), §§1–5.

The paper presents a framework for abductively proposing hypotheses, using them to guide evidence collection, and testing them with argument structures and evidence credibility. It describes a teachable agent shell and four prototypes spanning intelligence analysis, science education, cybersecurity, and surveillance/reconnaissance.

**Boundary:** this is a theory/architecture and prototype overview, not a comparative user or task-performance evaluation. It does not quantify accuracy, time, calibration, or error reduction against human-only or alternative agent baselines. Its transparency and instructability are design properties illustrated through examples; the claimed practical value requires independent task-level validation.

## 2020–2024

### 6. Learning Deductive Reasoning from Synthetic Corpus Based on Formal Logic (2023; sampled v3)

[Morishita et al., arXiv:2308.07336v3](https://arxiv.org/abs/2308.07336); [exact sampled full-text version](https://arxiv.org/html/2308.07336v3), §§4–7 and Appendix B.

The FLD corpus generates first-order-logic proof examples from a complete axiom set. It distinguishes answer accuracy from stricter proof accuracy, which requires both the answer and generated proof to be correct. In the reported 10-shot evaluation on FLD, GPT-4 answer accuracy is 52.4% while proof accuracy is 12.8%; on the harder FLD-star version, the values are 49.4% and 3.2%. The gap is concrete evidence that a correct final answer does not establish that the stated reasoning is valid. Fine-tuned T5 proof accuracy varies sharply across corpora: 92.4/93.9 on RuleTaker/RuleTaker-PR, 66.4 on FLD, and 37.7 on deeper FLD-star. Synthetic distractors also improve transfer robustness in the authors' ablation.

**Counterweight and boundary:** the authors do test transfer to human-authored EntailmentBank and report benefits versus baselines, so the contribution is not only performance on toy synthetic data. However, they state that their study covers only deduction from given facts in first-order predicate logic; other logic systems and reasoning types remain open. The synthetic proof rules are highly structured, and transfer to EntailmentBank required training on its full examples because its proof steps differ from the synthetic corpora. Neither result proves general-purpose reasoning.

### 7. Towards Robust Multi-Modal Reasoning via Model Selection (2023; sampled v2)

[Liu et al., arXiv:2310.08446v2](https://arxiv.org/abs/2310.08446); [exact sampled full-text version](https://arxiv.org/html/2310.08446v2), §§4–5 and appendices E–G.

M³ selects different vision/language specialist models at subtasks in a multi-step GQA/VisProg pipeline. MS-GQA begins with 10,000 test-dev examples; examples where the LLM-generated computation graph fails are removed, leaving 8,426 valid examples. Five-seed experiments report an overall successful-execution rate around 69% for M³ versus about 56% for random selection, around 60% for existing multimodal agents, and 100% for a per-example oracle. M³ improves the full-set score by 2.69% over MetaGL; the baseline rankings differ by subtask (VisProg is relatively strong on Compare but poor on Query/Choose).

**Counterweight and boundary:** the oracle gap remains large, and the authors say results are constrained to this single benchmark by resources. Filtering out invalid LLM-generated graphs conditions evaluation on successful task decomposition; that makes the selector's result different from end-to-end task success. The system is benchmarked on GQA/VisProg with a specified model pool, not diverse real-world multimodal agents.

### 8. Chain-of-Thought Reasoning Without Prompting (2024; sampled v2)

[Wang and Zhou, arXiv:2402.10200v2](https://arxiv.org/abs/2402.10200); [exact sampled full-text PDF](https://arxiv.org/pdf/2402.10200v2), §§2–4 and Discussion.

CoT-decoding searches alternative first-token paths to elicit latent chain-of-thought continuations without adding a CoT instruction. On pretrained Mistral-7B/GSM8K it reports 25.1% accuracy, compared with 9.9% greedy, 12.9% self-consistency without a CoT prompt, and 4.9–7.5% for the other decoding baselines in the table. On Mistral-7B it also improves MultiArith from 14.3% to 45.7% and year parity from 35.0% to 66.0%; gains also appear on instruction-tuned models.

**Counterweight and boundary:** it explores multiple paths and so adds inference cost. Gains vary by task/difficulty; on harder synthetic tasks the correct reasoning path is harder to find, and models lose track of state or apply arithmetic in the wrong order. The benchmark set comprises GSM8K, MultiArith, celebrity-year parity, and symbolic/synthetic tasks, mostly on PaLM-2, Mistral-7B, and Gemma-7B at the time. This is a decoding intervention with measured answer gains, not proof that a generated chain is faithful or that gains transfer to open-ended tasks.

## 2025–2026-through-cutoff

### 9. RegexPSPACE: A Benchmark for Evaluating LLM Reasoning on PSPACE-Complete Regex Problems (2025)

[Jin et al., arXiv:2510.09227v1](https://arxiv.org/abs/2510.09227); [exact sampled full-text version](https://arxiv.org/html/2510.09227v1), §§3–6 and limitations.

The benchmark tests regular-expression minimization and equivalence, with correctness checked against formal language definitions. It separately reports equivalence, minimality, output-length ratio, and invalid-answer rates. For example, GPT-OSS-low reaches 84.45% equivalence and 67.36% minimality, while its output-length ratio is 78.48%; the paper's best theoretical ratio is 72.70%. Thus even a strong score on equivalence does not imply a minimum-length construction. Reasoning-tuned models sometimes produce repetitive, overlong outputs or fail to terminate, so answer validity and parse/fail rates matter alongside accuracy.

**Boundary:** dataset construction is limited to relatively small alphabets and regex depths because enumeration/labeling grows double-exponentially. The paper’s own limitations say the current test does not cover the longer expressions needed to probe still more complex minimization. Regex is a precise stress test for algorithmic/formal reasoning, not a general measure of all reasoning.

### 10. A Survey of Secure Retrieval-Augmented Generation (2026; sampled v4)

[Xu et al., arXiv:2604.08304v4](https://arxiv.org/abs/2604.08304); [exact sampled full-text version](https://arxiv.org/html/2604.08304v4), §§1, 5–6 and Limitations.

This survey says it searched and curated 135 works and organizes attacks/defenses by pipeline surface, defense layer, security objective, and attack target. In its 15 “evaluation-primary” studies, it reports that 14 primarily evaluate fixed instances/queries (T1), with only one centrally testing aggregate/cross-query targets (T2). It also finds no unified defense-aware harness spanning all pipeline surfaces, and says attack-success, stance-shift, and certification metrics are not directly rankable across different assumptions.

**Counterweight and boundary:** the review explicitly recognizes multi-surface studies (SafeRAG, OpenRAG-Soc, Rag ’n Roll); its proposed harness is therefore a standardization/integration proposal, not a claim that no paper tests more than one surface. The paper itself labels the review a snapshot through 2026-04-30 and warns that LLM-assisted screening/expert selection and English/full-text constraints can introduce selection error. It offers a protocol specification, not executable harness software.

### 11. MedRouter: Demystifying Knowledge Differences Across Medical LLMs for Routing-Based Reasoning (2026)

[Cao et al., arXiv:2609.33119v1](https://arxiv.org/abs/2609.33119); [exact sampled full-text version](https://arxiv.org/html/2609.33119v1), §§1, 3–5 and Appendix C.

MedRouter routes a question to one or more text/multimodal medical specialist models and lets a separate answer generator integrate their responses. It evaluates eight text and multimodal QA benchmarks, with MedXpertQA held out for OOD evaluation. Across its two answer generators, it reports mean accuracy 45.9% and 46.1%, versus 42.6% for the strongest compared router and 43.6% for selecting the best specialist per dataset. A per-question oracle reaches 64.3%, showing that specialist responses are complementary but selection is far from solved. The reported total test set is 19,034 questions; answer correctness is judged by GPT-5.6-luna against reference answers.

**Counterweight and boundary:** gains are benchmark-specific medical-QA accuracy, not evidence of clinical safety or improved care. LLM-as-judge introduces a measurement dependency; the paper says the system is research-only and needs qualified clinical validation, privacy protection, and harm assessment. It also depends on the specialist pool and is not evaluated on broader medical tasks such as complex information synthesis.

## Cross-paper findings (bounded to this screen sample)

### Finding A: an answer score can hide failure in the reasoning artifact

The 2023 FLD study has a large answer/proof-accuracy gap; the 2025 regex benchmark separates binary equivalence from constructive minimization; and the 2024 CoT-decoding paper reports answer gains but also wrong state tracking and arithmetic steps. Conversely, the 2012 BRUE work evaluates the action recommendation it intends to improve, and the 2018 human–robot study combines elapsed time, task allocation, and participant ratings. Thus “reasoning quality” needs task-matched observables: answer, proof/trace validity, executed behavior, and cost—not a single generic score.

**Testable follow-up:** on tasks with machine-checkable traces, compare answer-only gains with verified-proof/trace gains, across increasing proof depth and held-out templates; charge inference tokens/runtime; include a behavior-only baseline and independent verifier. This hypothesis is weakened if answer accuracy alone reliably predicts valid traces and held-out task success at matched cost.

### Finding B: adaptivity/routing gains are conditional on evaluation boundary

The human–robot study finds faster completion and higher preference for more adaptive simulated robots, yet its task-allocation hypothesis is partly contradicted and the human trajectory is scripted. The multimodal selector reduces failures on filtered MS-GQA tasks but remains well below the oracle; MedRouter improves average QA on eight benchmarks but depends on an LLM judge and is not a clinical evaluation. These studies support complementarity/adaptation as promising, not the claim that routing itself guarantees reliability.

**Testable follow-up:** evaluate routing/adaptation against fixed and oracle policies on held-out task families, reporting end-to-end success (including decomposition failures), service/cost, individual-subtask errors, human preference where relevant, and an independent outcome verifier. This hypothesis is weakened if gains disappear outside the tuned benchmark or after failures and model-call costs are counted.

### Finding C: secure-RAG evaluation scope is an integration target, not an empty field

The 2026 survey's own 135-work map identifies skew toward fixed-instance attack targets and no unified defense-aware cross-surface harness, while also recognizing existing multi-surface papers. The actionable hypothesis is narrower: a shared harness could make cross-query, adaptive, multi-surface attack/defense outcomes more comparable. It would be weakened if a common harness neither changes defense rankings nor exposes new failure propagation or improves reproducibility. This is one survey's snapshot through 2026-04-30, not an exhaustive census of all RAG-security papers.

**Sampling boundary:** this batch adds 11 unread records to the fixed uniform-random frame for the `reasoning_and_agents` retrieval label; together with the earlier 2015 item, that cell contains 12 sampled papers, three in each of four arXiv-submission periods. It is not a prevalence estimate, systematic review, or time-trend analysis. Strata use first arXiv submission date, and each audited version is the exact version recorded in the frame.
