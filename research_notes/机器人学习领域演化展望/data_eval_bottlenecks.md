# Robot learning: data, evaluation and bottlenecks (as of Oct 2026)

Evidence-level tags used throughout:
- **[MEASURED]**: a number reported in a peer-reviewed or arXiv paper with its method described.
- **[COMPANY CLAIM]**: stated on a company blog or press release, with no independent audit.
- **[PRESS]**: journalism, often from anonymous or unnamed sources.
- **[OPINION]**: an argument or estimate from a named person.

All arXiv numbers were read from the arXiv abstract or HTML full text, or from alphaXiv's paper report, at the URLs given.

---

## Q1. Dataset sizes (trajectories, hours, embodiments, tasks) and comparison with language and vision data

### Takeaway
Open real-robot datasets grew roughly tenfold between 2023 and 2025:
- BridgeData V2: about 60k trajectories.
- DROID: 76k trajectories, 350 h.
- Open X-Embodiment (OXE): more than 1M trajectories, pooled from 60 datasets.
- AgiBot World: more than 1M trajectories, about 2,976 h.

Company corpora, all self-reported, are now 1–2 orders of magnitude larger than the open ones:
- Physical Intelligence (PI): more than 10k h.
- Generalist AI (GEN-0): more than 270k h, growing about 10k h per week.

Even so, robot data is still several orders of magnitude smaller than the corpora behind language models (more than 15T tokens for Llama 3) and vision models (5.85B image-text pairs in LAION-5B). The largest growth in 2026 is in egocentric human data (about 1k–20k+ h), not in robot teleoperation.

### Cited Findings
**Open X-Embodiment (2023)** [MEASURED]
- Pools 60 existing datasets from 34 labs at 21 institutions. Contains 1M+ real-robot trajectories across 22 embodiments, covering 527 skills and 160,266 tasks — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864)
- The data comes in many formats and is standardised to RLDS — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864)
- Conflicting counts: the AgiBot World paper describes OXE as "over 1.4 million trajectories" and "approximately 2000 hours", which differs from the OXE paper's own "1M+" — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)
- The OXE paper says that before OXE, the largest robotics datasets held 5–18 million observations, against billions of data points in NLP and computer vision — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864)

