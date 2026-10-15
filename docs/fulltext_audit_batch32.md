# Full-text audit batch 32: reward-progress feedback catches some hacks, not all risks

Updated 2026-10-12. This batch follows one recent random-frame robot-learning paper through a directly cited antecedent. It is a focused citation trace, not a systematic review of reward learning.

## 1. PHIRL: Aligning Learned Rewards with Task Progress for Inverse Reinforcement Learning (arXiv:2609.31855v1; sampled)

[Exact sampled full text](https://arxiv.org/html/2609.31855v1).

### What the paper actually tested

PHIRL trains an AIRL reward from demonstrations, then aligns that reward with human task-progress annotations (temporal change, relative magnitude, state potential, and task completion). Its simulation suite uses Robosuite Lift and PickPlaceCan tasks, each with high-quality and mixed-quality demonstrations; each dataset contains 200 demonstrations from one proficient operator or six operators (50 each). The real-robot task uses a Kinova Gen 3 Lite arm brushing pom-poms from a stuffed animal, with six participants providing ten demonstrations apiece. Four methods are compared: AIRL, preference-only, AIRL plus preferences, and Rank2Reward.

The two simulated reward-hacking cases are concrete: an AIRL-trained policy repeatedly lifts and drops a block, and a PPO policy pokes a can rather than grasping and placing it. PHIRL's progress-shaped reward penalizes the repeated drop and assigns near-zero negative reward to poking, which does not advance task completion. The real-robot endpoint is the number of pom-poms removed over ten episodes; reported totals are PHIRL 73 and online PHIRL 84, versus AIRL 39, AIRL-Pref 62, Pref 58, and Rank2Reward 54. In simulation, performance statistics use 100 evaluation rollouts, but the authors explicitly say the AIRL-based training conditions each use one training run because repeated adversarial training exceeded their budget.

### Limits that change the interpretation

- The “robust to reward hacking” evidence consists of two selected qualitative simulation scenarios, not a blinded or broad attack suite, and the paper reports no physical-robot reward-hacking challenge.
- One training run per condition leaves training-seed variability unmeasured, even though evaluation rollouts are numerous. Those are different sources of uncertainty.
- The real-robot result is a small, task-specific count over ten episodes, not a general safety, contact, or human-disturbance measurement.
- Progress annotations depend on a task that has a finite horizon or recognizable completion status; the authors say cyclic/infinite-horizon tasks such as ant-walk are outside the method's fit.
- The paper's own discussion warns that random annotation sampling may be less data-efficient than deliberately selecting imperfect demonstrations.

## 2. How Much Progress Did I Make? An Unexplored Human Feedback Signal for Teaching Robots (arXiv:2407.06459v2; citation follow-up)

[Exact version-2 full text](https://arxiv.org/html/2407.06459v2).

This antecedent helps separate what is new in PHIRL from what had already been tested. The earlier work studies progress as a human feedback signal, using two online studies and a public-space robot study: 76 crowd participants plus 40 non-expert demonstrators (116 people total). In a Kinova Gen 3 Lite ice-cream-topping task, 34 usable participant traces are reported; 34/40 demonstrations ultimately succeed, while still showing varied, imperfect strategies. On a separate long-horizon tea-steeping task, participants annotated five designed outcomes, including harmless mistakes, unproductive behavior, correction/backtracking, and failure.

The paper reports that progress scores tracked task completion better than scalar ratings in these examples and could distinguish a completed task with a harmless/fixed mistake from an unfinished one. Its discussion explicitly proposes progress as a way to reveal reward hacking because it measures task advancement, while scalar reward can be gamed. This is meaningful prior support for the feedback signal, but it is not a robot-policy safety evaluation: human ratings of recorded trajectories and 40 demonstrations do not establish that a trained controller avoids dangerous behavior. The user study also centers on a small number of tasks and one physical setup, and the authors note that the self-demonstration study lacks ground-truth progress labels for every frame.

## Cross-paper update to candidate finding 053

The new evidence rules out an overly broad version of the idea that embodied studies only measure task completion: this line of work already combines task-progress labels, reward hacking examples, and a physical task endpoint. It also sharpens the testable gap. The evidence progresses from (a) human judgment that progress describes task completion, to (b) two simulated reward-hacking demonstrations where progress shaping improves the reward response, but it does not yet demonstrate a repeatable, adversarially broad physical safety result. The 2025 progress study and 2026 PHIRL paper share authors, so this is a research-lineage extension, not independent replication.

**Updated falsifiable question:** across independently authored robot-learning systems, do progress/rubric feedback signals predict and prevent reward-hacking behavior on held-out attack patterns and real hardware, while preserving task completion? A preregistered test should hold out attack templates, use multiple training seeds, report external task success and harm/intervention outcomes separately, and include human-rated and automatically generated feedback. The opportunity weakens if existing independent studies already show stable, replicated physical robustness across such conditions.

## Sampling status

This batch adds one random-frame key and two citation-follow-up sources. The `robotics_embodied_ai` uniform-random cell now has seven of twelve keys audited or dispositioned (the remainder is five; prior coverage includes two earlier keys plus the four in batch 31 and PHIRL here). Findings remain exploratory and are not prevalence estimates for robotics or for the 198,690-record candidate pool.

## 3. Independent counterevidence: ReWiND tests reward ranking on failures and real-robot learning (arXiv:2505.10911v1; citation follow-up)

[Exact full text](https://arxiv.org/html/2505.10911v1).

ReWiND is from an independent author team and goes beyond two illustrative hacks. On 17 visually related but motion-distinct MetaWorld tasks, its reward model is tested on successful demonstrations and on policy rollouts grouped as failure, near-success, and success; each task has two trajectories per outcome class. The paper measures reward-order alignment, reward differences, and input robustness. It also trains policies online for eight downstream simulation tasks and reports an IQM success rate of 79% at 100k environment steps.

On real hardware, the paper uses two low-cost Koch bimanual arms and five task conditions. After one hour of online learning, mean success across the five tasks rises from 12% for the pretrained policy to 68% with ReWiND. This is important counterevidence to any claim that reward-learning work has not studied failures, generalization, or physical task outcomes.

However, this is not a direct disproof of the narrower PHIRL opportunity. Its main failure test is reward-ordering over selected rollout categories, not a held-out adversarial exploit suite with harm outcomes. The online real-robot setup assumes a human supervisor for resets and success detection. Authors report that reward alignment fails on a bimanual dish-scrubbing example, plausibly because Open-X lacks bimanual data and the sponge is occluded. They also state that a wrong but confident initial policy can remain hard to unlearn. Thus, ReWiND supplies stronger and independent robustness evidence, while leaving a matched, repeated physical exploit-and-safety protocol open for verification. These are different methods and tasks; the numerical results must not be pooled with PHIRL.

### Revised interpretation

The candidate question is no longer “do progress-based robot rewards get tested against failures?” Independent work already evaluates failure/near-success/success reward ordering and shows real-robot gains. The narrower falsifiable question is whether reward models that score well on such categorized rollouts also resist deliberately constructed reward exploits on held-out tasks, across multiple training seeds, without increasing physical harm or interventions. A preregistered common evaluation should compare PHIRL-, ReWiND-, preference-, and baseline reward models under matched task data and compute budgets. It should score reward-ranking accuracy, exploit rate, task success, contact/near-miss events, human interventions, and reset/success-detection dependence separately. If existing independent studies already cover held-out exploits with replicated physical safety outcomes, the gap is substantially weakened.

This citation trace now includes two distinct research lineages (PHIRL/progress feedback and ReWiND), but remains a small, purposive review rather than a systematic review of reward learning.
