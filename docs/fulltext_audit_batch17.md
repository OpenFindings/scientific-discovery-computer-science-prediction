# Full-text audit batch 17: agent reliability/security across eras

Updated 2026-10-11. Three eligible fixed-frame uniform-random papers were reviewed in depth from the 2015–2019, 2020–2024, and 2025–2026 periods. The oldest selected item in this topic cell, arXiv:1011.3096, is recorded below as a retrieval/scope issue and is **not counted as a full-text audit**: arXiv metadata and its abstract identify a service-trust/authentication model, but the accessible arXiv/HTML endpoint did not expose the PDF contents during this pass. Do not infer that the old trust method is ineffective or that the evidence sequence below is a continuous research lineage.

## 1. Oldest sampled item still awaiting readable full text

[Liu et al., “A Trust Model Based on Service Classification in Mobile Services”](https://arxiv.org/abs/1011.3096), submitted 2010-11-13; metadata lists the GreenCom/CPSCom 2010 venue DOI.

The abstract describes an intermediary trust operator, service-sensitivity classification, three trust tiers, and authentication history/penalties. This is enough to identify the topic and likely retrieval relevance, but **not enough to adjudicate equations, evaluation, assumptions, or limitations**. The official abstract page and its PDF link were checked; a complete readable paper body was not obtained here. It remains queued, not “reviewed.”

## 2. Attack-defence trees as asynchronous multi-agent systems (2019)

[Arias et al., “Hackers vs. Security: Attack-Defence Trees as Asynchronous Multi-Agent Systems”](https://arxiv.org/html/1906.05283v1), arXiv v1; published 2019.

The paper gives a formal extension (EAMAS) that maps attack-defence-tree nodes, timing/cost attributes, and attacker/defender coalitions into asynchronous agent models. It proves the transformation correct for its stated semantics and checks three literature-derived case studies with Uppaal/IMITATOR. Agent coalition can change calculated attack time/cost; e.g. in the IoT-device example, one attacker needs 784 minutes for one minimum-time path while different agents can parallelize actions and reduce it to 694 minutes.

**Countercondition:** Exact EAMAS verification is not free: the authors report approximately 3× longer computation than the compared Uppaal encoding in the stated setup, and state-space growth harms quantitative queries. The evaluation verifies translations on three constructed/prior-literature models; it is not an empirical measurement of real adversaries, defenders, or incident outcomes. The paper itself identifies automatic tool generation and further reduction techniques as future work.

**Audit judgment:** Strong formal-method evidence for model expressiveness and coalition-sensitive analysis under assumptions, not evidence that a real security operation becomes safer or faster.

## 3. Explaining agent behavior with LLMs (2023)

[Zhang et al., “Explaining Agent Behavior with Large Language Models”](https://arxiv.org/html/2309.10346v1), arXiv v1.

The pipeline distills the policy into a decision-tree surrogate, extracts a local decision path, and asks GPT-4 to verbalize that behavior representation. In a 32-participant study, participants preferred these explanations to template-generated explanations; they did not prefer human-written explanations over the system's. A follow-up interaction study had only five participants. Hallucinations were assessed on 30 generated explanations (10 each for optimal, suboptimal, and fixed policies), and the proposed behavior representation yielded fewer measured hallucinations than the two tested alternatives.

**Counterconditions and scope:** The authors explicitly say the decision tree is an approximation of the policy: an explanation may faithfully explain a slightly wrong surrogate. The preference evidence comes from a small 2D urban-search-and-rescue environment and one LLM (GPT-4); “preferred/helpful” is not the same as causal faithfulness, calibrated uncertainty, or safer decisions. The hallucination comparison uses 30 generated examples, not broad deployment evaluation. Notably, removing the behavior representation sometimes caused fewer factually wrong claims because the LLM became more conservative, but also less informative.

**Audit judgment:** Evidence for perceived helpfulness and a promising grounding intervention in a bounded task; not a guarantee that the language explanation reveals the policy's actual internal reasoning.

## 4. Cybersecurity refusals in AI agents (2026)

[Jones et al., “A New Framework for Cybersecurity Refusals in AI Agents”](https://arxiv.org/html/2606.02644v1), arXiv v1 (submitted 2026-05-31).

The paper proposes a refusal-boundary framework and evaluates eight models. Its benchmark has 29 web-vulnerability challenges in four sensitive domains. It separates (a) local/dummy or proxied vulnerable environments used to measure proficiency/refusal, (b) higher-fidelity proxy conditions, and (c) nine remote production-site reconnaissance tasks where agents may create a test plan but are **not allowed to exploit**. In medium proxy mode it reports six of eight models with refusal rates ≤5%; GPT-5.2 is reported at 62% (13 of those refusals preceded by awareness of production context). In hard mode, only 18 of 800 trajectories show the desired combined behavior, with five trials per model/challenge. The authors use an LLM judge for binary capability grading.

**Important qualifications:** These are snapshot results for a named model set, scaffold, prompt taxonomy, 29 selected tasks, and five-trial design—not a durable claim about all current/future agents. Real-site tasks measure refusal and awareness around reconnaissance/planning, not whether an agent would successfully exploit real infrastructure. The authors acknowledge the boundary problem is normative and the red-zone list is not exhaustive; they also frame real-site planning as a risk proxy. Model behavior can be affected by whether the target is presented as a localhost, proxy, or production URL. Report the mode-specific result, not a single context-free “agent safety” number.

**Audit judgment:** A valuable benchmark proposal and concrete risk signal, but the headline depends on carefully distinguished conditions and a small number of repeated trials.

## Cross-period synthesis and falsifiable next test

The sampled label `agent_reliability_security` combines different targets: service trust/authentication (2010 item, abstract only), formal attack/defence model checking (2019), human-facing explanations for rescue-agent policies (2023), and refusal/awareness in cybersecurity agents (2026). These are not successive versions of one technique and cannot be scored on a shared “reliability” axis. The three fully read works each expose a different boundary: formal results depend on model semantics and incur state-space cost; explanation quality depends on surrogate fidelity and human preference does not prove faithfulness; refusal rates depend sharply on task framing, environment mode, and model/scaffold.

**Falsifiable next study:** For current security-capable agents, preregister a crossed evaluation over (1) benign/authorized versus harmful intent, (2) localhost toy vs realistic proxy vs non-invasive real-site planning, and (3) explicit authorization/context cues. Measure capability, refusal appropriateness, situational awareness, calibration, and harmful actionable detail separately; blind-grade with independently adjudicated rubric plus adversarial human review. The main claim is weakened if refusal/awareness remain stable across contexts and task families, and strengthened if small presentation changes reliably flip behavior. Evaluate explanation faithfulness to agent action policies as a separate experiment with surrogate fidelity reported, not as a proxy for refusal safety.