**DROID (2024)** [MEASURED]
- Size: 76k successful demonstration trajectories, 350 h of interaction.
- Diversity: 564 scenes in 52 buildings, 86 tasks or verbs, 1,417 camera viewpoints.
- Collection: 50 collectors at 13 institutions over 12 months, on one standardised platform (Franka Panda arm, Robotiq gripper, 3 ZED cameras, Oculus Quest 2 teleoperation). The platform was replicated 18 times.
- Licence: CC-BY 4.0.
- Source: [arXiv 2403.12945](https://arxiv.org/abs/2403.12945)

**BridgeData V2 (2023)** [MEASURED]
- 60,096 trajectories in 24 environments on a low-cost WidowX robot — [arXiv 2308.12952](https://arxiv.org/abs/2308.12952)
- AgiBot's comparison table lists the original BridgeData at 7.2k trajectories, RoboTurk at 2.1k and RT-1 at 130k — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)

**AgiBot World Colosseo (Mar 2025)** [MEASURED]
- Size: over 1M trajectories, 2,976.4 h, 217 tasks, 87 skills, 106 scenes, more than 3,000 objects.
- Hardware: about 100 AgiBot G1 dual-arm robots on mobile bases, with optional dexterous hands and visuo-tactile sensors.
- Collection site: a 4,000 m² facility that recreates 5 domains (domestic, retail, industrial, restaurant, office).
- Episode length: trajectories typically last about 30 s, and some exceed 2 min.
- Failure-recovery data: about 1% of the data, with annotations.
- Licence: CC BY-NC-SA 4.0.
- Source: [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)

**Other 2024–2026 open robot datasets** [MEASURED]
- RoboMIND (Dec 2024): 107k trajectories, 479 tasks, 96 object classes, 4 embodiments (Franka, UR5e, AgileX dual-arm, a humanoid with dexterous hands), plus 5k annotated failure demonstrations and an Isaac Sim digital twin — [arXiv 2412.13877](https://arxiv.org/abs/2412.13877)
- Galaxea Open-World (Sep 2025): 500 h and 100k trajectories, 150+ tasks, 50 real scenes, one embodiment, with subtask-level language annotations — [arXiv 2509.00576](https://arxiv.org/abs/2509.00576)
- RoboCOIN (Nov 2025, BAAI): 180k+ bimanual demonstrations from 15 robot platforms, 16 environments, 421 tasks — [arXiv 2511.17441](https://arxiv.org/abs/2511.17441)
- PRISM (Aug 2026): an industrial contact-rich dataset, 5,000+ trajectories and 45 h, with force/torque and tactile sensing. It shows that precision-assembly data is still small — [arXiv 2608.17962](https://arxiv.org/abs/2608.17962)
- RoboTacDex (Jun 2026): 6k trajectories on a Unitree G1 with tactile sensing, 19 tasks — [arXiv 2606.31836](https://arxiv.org/abs/2606.31836)

**Human and handheld-interface datasets (2025–2026)** [MEASURED]
- EgoDex (Apple, May 2025): 829 h of Apple Vision Pro egocentric video with 3D hand and finger tracking, 194 tasks — [arXiv 2505.11709](https://arxiv.org/abs/2505.11709)
- EgoVerse (Apr 2026): 1,362 h (80k episodes), 1,965 tasks, 240 scenes, 2,087 demonstrators — [arXiv 2604.07607](https://arxiv.org/abs/2604.07607)
- EgoScale (NVIDIA, Feb 2026): trains on more than 20,854 h of action-labelled egocentric human video, which it says is "more than 20 times larger than prior efforts" — [arXiv 2602.16710](https://arxiv.org/abs/2602.16710)
- TouchScale (Oct 2026): 500 h of egocentric human video with full-hand tactile data, about 2K task descriptions — [arXiv 2610.10288](https://arxiv.org/abs/2610.10288)
- TacClaw-Infinity (Oct 2026): a tactile UMI-style handheld gripper. The dataset has more than 10,000 h, 1M episodes and 1B frames across more than 1,000 task types — [arXiv 2610.20320](https://arxiv.org/abs/2610.20320)
- Ego4D (2021), the general reference corpus: 3,670 h from 931 camera wearers in 74 locations across 9 countries. EgoDex notes that Ego4D lacks native hand-pose annotations and does not focus on manipulation — [arXiv 2110.07058](https://arxiv.org/abs/2110.07058); [arXiv 2505.11709](https://arxiv.org/abs/2505.11709)

**Company data efforts**
- Physical Intelligence: base checkpoints are "pre-trained on 10k+ hours of robot data" [COMPANY CLAIM / paper] — [openpi README](https://github.com/Physical-Intelligence/openpi); the π0 paper says "over 10,000 hours of robot" data and covers 8 distinct robots in its own dexterous dataset — [arXiv 2410.24164](https://arxiv.org/abs/2410.24164); [PI π0 blog](https://www.pi.website/blog/pi0)
- In the π0 mixture, the OXE subset ("OXE Magic Soup") makes up 9.1% of training data, and the paper also uses 903M timesteps of the company's own data — [arXiv 2410.24164](https://arxiv.org/abs/2410.24164)
- In the π0.5 ablation, the mobile-manipulation data collected on the evaluation robots is "about 400 hours" — [PI π0.5 blog](https://www.pi.website/blog/pi05)
- Generalist AI GEN-0 (Nov 2025) [COMPANY CLAIM]:
  - Pretraining corpus of "over 270,000 hours of real-world diverse manipulation data, growing at a rate of 10,000 hours a week and accelerating".
  - Collected "in 1,000s of homes, warehouses, and workplaces worldwide" through "1,000s of data collection devices and robots" and "multiple data foundry partners".
  - "Dozens of Petabytes" of data.
  - Source: [Generalist GEN-0 blog](https://generalistai.com/blog/nov-04-2025-GEN-0)
- Figure Helix (Feb 2025) [COMPANY CLAIM]: "~500 hours" of multi-robot, multi-operator teleoperated data, which Figure calls "<5%" of previous VLA datasets. The model has 7B parameters in System 2 and 80M in System 1 — [Figure Helix](https://www.figure.ai/news/helix)
- Figure Project Go-Big [COMPANY CLAIM]:
  - Navigation was trained on "100% egocentric human video" collected in Brookfield homes. No hour count is disclosed.
  - The Brookfield partnership cites "over 100,000 residential units", "500 million square feet" of office space and "160 million square feet" of logistics space.
  - Source: [Figure Go-Big](https://www.figure.ai/news/project-go-big)
- Tesla Optimus [PRESS]: Business Insider (via Sherwood, 25 Aug 2025) reported that Tesla moved Optimus training mainly to video recordings of human workers, away from motion-capture suits and VR teleoperation, after the head of Optimus left in June 2025. No Tesla data volumes are public — [Sherwood News](https://www.sherwood.news/tech/teslas-robots-get-the-same-treatment-as-its-cars-video-training/)
- TRI Large Behavior Models: about 1,700 h of robot demonstrations, covering more than 500 internally collected tasks plus public data [MEASURED] — [arXiv 2507.05331](https://arxiv.org/abs/2507.05331)
- NVIDIA GR00T N1 used 88 h of in-house teleoperation data, augmented with video-generated and simulated data (details in Q2) — [arXiv 2503.14734](https://arxiv.org/abs/2503.14734)

**Comparison with language and vision corpora**
- Llama 3 was pretrained on "over 15T tokens" [COMPANY CLAIM] — [Meta Llama 3 blog](https://ai.meta.com/blog/meta-llama-3/)
- LAION-5B contains 5.85B CLIP-filtered image-text pairs — [LAION blog](https://laion.ai/blog/laion-5b/)
- V-JEPA 2 pretrains on more than 1M hours of internet video. Its robot world model then uses less than 62 h of DROID video — [arXiv 2506.09985](https://arxiv.org/abs/2506.09985)
- Ken Goldberg's "100,000-year data gap" [OPINION]: he estimates that VLM training data is equivalent to about 100,000 years of experience. A Penn seminar abstract describing his argument says the largest robot dataset is "on the order of 1 year" (8,760 h). Published as Science Robotics pieces in Aug 2025 — [Penn seminar](https://events.seas.upenn.edu/event/cis-seminar-good-old-fashioned-engineering-can-close-the-100000-year-data-gap-in-robotics/); [Berkeley news](https://news.berkeley.edu/?p=134910)

### Inferences
- Approximate scale ladder: academic open sets are about 10²–10³ h; AgiBot about 3×10³ h; PI about 10⁴ h; open egocentric human data about 10³–2×10⁴ h; GEN-0 claims about 2.7×10⁵ h. GEN-0's 270k h already exceeds Goldberg's "~1 year" (8,760 h) by about 30×, if the claim is accurate. That would put the "100,000-year" gap nearer 10³–10⁴× for the leading private corpus, but the 270k figure is unaudited.
- Counting conventions differ: trajectories, hours, episodes, frames and "datasets per day". Cross-dataset comparison has roughly 2× uncertainty. For example, OXE is reported as both 1M+ and 1.4M trajectories.
- Most 2026 growth in hours comes from human and handheld data (EgoScale, TacClaw, EgoVerse), not from robot teleoperation. This matters for forecasts: hour counts may rise quickly while the action-labelled, embodiment-matched share grows slowly.

### Gaps
- No public, verified hour counts for Tesla Optimus, Figure (beyond the 500 h for Helix in Feb 2025), 1X, Google DeepMind Gemini Robotics or Agility. I found nothing reliable.
- GEN-0's 270k h is not independently verified. How much of it is robot-embodied and how much is human handheld data is not stated precisely. A 36kr report describes it as human operation video; I treat that as unverified.
- No consistent token-equivalent conversion between robot hours and LLM tokens. Goldberg's conversion is his own.

---

## Q2. Data sources and their trade-offs

### Takeaway
There are four main sources:
- **Teleoperation** (ALOHA, VR, motion capture): the best match to the robot's body, but expensive and slow. Systems cost about $20k–32k per station, data is often throughput-limited, and it is tied to one embodiment.
- **Handheld interfaces such as UMI**: cheap and portable, and they record in the wild without a robot. Constraints include SLAM tracking failures (about 10% of demonstrations discarded) and a remaining embodiment mismatch.
- **Simulation and generated data**: very cheap per hour (for GR00T, 780k trajectories, equal to 6,500 h, were generated in 11 h). The sim-to-real gap remains, and generated video costs a lot of compute.
- **Human egocentric video**: the most scalable source. In 2026 studies it increasingly matches or beats robot data for pretraining, but it still needs some aligned robot data afterwards.

China is building state-backed teleoperation "data factories" at scale.

### Cited Findings
**Teleoperation**
- ALOHA "costs <$20k with off-the-shelf robots and 3D printed components". ACT learned 6 fine tasks at 80–90% success from "only 10 minutes worth of demonstrations" [MEASURED] — [arXiv 2304.13705](https://arxiv.org/abs/2304.13705)
- Mobile ALOHA was built "with a $32k budget" including onboard power and compute. With 50 demonstrations per task, co-training with static ALOHA data raised success "by up to 90%" — [arXiv 2401.02117](https://arxiv.org/abs/2401.02117)
- DROID used VR teleoperation (Oculus Quest 2). Collectors gathered about 100 trajectories (about 20 min) per scene, which shows how throughput is limited by moving the robot between scenes — [arXiv 2403.12945](https://arxiv.org/abs/2403.12945)
- AgiBot used VR teleoperation and whole-body motion capture, with a human-in-the-loop quality check. A smaller human-verified set gave a 0.18 higher completion score than a larger unverified set on "Wipe Table" — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)
- A former Tesla data collector described motion-capture sessions as partly staged ("we're controlling the bots so it looks more fluid") [PRESS, anonymous source] — [search result summarising Business Insider / Futurism reporting](https://www.notateslaapp.com/news/2761/teslas-optimus-is-now-learning-by-watching-first-person-today-third-person-tomorrow-video)

**Handheld grippers (UMI and successors)**
- UMI uses hand-held grippers for "portable, low-cost" in-the-wild demonstrations. Policies transfer across robot platforms through latency matching and relative-trajectory actions — [arXiv 2402.10329](https://arxiv.org/abs/2402.10329)
- In a UMI-based scaling study, about 90% of demonstrations were valid after SLAM filtering. Constraints include the need for visually rich environments and objects small enough not to block the camera — [arXiv 2410.18647](https://arxiv.org/abs/2410.18647)
- Chinese firms recruit "Universal Manipulation Interface data collectors" for "around 20 yuan (HK$22) an hour or 200 yuan a day" [PRESS] — [The Standard, 19 Aug 2026](https://www.thestandard.com.hk/china/article/340377/Chinas-embodied-AI-boom-fuels-demand-for-human-collected-training-data)
- TacClaw-Infinity adds fingertip tactile sensing to a UMI-style device and reaches more than 10k h — [arXiv 2610.20320](https://arxiv.org/abs/2610.20320)

**Simulation and synthetic data**
- GR00T N1 (NVIDIA) [MEASURED]:
  - "780,000 simulation trajectories — equivalent to 6,500 hours, or nine continuous months, of human demonstration data — in just 11 hours".
  - Also generated about 827 h of "neural trajectories" (about 300k) from 88 h of real teleoperation data using video-generation models, about a 10× augmentation. This cost about 105k L40 GPU-hours, at about 2 minutes per second of video.
  - Source: [arXiv 2503.14734](https://arxiv.org/abs/2503.14734)
- GraspVLA trained on SynGrasp-1B, a billion-frame synthetic grasping dataset with photorealistic rendering and domain randomisation, and reports zero-shot real-world grasping. The scope is grasping only — [arXiv 2505.03233](https://arxiv.org/abs/2505.03233)
- RoboMIND ships an Isaac Sim digital twin for low-cost extra data and evaluation — [arXiv 2412.13877](https://arxiv.org/abs/2412.13877)
- LIBERO-Safety generated 19,664 collision-free demonstrations with a keypose-driven pipeline "to overcome the scalability bottlenecks of human teleoperation" — [arXiv 2606.23686](https://arxiv.org/abs/2606.23686)

**Human video and video pretraining**
- EgoScale finds "a log linear scaling law between human data scale and validation loss". The loss correlates with real-robot performance, and success is 54% higher than a no-pretraining baseline on a 22-DoF hand — [arXiv 2602.16710](https://arxiv.org/abs/2602.16710)
- HumanScale (Jun 2026) reports that with the same amount of pretraining data, egocentric pretraining gives 24% lower validation loss on real-robot action prediction than teleoperated robot data. It also gives 52.5% (in-distribution) and 90% (OOD) higher success rates. This needs careful filtering and labelling, plus a small amount of robot data for alignment — [arXiv 2606.20521](https://arxiv.org/abs/2606.20521)
- Physical Intelligence and Georgia Tech find that human-to-robot transfer "emerges once the VLA is pre-trained on sufficient scenes, tasks, and embodiments". It can "nearly double" performance on settings seen only in human data — [arXiv 2512.22414](https://arxiv.org/abs/2512.22414)
- EgoVerse: "policy performance generally improves with increased human data, but … effective scaling depends on alignment between human data and robot learning objectives" — [arXiv 2604.07607](https://arxiv.org/abs/2604.07607)
- AgiBot's GO-1 learns latent actions from unlabelled heterogeneous video, including human video, with a VQ-VAE latent action model — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)
- Tesla team members reportedly said "teleoperation doesn't scale" while video does [PRESS] — [Not a Tesla App](https://www.notateslaapp.com/news/2761/teslas-optimus-is-now-learning-by-watching-first-person-today-third-person-tomorrow-video); Sherwood adds that video "is not as robust as more expensive methods" — [Sherwood](https://www.sherwood.news/tech/teslas-robots-get-the-same-treatment-as-its-cars-video-training/)

**Data-collection "factories" (China)**
- RealMan's Beijing Humanoid Robotics Data Training Center (Sep 2025): 3,000 m², 108 robots deployed, 10 real-world scenario environments. Claims "over one million high-quality data points annually" [COMPANY CLAIM] — [Robotics 24/7](https://www.robotics247.com/article/realman_robotics_launches_humanoid_robotics_data_training_center_in_beijing/supply_chain)
- The Standard (Aug 2026) [PRESS]:
  - "At least 30 data-collection facilities" existed by end-2025 in cities including Beijing, Tianjin, Shanghai, Guangzhou, Zhengzhou, Wuxi and Jinan.
  - Each robot is paired with a teleoperator who records joint angles and grip force.
  - Centre manager Zhu Kai says one basic skill needs "thousands of sets of data".
  - Zhu Kai also says China shipped 23,000 humanoids in H1 2026 but fewer than 5% can do practical factory work, mainly for lack of data. This is a manager's claim.
  - Source: [The Standard](https://www.thestandard.com.hk/china/article/340377/Chinas-embodied-AI-boom-fuels-demand-for-human-collected-training-data)
- A different count: Interesting Engineering, citing Chinese media, reports "more than 40 state-backed robot data collection centres" by end-2025, 24 of them operating. A Shanghai Zhangjiang centre of 5,000 m² hosts more than 100 robot models from more than a dozen companies [PRESS, aggregated] — [LetsDataScience aggregation](https://letsdatascience.com/news/china-opens-training-centers-to-ready-humanoids-07b6a7b9). This conflicts with The Standard's "at least 30".
- A search summary of Xinhua reporting says a Sichuan (Zigong) centre targets about 15,000 datasets per day and about 3 million per year. I could not open the primary page, so this is unverified — [Fujian gov / Xinhua mirror](https://www.fujian.gov.cn/english/business/news/202605/t20260528_7153552.htm)
- AgiBot's own 4,000 m² facility with about 100 robots is the best-documented "factory", with output published as a dataset — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)

**Cost estimates** [OPINION]
- A Substack commentator estimated that about 250k h of teleoperation at about $20/h would cost about $5M. That is the commentator's estimate, not Generalist's — [theahura Substack](https://theahura.substack.com/p/tech-things-robotics-has-its-gpt2)

### Inferences
- Approximate cost per hour: the Chinese UMI collector wage is ¥20/h, about US$3/h. Teleoperation stations cost $20–32k each plus operator time. Simulation trajectories are almost free at the margin. Generated video costs about 127 L40 GPU-hours per hour of video (105k GPU-hours / 827 h). This cost order favours human, handheld and simulated data for scaling, with teleoperation kept for alignment and post-training.
- The field moved in 2025–2026 from "teleoperation is the dataset" to a layered recipe: pretrain on human video and handheld data, mid-train on aligned robot data, then post-train with RL or autonomous experience. Tesla, Figure (Go-Big), NVIDIA (EgoScale), PI (human-to-robot) and Generalist all point in this direction.
- Chinese data factories produce volume, but quality and diversity are unclear. A facility with recreated scenes has fewer real scenes than in-the-wild collection: AgiBot has 106 scenes, DROID 564.

### Gaps
- No audited figures for hours per year from Chinese centres. "Datasets" and "data points" are undefined units.
- No public cost per hour for teleoperation at company scale, such as PI or Figure.
- Few controlled head-to-head comparisons of sim data against real data per dollar for dexterous, contact-rich tasks.

---

## Q3. Scaling-law evidence for robot data

### Takeaway
Quantitative evidence exists, but the studies are small and differ in setup.
- Within one task, generalisation follows approximate **power laws in the number of environments and objects**. The raw number of demonstrations saturates at about 50 per environment-object pair.
- Across tasks, pretraining on more and more diverse data predictably improves downstream success: AgiBot found r = 0.97 for a power-law fit; TRI LBM, PI π0.5 and GEN-0 report similar trends.
- Human egocentric data shows log-linear loss scaling (EgoScale).
- Cross-embodiment gains are real but depend on model capacity.
- Generalist AI claims a "phase transition" at about 7B parameters.

None of these are compute-optimal laws of the kind Chinchilla established for language models, and most use small evaluation sets.

### Cited Findings
**Single-task scaling: Lin et al., ICLR 2025** [MEASURED]
- Generalisation follows an approximate power law in the number of training environments, objects or environment-object pairs (Pearson r 0.942–0.991). More demonstrations with environments and objects held fixed did not follow a clear power law and plateaued.
- 32 environment-object pairs with about 50 demonstrations each reached about 90% success on unseen environments and objects for 4 tasks. The data took "one afternoon for two tasks with four data collectors".
- More than 40k UMI demonstrations and more than 15k real rollouts.
- Scaling the visual encoder helped. Scaling the diffusion U-Net did not.
- Source: [arXiv 2410.18647](https://arxiv.org/abs/2410.18647)

**Cross-embodiment (OXE)** [MEASURED]
- RT-1-X beat the original methods on 4 of 5 small datasets.
- On data-rich domains, RT-1-X (35M parameters) *underperformed* the single-robot RT-1. RT-2-X (55B) beat both.
- RT-2-X was about 3× better than RT-2 on emergent skills transferred from other robots' data.
- Removing Bridge data reduced that gain.
- Web pretraining was "critical".
- The evaluation used 3,600 trials on 6 robots.
- Source: [arXiv 2310.08864](https://arxiv.org/abs/2310.08864)

**Dataset-level effects**
- DROID co-training raised success by 20% on average over in-domain-only training and beat co-training on OXE. Scene diversity mattered more than size: a diverse subset beat a 20-scene subset of the same size — [arXiv 2403.12945](https://arxiv.org/abs/2403.12945)
- AgiBot World:
  - Pretraining on AgiBot World instead of OXE gave +30% success in-domain and +29% OOD for RDT.
  - GO-1 performance followed a power law in data size from 9.2k to 1M trajectories (r = 0.97).
  - The 236 h "alpha" subset beat OXE (about 2,000 h).
  - Source: [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)
- TRI LBM: performance "predictably increases as pretraining scale and diversity grows". On new tasks, LBMs "require a fraction of the data" of single-task baselines. Based on about 1,700 h of data and 1,800 real trials — [arXiv 2507.05331](https://arxiv.org/abs/2507.05331)
- π0.5 [COMPANY CLAIM / blog]:
  - Generalisation to new homes "steadily increases with the number of distinct environments". After about 100 training environments it approaches a baseline trained on the test environment itself.
  - Ablation success rates (OOD): full model 94%, without web data 74%, without cross-embodiment data 49%, without multi-environment data 31%.
  - Source: [PI π0.5 blog](https://www.pi.website/blog/pi05)

**Model size and pretraining scale (GEN-0, Generalist AI)** [COMPANY CLAIM]
- "Phase transition at 7B where smaller models exhibit ossification". 1B models "struggle to absorb" diverse data; 6B and 7B models improve.
- Downstream validation error follows L(D) = (D_c/D)^α_D in pretraining data size.
- More pretraining improves success with only 5.6 h of task data. Peak success reaches "up to 99%" with 550+ h of post-training data.
- Source: [Generalist GEN-0 blog](https://generalistai.com/blog/nov-04-2025-GEN-0)

**Human data scaling**
- EgoScale: log-linear relation between human data hours (up to 20,854 h) and validation loss, which correlates with real-robot success — [arXiv 2602.16710](https://arxiv.org/abs/2602.16710)
- TouchScale: with sensor and protocol held fixed, tactile prediction and robot success "show an overall upward trend" with more data. Robot success on four contact-rich tasks rose from 22.5% to 57.5% — [arXiv 2610.10288](https://arxiv.org/abs/2610.10288)

**Controlled cross-embodiment study (ZETA, Sep 2026)** [MEASURED]
- Diversity of source embodiments adds about 18 percentage points to zero-shot transfer. End-effector action representation adds about 15 pp. Auxiliary co-training adds about 7 pp.
- Adding 5% target-embodiment data during pretraining adds 13.4 pp.
- The authors say "strict" and "pretrain-exposed" zero-shot results should be reported separately.
- Source: [arXiv 2609.02546](https://arxiv.org/abs/2609.02546)

**BridgeData V2**: performance "improves with more data and higher capacity models" — [arXiv 2308.12952](https://arxiv.org/abs/2308.12952)

### Inferences
- The most consistent result is that **diversity (environments, scenes, embodiments) scales better than repetition**. This holds in Lin et al., DROID, π0.5 and ZETA. Forecasts should track the number of distinct environments, not raw hours.
- Model capacity interacts with data heterogeneity: the 35M-parameter RT-1-X underfit in OXE, and GEN-0 reports ossification at 1B. Larger corpora are likely to need VLA backbones of 7B parameters or more, which makes inference latency worse (see Q5).
- Every "scaling law" reported so far uses proxy losses (validation MSE or next-action error) or small real evaluation suites. Correlation between loss and success is claimed (EgoScale, GEN-0) but not independently reproduced.

### Gaps
- No independent replication of GEN-0's scaling or phase-transition claims.
- No compute-optimal (Chinchilla-style) allocation results for robot data published with code and data.
- Scaling for long-horizon reliability, for example how mean time between failures changes with data, is largely unmeasured.

---

## Q4. Evaluation: real-world arenas, simulation benchmarks and reproducibility problems

### Takeaway
Real-world evaluation is moving towards distributed, double-blind, pairwise "arenas" (RoboArena) and toward large-N blind A/B trials with statistics (TRI LBM). Simulation benchmarks are either saturated (LIBERO is near 100%) or shown to be gameable:
- A 0.09B probe with no language encoder matches state of the art on LIBERO.
- Most reported LIBERO gains are not statistically significant.
- Benchmark bugs have reversed rankings.

In 2026 many "LIBERO-X" robustness variants appeared. Hardware or mid-task perturbations cut success by about 11–42 percentage points.

### Cited Findings
**Real-world arenas**
- RoboArena (Jun 2025):
  - Method: crowd-sourced, double-blind pairwise comparisons on the DROID platform. Evaluators choose their own tasks and scenes, and rankings come from a task-aware Bradley-Terry model.
  - Scale: more than 600 pairwise episodes (4,284 rollouts), 7 policies, 7 institutions.
  - Ranking quality against an oracle ranking: Pearson r = 0.98 and MMRV 1.8%. Conventional fixed-task evaluation scored r = 0.69 and MMRV 13%.
  - Converges in about 100 comparisons.
  - Failure modes found: tool use, deformable objects, precise insertion and multi-step tasks.
  - Limitations: one embodiment, and open to adversarial evaluators.
  - Source: [arXiv 2506.18123](https://arxiv.org/abs/2506.18123)
- TRI LBM: blind, randomised A/B tests with 50 rollouts per task, policy and condition in the real world and 200 in simulation. Uses Bayesian violin plots instead of point estimates, across 1,800 real trials. An example of a statistically careful protocol — [arXiv 2507.05331](https://arxiv.org/abs/2507.05331)
- Lin et al. used human-scored normalised scores, blind randomised testing with matched initial conditions, and more than 15k rollouts. Normalised scores correlated better with real performance than validation MSE — [arXiv 2410.18647](https://arxiv.org/abs/2410.18647)

**Simulation benchmarks**
- LIBERO has 4 task suites (130 tasks) with teleoperated demonstrations — [arXiv 2306.03310](https://arxiv.org/abs/2306.03310)
- Saturation: "On LIBERO, SOTA method have achieved nearly 100% success rates" — [LIBERO-Recover, arXiv 2609.05178](https://arxiv.org/abs/2609.05178)
- SIMPLER (SimplerEnv) reduces the control and visual sim-to-real gap for Google Robot and WidowX setups. It shows "strong correlation" with real-world performance over about 1,500 paired episodes — [arXiv 2405.05941](https://arxiv.org/abs/2405.05941)
- "What Are We Actually Benchmarking in Robot Manipulation?" (Jun 2026) [MEASURED]:
  - Names four failure modes: shortcut solvability, lack of statistical significance, creeping overfitting, data-source dependence.
  - LIBERO and CALVIN fail multiple diagnostics; RoboCasa and RoboTwin 2.0 fail fewer.
  - On LIBERO, "a 0.09B probe with no language encoder scores at or near reported SOTA, and most reported gains are not provably statistically significant".
  - On CALVIN, randomising block poses within the training range lowers every policy's score.
  - Source: [arXiv 2606.04233](https://arxiv.org/abs/2606.04233)
- Benchmark bugs (Sep 2026): an audit of 7 benchmarks (including RoboTwin, LIBERO-Plus and VLABench) found 22 bugs and 4 design limitations. Fixing them "can reverse method rankings", moving a baseline from last to first — [arXiv 2609.37771](https://arxiv.org/abs/2609.37771)
- Language overfitting: LIBERO policies are trained and tested on the same ten instruction strings. Rewording an instruction changes OpenVLA success by −38.0 points — [arXiv 2610.19438](https://arxiv.org/abs/2610.19438)
- Hardware robustness (LIBERO-RIG, Oct 2026): 9 VLAs, 500 episodes per condition. Pooled success drops from 0.932 to 0.767 at medium perturbation severity and to 0.509 at the highest, under camera, calibration, gain or control-rate changes — [arXiv 2610.18843](https://arxiv.org/abs/2610.18843)
- Mid-task changes (LIBERO-MAX, Sep 2026): 8,000 paired cases and 14 policies. Events during the task reduce success by 11.0–25.7 pp — [arXiv 2609.36518](https://arxiv.org/abs/2609.36518)
- Automatic judging: on FailBench, the best of 13 VLM failure detectors reaches only 0.77 balanced accuracy, near chance (<0.60) on contact-rich assembly, and is biased toward predicting success — [arXiv 2609.03611](https://arxiv.org/abs/2609.03611)

### Inferences
- Headline simulation numbers, especially LIBERO above 95%, should be treated as weak evidence of capability by 2026. Forecast indicators should prefer RoboArena-style rankings, statistically powered real trials (50 or more per condition) and perturbation suites.
- Using VLMs as automatic judges to scale evaluation is itself unreliable, especially for contact-rich tasks. Human-in-the-loop evaluation remains a cost bottleneck.
- Real-world evaluations are not comparable across labs: embodiments, rubrics and initial conditions differ. Company demos such as π*0.6 or Helix are not standardised benchmarks.

### Gaps
- No cross-embodiment real-world arena at scale. RoboArena covers DROID/Franka only.
- No public, independently run evaluation of frontier company models (GEN-0, Helix, π0.6) on a common protocol.
- I did not find a 2026 update on RoboArena's scale (number of evaluations or policies).

---

## Q5. Bottlenecks: generalisation, long-horizon reliability, dexterity and touch, safety, hardware cost, latency

### Takeaway
- **Generalisation** to new scenes is improving through environment diversity. About 100 homes for π0.5, or 32 environment-object pairs per task, gives near-in-domain performance. Robustness to setup changes is still poor: success falls 18–42 pp under hardware perturbation.
- **Long-horizon reliability** is now shown in company demos (hours of continuous operation, failure rates halved with RL from experience). These are not standardised measurements.
- **Dexterity and touch**: the data is thin. Tactile datasets are only now reaching 500–10k h, and industrial contact-rich data is tiny (45 h for PRISM).
- **Safety**: standards are still drafts (ISO 25785-1) and benchmarks are new.
- **Hardware cost** is falling fast: humanoids from about $5.9k to about $90k list price; Goldman Sachs reports manufacturing cost falling about 40% in a year.
- **Latency**: 3B+ VLAs need about 73 ms per chunk on an RTX 4090. This forces dual-system designs (7–9 Hz planner with a 200 Hz controller) and asynchronous chunking.

### Cited Findings
**Generalisation**
- π0.5: steady gains with more environments; about 100 environments approach the test-environment baseline. Without multi-environment data, OOD success falls to 31% [COMPANY CLAIM] — [PI π0.5 blog](https://www.pi.website/blog/pi05)
- Lin et al.: environment generalisation is harder than object generalisation (lower slope) — [arXiv 2410.18647](https://arxiv.org/abs/2410.18647)
- Across RoboArena tasks, policies do well at pick-and-place and pushing but struggle with tool use, deformable objects, precise alignment and multi-step reasoning — [arXiv 2506.18123](https://arxiv.org/abs/2506.18123)
- OXE authors list generalisation to unseen robots and new sensing modalities as open problems — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864)
- A 2026 survey argues that the "embodiment gap" (work still needed to run a model on a given body) is underreported by success rates alone — [arXiv 2608.18433](https://arxiv.org/abs/2608.18433)
- LIBERO-RIG: success drops from 0.932 to 0.509 at the highest hardware-perturbation severity. Training on visual perturbations does not fix faults that leave camera images unchanged — [arXiv 2610.18843](https://arxiv.org/abs/2610.18843)

**Long-horizon reliability**
- π*0.6 with Recap (RL on autonomous experience) "more than doubles the throughput on some of the hardest tasks, and can decrease failure rates by 2x or more". Demos [COMPANY CLAIM]:
  - Making espresso "from 5:30am to 11:30pm".
  - Folding "50 different novel laundry items in a new home".
  - Assembling and labelling "59 boxes" in a real factory, "without interruption for hours".
  - Source: [PI π*0.6 blog](https://www.pi.website/blog/pistar06)
- GEN-0: peak success "up to 99%" on some tasks with 550+ h of task-specific post-training [COMPANY CLAIM] — [Generalist GEN-0 blog](https://generalistai.com/blog/nov-04-2025-GEN-0)
- AgiBot trajectories average about 30 s, against less than 5 s for most prior datasets. The authors describe OXE-trained policies as "constrained to naive, short-horizon tasks" — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669)
- Recovery is barely measured: LIBERO-Recover argues that "near perfect performance on existing benchmarks can be misleading" and builds 1,000+ recovery scenarios — [arXiv 2609.05178](https://arxiv.org/abs/2609.05178)
- Reports that Figure Helix-02 ran a 50-hour autonomous warehouse session come only from low-authority aggregators. Unverified — [aiweekly](https://aiweekly.co/alerts/figure-ai-helix-02-runs-50-hours-autonomous-zero-teleoperation)

**Dexterity and tactile sensing**
- EgoDex states: "there is no Internet-scale corpus of data for dexterous manipulation" — [arXiv 2505.11709](https://arxiv.org/abs/2505.11709)
- TouchScale says synchronised tactile data "remain far smaller in volume than human video". Its 500 h raised robot success from 22.5% to 57.5% on four contact-rich tasks — [arXiv 2610.10288](https://arxiv.org/abs/2610.10288)
- PRISM says most datasets "emphasize short-horizon, low-contact tasks such as pick-and-place" and lack force/torque and tactile data. PRISM itself has only 45 h — [arXiv 2608.17962](https://arxiv.org/abs/2608.17962)
- EgoScale: human-data pretraining gave +54% success on a 22-DoF hand and transferred to hands with fewer degrees of freedom — [arXiv 2602.16710](https://arxiv.org/abs/2602.16710)
- Figure Helix controls a 35-DoF action space, including individual fingers, at 200 Hz [COMPANY CLAIM] — [Figure Helix](https://www.figure.ai/news/helix)

**Safety**
- ISO 25785-1 (actively balanced industrial mobile robots, including humanoids) is at Committee Draft stage under ISO/TC 299. Existing standards such as ISO 10218 and ISO 3691-4 do not cover the risks of mobility and balance — [ISO 91469](https://www.iso.org/standard/91469.html); [BSI listing](https://standardsdevelopment.bsigroup.com/projects/9025-11561)
- LIBERO-Safety: evaluates 8 VLA and 2 embodied foundation models and finds "a critical generalization-safety tension". VLA safety under constraints "remains largely unverified" — [arXiv 2606.23686](https://arxiv.org/abs/2606.23686)
- RoboArena needed safety layers (policy compliance tests, supervised test runs) before allowing distributed evaluation — [arXiv 2506.18123](https://arxiv.org/abs/2506.18123)
- Reliable failure detection is weak: the best VLM detector reaches 0.77 balanced accuracy — [arXiv 2609.03611](https://arxiv.org/abs/2609.03611)

**Hardware cost**
- ALOHA costs less than $20k, and its ViperX arms about $5.6k each. Mobile ALOHA costs about $32k, "comparable to a single industrial cobot such as the Franka Emika Panda". PR2 or TIAGo robots cost more than $200k — [arXiv 2304.13705](https://arxiv.org/abs/2304.13705); [arXiv 2401.02117](https://arxiv.org/abs/2401.02117)
- Unitree R1 launched in Jul 2025 at ¥39,999, about US$5,900 [PRESS] — [SCMP](https://www.scmp.com/tech/tech-trends/article/3319637/chinas-unitree-debuts-us5900-humanoid-robot-race-make-cheaper-products). G1 is listed at about ¥99,000 (about $13.8k) and H1 at about $90.8k [PRESS] — [Interesting Engineering](https://interestingengineering.com/innovation/unitree-launches-cheapest-humanoid-robot-r1)
- Goldman Sachs (2024): humanoid manufacturing cost per unit fell from $50k–250k to $30k–150k. That is a 40% decline, against the 15–20% a year analysts expected [analyst claim] — [Goldman Sachs](https://goldmansachs.com/insights/articles/the-global-market-for-robots-could-reach-38-billion-by-2035)

**Inference latency**
- π0 (about 3.3B parameters) takes 73 ms per action chunk onboard and 86 ms offboard on an RTX 4090. Of this, image encoders take 14 ms, the observation forward pass 32 ms and 10 flow steps 27 ms. Control runs at up to 50 Hz through action chunking — [arXiv 2410.24164](https://arxiv.org/abs/2410.24164); [PI π0 blog](https://www.pi.website/blog/pi0)
- RT-2-X (55B) ran through a cloud service at 3–10 Hz depending on the robot — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864)
- Figure Helix splits into a 7B VLM at 7–9 Hz (System 2) and an 80M visuomotor policy at 200 Hz (System 1) [COMPANY CLAIM] — [Figure Helix](https://www.figure.ai/news/helix). GR00T N1 also uses a dual-system design — [arXiv 2503.14734](https://arxiv.org/abs/2503.14734)
- Real-time chunking (RTC) says the "high latency of state-of-the-art generalist models … poses a significant challenge". It produces pauses or jerky motion at chunk boundaries. RTC allows asynchronous execution without retraining and keeps high success on precise tasks (such as lighting a match) under delay — [arXiv 2506.07339](https://arxiv.org/abs/2506.07339)
- Benchmark flaws distort claims about VLA *acceleration*: some training-free speed-ups appeared to raise success only because of benchmark bugs — [arXiv 2609.37771](https://arxiv.org/abs/2609.37771)

### Inferences
- Bottleneck ranking from this evidence. This is my judgement, not a sourced claim.
  1. Reliability and recovery over long horizons, which is poorly measured.
  2. Contact-rich dexterity, where tactile and force data are scarce.
  3. Robustness to deployment variation, including hardware drift.
  4. Evaluation itself, which is unreliable and expensive.
  5. Latency, which is largely solved for now by engineering (dual systems, RTC), but costs will grow if backbones scale past 7B.
  6. Hardware cost, which is falling fastest. Sub-$15k humanoids already exist, but their capability and durability are unclear.
- Safety is probably the slowest-moving constraint on deployment: the main standard is still a draft, and no validated failure detectors exist.

### Gaps
- No independent measurements of mean time between failures or interventions per hour for any frontier generalist policy in real deployment.
- No public cost-of-ownership data (durability, maintenance) for cheap humanoids.
- No public figures on the share of autonomous work against remote teleoperation in commercial humanoid deployments (Figure, Tesla, Agility, 1X).
- Search budget was limited: about 10 web searches plus arXiv/alphaXiv lookups. Gemini Robotics data scale, 1X, and the Chinese government's official data-centre statistics were not checked.
