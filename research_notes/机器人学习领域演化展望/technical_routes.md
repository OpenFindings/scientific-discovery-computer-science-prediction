# Technical Routes of Robot Learning (Robot RL and Robot Foundation Models), 2022 to Oct 2026

Compiled 2026-10-18. Evidence labels used throughout:
- **[PEER]**: peer-reviewed venue that I saw stated on the arXiv comment or project page.
- **[PREPRINT]**: arXiv technical report or paper with no venue I could verify.
- **[COMPANY]**: company blog, model card or press release. These are self-reported, usually without independent replication.
- **[SECONDARY]**: news or aggregator coverage.
- **[OPINION]**: an essay or position statement.

Most of the 2025–2026 frontier claims (π0.7, π*0.6, Gemini Robotics 2, Helix 02, GEN-0/GEN-1, Cosmos 3) come from companies and have not been independently replicated. Where I fetched a page directly I cite it. Snippets from search engines alone are flagged.

---

## Q1. Vision-language-action (VLA) models: date, organisation, what each showed, known limits

### Takeaway
VLAs went through three stages:
1. 2022–23: Google's RT-1, then RT-2, which tokenised actions and co-trained a VLM on web data.
2. 2024: open, cross-embodiment models (Open X-Embodiment/RT-X, Octo, OpenVLA), then π0, which put a flow-matching "action expert" on a VLM.
3. 2025–26: hierarchical or "System 1/2" generalists with whole-body humanoid control, memory, steerable prompting and RL post-training. Examples are π0.5, π*0.6, π0.7, Gemini Robotics 1.5 and 2, GR00T N1.x, Helix and Helix 02, and GEN-0/GEN-1.

Claimed capability has risen fast. Independent robustness audits still show brittleness. Even the leading labs report that multi-finger dexterity, out-of-distribution task generalisation and language following remain unsolved.

### Cited Findings

**RT-1 (Google, Dec 2022) [PREPRINT; project page]**
- Robotics Transformer: EfficientNet with FiLM language conditioning, then TokenLearner, then a Transformer that outputs discretised action tokens at 3 Hz — [RT-1 project page](https://robotics-transformer1.github.io/).
- Data was over 130k episodes covering more than 700 tasks, collected by a fleet of 13 robots over 17 months. RT-1 succeeded on 97% of seen instructions and 76% of unseen instructions, 24% more than the next baseline on unseen instructions — [RT-1 project page](https://robotics-transformer1.github.io/); [arXiv 2212.06817](https://arxiv.org/abs/2212.06817).

**RT-2 (Google DeepMind, Jul 2023) [PREPRINT]**
- RT-2 coined the term "VLA". It expresses actions as text tokens and co-fine-tunes a web-scale VLM on robot trajectories together with VQA data. Across 6k evaluation trials it showed better generalisation to novel objects and to commands absent from the robot data, plus rudimentary reasoning — [arXiv 2307.15818](https://arxiv.org/abs/2307.15818).
- Limits stated by the authors:
  - The robot "does not acquire any ability to perform new motions"; physical skills stay limited to the robot-data skill distribution.
  - High compute cost makes real-time inference a bottleneck for high-frequency control.
  - Source: [RT-2 paper, Limitations](https://arxiv.org/html/2307.15818v1).

**Open X-Embodiment / RT-X (21 institutions led by Google DeepMind, Oct 2023) [PREPRINT]**
- The dataset covers 22 robots from 21 institutions, with 527 skills (160,266 tasks). RT-X showed "positive transfer", improving several robots by drawing on other platforms' data — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864).

**Octo (UC Berkeley, Stanford, CMU and others, May 2024) [PREPRINT]**
- Open-source transformer policy (diffusion action head) trained on 800k Open X-Embodiment trajectories. It accepts language or goal-image conditioning, fine-tunes to new sensors and action spaces in hours on consumer GPUs, and was evaluated on 9 platforms — [arXiv 2405.12213](https://arxiv.org/abs/2405.12213).
- Limits stated by the authors:
  - It "struggles with adequately processing wrist camera information".
  - Language-conditioned and goal-conditioned performance differ greatly.
  - The authors attribute both to the data: only 27% of it has wrist cameras and only 56% has language labels.
  - Source: [Octo paper](https://arxiv.org/html/2405.12213v2).

**OpenVLA (Stanford, UC Berkeley, TRI, Google DeepMind and others, Jun 2024) [PREPRINT]**
- 7B open VLA (Llama 2 with a fused DINOv2 and SigLIP encoder) trained on 970k demonstrations. It beat the closed RT-2-X (55B) by 16.5% absolute success across 29 tasks with 7x fewer parameters, and beat Diffusion Policy by 20.4% when fine-tuned — [arXiv 2406.09246](https://arxiv.org/abs/2406.09246).
- Limits stated by the authors:
  - Single-image observations only.
  - Inference throughput is too low for 50 Hz setups such as ALOHA.
  - Success rates leave room for improvement.
  - Source: [OpenVLA paper, Limitations](https://arxiv.org/html/2406.09246v3).

**Physical Intelligence π0 (Oct 31 2024) [PEER: RSS 2025 per the arXiv comment]**
- Flow-matching VLA: a PaliGemma VLM plus a smaller "action expert", controlling at up to 50 Hz. It was pretrained on over 10,000 hours of robot data from 7 robot configurations and 68 tasks. Shown on laundry folding, table bussing and box assembly — [arXiv 2410.24164](https://arxiv.org/abs/2410.24164); [π0 paper HTML](https://arxiv.org/html/2410.24164v1).
- Limits stated by the authors:
  - It is unclear how pretraining data should be composed or weighted.
  - "Not all tasks in our evaluation work reliably".
  - It is unclear how much data is needed for near-perfect performance.
  - The amount of positive transfer from highly diverse data remains to be seen.
  - Source: [π0 paper](https://arxiv.org/html/2410.24164v1).
- Release timeline [COMPANY]:
  - FAST action tokenizer: Jan 16 2025.
  - Open-sourced π0 and π0-FAST weights: Feb 4 2025.
  - "Hi Robot" hierarchical language reasoning: Feb 26 2025.
  - Source: [PI blog index](https://www.pi.website/blog).
- FAST (DCT-based action tokenisation) lets autoregressive VLAs train on 10k hours of data and match diffusion VLAs with up to 5x less training time — [arXiv 2501.09747](https://arxiv.org/abs/2501.09747).

**π0.5 (Physical Intelligence, Apr 22 2025) [PREPRINT and COMPANY]**
- Co-training on heterogeneous data (multiple robots, high-level semantic subtask prediction, web data, object detections). The authors claim "for the first time" that an end-to-end learned system performs long-horizon, dexterous tasks such as cleaning a kitchen or bedroom "in entirely new homes" — [arXiv 2504.16054](https://arxiv.org/abs/2504.16054).
- "Knowledge insulation" (May 28 2025) [COMPANY]:
  - The backbone is trained with FAST-discretised actions while gradients from the continuous action expert are blocked from flowing back into the VLM.
  - The motivation is that grafting action experts onto VLMs "could damage the VLM's internal representations", causing forgetting and weaker language following.
  - The post frames RT-2 and OpenVLA as "first-generation" VLAs (binned action tokens, "too crude for precise tasks, and very slow") and π0-style action experts as the second generation.
  - Source: [PI knowledge insulation](https://www.pi.website/research/knowledge_insulation).

**π0.6 / π*0.6 with Recap (Physical Intelligence, Nov 17 2025) [PREPRINT and COMPANY]**
- π0.6 uses a 5B-parameter VLM backbone plus an action expert and accepts heterogeneous prompts, including quality and advantage conditioning — [PI π*0.6 blog](https://www.pi.website/blog/pistar06).
- Recap ("RL with Experience & Corrections via Advantage-conditioned Policies") works in stages:
  - offline-RL pretraining;
  - then fine-tuning on demonstrations;
  - then on-robot experience plus teleoperated interventions, using a learned value function and advantage-conditioned policy extraction.
- Claimed results: "more than doubles task throughput and roughly halves the task failure rate" on the hardest tasks — [arXiv 2511.14759](https://arxiv.org/abs/2511.14759).
- Company demos: espresso drinks made from 5:30am to 11:30pm; 50 novel laundry items folded in a new home; 59 boxes assembled in a real chocolate factory; "over a 90% success rate" on the espresso-task stages — [PI π*0.6 blog](https://www.pi.website/blog/pistar06).
- "Robot Olympics" (Dec 22 2025) [COMPANY]:
  - Fine-tuning the π0.6-based model, mostly with under 9 hours of data per task, gave "gold" on 3 of 5 of Benjie Holson's challenge categories and "silver" on the other 2.
  - Average success was only 52% (72% task progress).
  - A baseline built by fine-tuning a plain VLM succeeded on none (9% progress).
  - Source: [PI Robot Olympics](https://www.pi.website/blog/olympics).
- Human-to-robot transfer (Dec 16 2025) [COMPANY]: adding egocentric human video during fine-tuning gave about a 2x gain on 4 generalisation scenarios present only in the human data. The post says this transfer "emerges" as robot pretraining data scales — [PI human-to-robot](https://www.pi.website/research/human_to_robot).

**π0.7 (Physical Intelligence, Apr 16 2026) [COMPANY; a paper PDF is linked but I did not verify its arXiv status]**
- Claims a "step-change in generalization":
  - It matches fine-tuned specialists out of the box.
  - It shows "first signs of compositional generalization", for example using unseen kitchen appliances with step-by-step language coaching.
  - It folds laundry on a bimanual UR5e that had no laundry data, at a success rate equal to expert teleoperators (mean 375 hours of experience) trying that robot for the first time.
  - Source: [PI π0.7 blog](https://www.pi.website/blog/pi07).
- Method: diverse multimodal prompts (language subtasks, metadata on speed and quality, control-modality labels, and visual subgoal images generated at test time by a "lightweight world model"). This lets suboptimal autonomous data be included in training. π0.7 distils Recap RL experience so that a single model equals or beats the π*0.6 specialists on laundry, espresso and box building — [PI π0.7 blog](https://www.pi.website/blog/pi07).
- Limit the company itself shows: on the one-shot prompt "load a sweet potato into the air fryer", π0.7 makes a "reasonable attempt… but not finishing it fully". Success needed human verbal coaching or a fine-tuned high-level policy — [PI π0.7 blog](https://www.pi.website/blog/pi07).
- Other PI 2026 posts [COMPANY]:
  - MEM (Mar 3 2026): multi-scale embodied memory (video encoder plus language memory) for tasks up to about 15 minutes — [PI MEM](https://www.pi.website/research/memory).
  - RL Tokens (Mar 19 2026): see Q3.
  - Pi API beta (Oct 13 2026): hosted fine-tuning and cloud inference. Partner deployments include an autonomous wheel loader at Actor. The post notes "network connectivity challenges for some" — [PI API beta](https://www.pi.website/blog/api-beta).

**Gemini Robotics (Google DeepMind)**
- Gemini Robotics and Gemini Robotics-ER (arXiv Mar 25 2025) [PREPRINT]:
  - A VLA built on Gemini 2.0.
  - It can be specialised to long-horizon dexterous tasks, learns new short-horizon tasks "from as few as 100 demonstrations", and adapts to novel embodiments.
  - ER adds pointing, 3D boxes, trajectory and grasp prediction.
  - Source: [arXiv 2503.20020](https://arxiv.org/abs/2503.20020).
- Gemini Robotics 1.5 (Oct 2 2025) [PREPRINT]: a multi-embodiment VLA with a "Motion Transfer" mechanism for learning from heterogeneous robot data, plus interleaved natural-language "thinking before acting". ER 1.5 is described as state of the art on embodied reasoning — [arXiv 2510.03342](https://arxiv.org/abs/2510.03342).
- Gemini Robotics 2 (Jul 30 2026) [COMPANY]:
  - Family of three models: the GR2 VLA, ER 2 (embodied reasoning / agent), and On-Device 2.
  - Claimed: whole-body humanoid control (Apptronik Apollo 2) "from feet to fingertips"; dexterity with the 22-DoF SharpaWave hand (knots, sealing ziplock bags); multi-robot collaboration; tasks lasting "several minutes and involving hundreds of decisions"; On-Device 2 adapts to new bi-arm embodiments "typically with less than 200 examples" in a few hours.
  - Stated limits:
    - "multi-finger dexterous manipulation remains challenging";
    - "our robots have more to advance in movement speed";
    - only ER 2 is publicly available (AI Studio), while the VLA and On-Device models go to early-access partners.
  - Source: [DeepMind GR2 blog](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/); [DeepMind Gemini Robotics page](https://deepmind.google/models/gemini-robotics/).
  - Secondary coverage reports lifting success rates on Apollo hands of 68.4% from a table, 45.7% from the floor and 76.3% from a shelf [SECONDARY, not verified on the DeepMind page] — [Gigazine](https://gigazine.net/gsc_news/en/20260731-google-deepmind-gemini-robotics-2).

**NVIDIA GR00T N1 and successors**
- GR00T N1 (Mar 18 2025) [PREPRINT]:
  - An open humanoid foundation model with a dual system: a VLM as "System 2" and a diffusion transformer as "System 1", trained jointly end to end.
  - Trained on real robot trajectories, human videos and synthetic data.
  - Deployed on the Fourier GR-1 for language-conditioned bimanual tasks.
  - Source: [arXiv 2503.14734](https://arxiv.org/abs/2503.14734).
- GR00T N1.6 (Dec 15 2025) [COMPANY]:
  - Architecture: Cosmos-2B VLM variant; DiT twice as large (32 layers); state-relative action chunks.
  - Data: several thousand added hours of teleoperation (YAM, AgiBot Genie-1, Unitree G1 whole-body loco-manipulation).
  - Model card: flow-matching DiT, jointly trained with flow-matching and world-modelling objectives.
  - Stated limits: "Multi-task language following and out-of-distribution task generalization continue to be challenging for current VLA models"; relative actions accumulate error with small datasets; DAgger is recommended when performance is weak.
  - Source: [NVIDIA GR00T N1.6 research blog](https://research.nvidia.com/labs/gear/gr00t-n1_6/); [HF model card](https://huggingface.co/nvidia/GR00T-N1.6-3B).
- GR00T N1.7 [COMPANY]: model card lists a Cosmos-Reason2-2B backbone with a flow-matching action transformer, released under the NVIDIA Open Model License — [HF GR00T-N1.7-3B](https://huggingface.co/nvidia/GR00T-N1.7-3B).
  - A third-party report replaced the N1.7 DiT head with a one-step "drifting" head. Head latency fell from 45.3 ms to 5.0 ms, but success dropped systematically (LIBERO-Long 26.0±2.6%). The authors present this as a speed–success trade-off — [arXiv 2609.18108](https://arxiv.org/abs/2609.18108).
- I found no evidence of a "GR00T N2" release (see Gaps).

**Figure Helix (Feb 20 2025) and Helix 02 (Jan 27 2026) [COMPANY]**
- Helix:
  - Claimed "first VLA to output high-rate continuous control of the entire humanoid upper body", including fingers, at 200 Hz.
  - Architecture: System 2 is a 7B VLM; System 1 is an 80M visuomotor policy.
  - Trained on about 500 hours of supervised data (<5% of earlier VLA datasets).
  - Also shown: multi-robot collaboration.
  - Source: [Figure Helix](https://www.figure.ai/news/helix).
- Helix 02:
  - Adds "System 0", a 10M-parameter whole-body controller at 1 kHz trained in simulation (200,000+ parallel environments, domain randomisation) on more than 1,000 hours of retargeted human motion. Figure says it "replaces 109,504 lines of hand-engineered C++".
  - System 1 now maps all sensors (head and palm cameras, fingertip tactile sensing down to 3 g, proprioception) to every joint at 200 Hz.
  - Demo: a 4-minute autonomous dishwasher unload/reload with 61 loco-manipulation actions, which Figure calls the "longest horizon, most complex task completed autonomously by a humanoid robot to date".
  - Source: [Figure Helix 02](https://www.figure.ai/news/helix-02).
- Elon Musk publicly questioned whether a later Helix 02 cleaning demo was teleoperated [SECONDARY] — [Finviz/Benzinga](https://finviz.com/news/334591/nvidia-backed-figure-shows-humanoid-robot-as-elon-musk-questions-if-its-truly-autonomous).
- Claims of 8-hour shifts are reported only from a company X post [SECONDARY] — [humanoid.guide](https://humanoid.guide/figure-ai-demonstrates-helix-02-humanoid-robots-on-8-hour-shifts/).

**Other important 2025–2026 successors**
- **Generalist AI GEN-0** (Nov 4 2025) [COMPANY]:
  - Claims "strong scaling laws" from pretraining data and compute to downstream post-training performance.
  - Claims a "phase transition" at about 7B parameters: 1B models "ossify", 7B+ models keep absorbing data. Since scaled to 10B+.
  - Data: over 270,000 hours of real-world manipulation data, growing 10,000 hours per week.
  - "Harmonic Reasoning" interleaves asynchronous sensing and acting tokens without a System 1/2 split.
  - Tested on 6-DoF, 7-DoF and 16+-DoF semi-humanoid robots.
  - Source: [Generalist GEN-0](https://generalistai.com/blog/gen-0).
- **GEN-1** (Apr 2 2026) [COMPANY]:
  - Claims 99% average success on tasks where earlier models reach 64%, about 3x faster than state of the art, with about 1 hour of robot data per task.
  - Trained from scratch on "half a million hours" of real-world data. The base model uses "data from low-cost wearable devices on humans" rather than teleoperation.
  - Stated limits: "not all tasks that we have attempted are able to hit these rates", and emergent improvisation "can be… a liability" (an alignment problem).
  - Source: [Generalist GEN-1](https://generalistai.com/blog/gen-1).
- **TRI Large Behavior Models** [PEER: Science Robotics 2026 per the project page]:
  - Diffusion-transformer LBMs trained on about 1,700 hours (468 h internal bimanual teleoperation, 45 h simulation, 32 h UMI, about 1,150 h curated OXE).
  - Evaluated with 1,800 real and 47,000+ simulated blind, randomised rollouts.
  - Pretraining gives consistent gains, 3–5x less data for new tasks, and "improve[s] steadily as pretraining data increases".
  - Source: [TRI LBM project page](https://toyotaresearchinstitute.github.io/lbm1/); [arXiv 2507.05331](https://arxiv.org/abs/2507.05331).
- **Boston Dynamics + TRI LBM on Atlas** (Aug 20 2025) [COMPANY]: a single LBM directly controls the whole robot, "treating the hands and the feet almost identically", during long packing and sorting sequences with mid-task disturbances — [TRI press release](https://www.tri.global/news/ai-powered-robot-boston-dynamics-and-toyota-research-institute-takes-key-step-towards-general).
- **NVIDIA Cosmos Policy and Cosmos 3** (world-model-based policies; see Q4) — [arXiv 2601.16163](https://arxiv.org/abs/2601.16163); [arXiv 2606.02800](https://arxiv.org/abs/2606.02800).
- **Chinese and other industrial VLAs** [PREPRINT]:
  - AgiBot World and GO-1 (Mar 2025): over 1M trajectories and 217 tasks; latent-action policy with "predictable performance scaling with increased data volume"; 30% better than OXE-pretrained policies — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669).
  - ByteDance GR-3 (Jul 2025): claims to surpass π0, co-training on web VL data and VR human trajectories — [arXiv 2507.15493](https://arxiv.org/abs/2507.15493).
  - RDT-1B (Oct 2024): 1.2B diffusion bimanual foundation model — [arXiv 2410.07864](https://arxiv.org/abs/2410.07864).
  - Tencent HyVLA-0.5 (Jun 2026): a full stack including RL post-training — [arXiv 2606.14409](https://arxiv.org/abs/2606.14409).
  - Hugging Face SmolVLA (Jun 2025): small community VLA trainable on a single GPU — [arXiv 2506.01844](https://arxiv.org/abs/2506.01844).

**Independent evaluations and critiques of VLAs**
- LIBERO-Plus (Oct 2025) [PREPRINT]: under modest perturbations (camera viewpoint, robot initial state) VLA success drops "from 95% to below 30%". Models "tend to ignore language instructions completely" — [arXiv 2510.13626](https://arxiv.org/abs/2510.13626).
- WorldGym [PREPRINT]: "modern VLA-based robot policies still struggle to distinguish object shapes and can become distracted by adversarial facades" — [arXiv 2506.00613](https://arxiv.org/abs/2506.00613).
- STAR-Gen taxonomy [PEER: RA-L]: calls generalisation evaluation "the Wild West of modern robotics" — [arXiv 2503.01238](https://arxiv.org/abs/2503.01238).
- RoboArena [PREPRINT]: distributed, double-blind pairwise real-world evaluation across 7 institutions on DROID — [arXiv 2506.18123](https://arxiv.org/abs/2506.18123).
- VLANeXt [PREPRINT]: the VLA landscape is "fragmented", and inconsistent protocols make it hard to identify which design choices matter — [arXiv 2602.18532](https://arxiv.org/abs/2602.18532).
- Surveys from 2025–2026:
  - [Action-tokenization survey, arXiv 2507.01925](https://arxiv.org/abs/2507.01925)
  - [Pure VLA survey, arXiv 2509.19012](https://arxiv.org/abs/2509.19012)
  - [VLA review towards real-world applications, arXiv 2510.07077](https://arxiv.org/abs/2510.07077)
  - [10 Open Challenges for VLAs, arXiv 2511.05936](https://arxiv.org/abs/2511.05936)

### Inferences
- The architecture has converged on a pretrained VLM (or video-model) backbone, a continuous action expert (diffusion or flow matching) that outputs action chunks, and a slower reasoning or planning layer (Hi Robot, π0.5 subtasks, Gemini ER, Helix S2, GR00T System 2). Within one generation (2023 to 2025) the field abandoned binned action tokens as the main output head.
- Since late 2025 the frontier "recipe" changed from "more teleoperation plus a bigger VLM" to four ingredients:
  1. heterogeneous data, including human egocentric and wearable data and autonomous rollouts;
  2. richer conditioning (metadata, subgoals);
  3. RL post-training for reliability and throughput;
  4. memory for long horizons.
- The capability gap between company claims and independent benchmarks is large. Forecasts should discount company success rates, because they come from chosen tasks, are often fine-tuned, and are not blind-evaluated. TRI's Science Robotics LBM study and RoboArena are the main exceptions that use rigorous protocols.

### Gaps
- No independent replication exists for π0.7, Gemini Robotics 2, Helix 02 or GEN-1. Their task success rates are self-reported.
- I could not confirm a GR00T N1.7 release date or any "GR00T N2". The search did not surface NVIDIA's newsroom.
- I did not verify whether the π0.7 paper is on arXiv or peer-reviewed.
- I did not check venues for RT-1, RT-2, OXE, OpenVLA or Octo, so they are cited as arXiv.
- Tesla Optimus, 1X, Skild AI and Agility learning stacks were not researched (budget).

---

## Q2. Diffusion policy, action chunking (ACT/ALOHA) and flow-matching action heads

### Takeaway
Since 2023, generative action models have become the default policy class. They predict action *chunks* with diffusion or flow matching, which handles multimodal demonstrations and high-frequency control. Flow-matching action experts on top of VLMs (π0, GR00T N1.6/N1.7) are now the standard VLA head. The main remaining issues are inference latency and smoothness at chunk boundaries, which real-time chunking and one-step heads try to address, so far with trade-offs.

### Cited Findings
- **ACT / ALOHA** (Stanford, Apr 2023) [PREPRINT]: low-cost bimanual teleoperation hardware plus Action Chunking with Transformers (a generative model over action sequences) learned 6 fine tasks, such as slotting a battery, at 80–90% success from about 10 minutes of demonstrations — [arXiv 2304.13705](https://arxiv.org/abs/2304.13705).
- **Mobile ALOHA** (Jan 2024) [PREPRINT]: whole-body teleoperation for mobile bimanual tasks. Co-training with static ALOHA data raised success "by up to 90%" with 50 demonstrations per task (cooking shrimp, calling an elevator) — [arXiv 2401.02117](https://arxiv.org/abs/2401.02117).
- **Diffusion Policy** (Columbia, TRI, MIT, Mar 2023) [PEER: RSS 2023, with an extended journal version]:
  - Represents the policy as conditional denoising diffusion, with receding-horizon control and a time-series diffusion transformer.
  - Average improvement of 46.9% over the prior state of the art across 12 tasks from 4 benchmarks.
  - Handles multimodal action distributions and high-dimensional actions stably.
  - Source: [arXiv 2303.04137](https://arxiv.org/abs/2303.04137).
- **UMI** (Stanford, Columbia, TRI, Feb 2024) [PREPRINT]: hand-held gripper data collection that does not require a robot during collection. Inference-latency matching and relative-trajectory actions give hardware-agnostic policies — [arXiv 2402.10329](https://arxiv.org/abs/2402.10329).
- **Flow matching in VLAs**:
  - π0 uses "an action chunking architecture with flow matching (a variant of diffusion)" to reach 50 Hz — [π0 paper](https://arxiv.org/html/2410.24164v1).
  - GR00T N1.6 uses a flow-matching DiT and cites π0 as the flow-matching policy reference — [HF model card](https://huggingface.co/nvidia/GR00T-N1.6-3B).
  - TRI LBMs are diffusion transformers that predict 16-step (1.6 s) chunks — [TRI LBM](https://toyotaresearchinstitute.github.io/lbm1/).
  - DexVLA uses a 1B diffusion expert [PEER: CoRL 2025] — [arXiv 2502.05855](https://arxiv.org/abs/2502.05855).
- **Latency fixes**:
  - Real-time chunking (RTC; PI, Jun 2025) [PEER: NeurIPS 2025] generates the next chunk while executing the current one ("freezing" and "inpainting"), needs no retraining, and is robust to inference delay. Example task: lighting a match — [arXiv 2506.07339](https://arxiv.org/abs/2506.07339).
  - NVIDIA uses test-time and train-time RTC on G1 and YAM — [GR00T N1.6 blog](https://research.nvidia.com/labs/gear/gr00t-n1_6/).
  - One-step heads speed up inference but lose success — [arXiv 2609.18108](https://arxiv.org/abs/2609.18108).
- **Autoregressive alternative**: FAST tokenisation recovers performance for autoregressive VLAs and matches diffusion VLAs — [arXiv 2501.09747](https://arxiv.org/abs/2501.09747). PI's knowledge-insulation work combines both: FAST tokens train the backbone and a flow expert produces the output — [PI KI](https://www.pi.website/research/knowledge_insulation).

### Inferences
- Action chunking combined with a diffusion or flow head is now the backbone shared by imitation learning, VLAs and even world-action models (Cosmos Policy encodes actions as latent frames). Further progress here will likely come from systems work (latency, asynchrony, distillation) rather than new policy classes.
- Flow and diffusion heads lack tractable likelihoods, so RL fine-tuning of them needs special techniques (πRL's Flow-Noise and Flow-SDE, Recap's advantage conditioning; see Q3). This coupling links Q2 and Q3.

### Gaps
- I found no controlled head-to-head study across 2025–26 of diffusion versus flow versus autoregressive heads at frontier scale. VLANeXt may contain one but I only read its abstract.

---

## Q3. Reinforcement learning's role now: sim-to-real locomotion, RL fine-tuning of VLAs, real-world RL, RLHF and preference learning

### Takeaway
RL plays two distinct roles:
1. **Sim-to-real RL is the established, dominant method for legged and humanoid locomotion and whole-body control.** It runs from ANYmal (2020) to Helix 02's System 0 (2026).
2. **For manipulation, RL came back in 2024–26 as a *post-training* stage on top of imitation-pretrained VLAs**, aimed at reliability and throughput rather than at learning skills from scratch. Examples are HIL-SERL, π*0.6/Recap, RL Tokens, SimpleVLA-RL, πRL, and the many papers since September 2026.

Preference and RLHF-style methods in robotics are mostly about *learned reward and progress models* (often VLM-based). They are an active research area, not yet a proven standard.

### Cited Findings

**Sim-to-real locomotion (legged and humanoid)**
- ANYmal (ETH, 2020) [PREPRINT]: an RL controller trained in simulation on proprioception showed "remarkable zero-shot generalization from simulation to natural environments" (mud, snow, dynamic footholds) — [arXiv 2010.11251](https://arxiv.org/abs/2010.11251).
- Perceptive extension (2022) [PREPRINT]: an attention-based recurrent encoder fusing exteroception and proprioception for robust perceptive locomotion in the wild — [arXiv 2201.08117](https://arxiv.org/abs/2201.08117).
- Real-world humanoid locomotion (UC Berkeley, Mar 2023) [PREPRINT]: a causal transformer trained with large-scale model-free RL on randomised simulated environments was deployed zero-shot outdoors and adapts in context — [arXiv 2303.03381](https://arxiv.org/abs/2303.03381).
- DeepMind OP3 soccer (Apr 2023) [PREPRINT]: deep RL on a 20-joint miniature humanoid gave fall recovery, kicking and tactics, transferred zero-shot. Transfer relied on high-frequency control, targeted dynamics randomisation and perturbations — [arXiv 2304.13653](https://arxiv.org/abs/2304.13653).
- Industrial adoption: Helix 02's System 0 is trained entirely in simulation with RL plus human-motion tracking, replacing 109,504 lines of C++ [COMPANY] — [Figure Helix 02](https://www.figure.ai/news/helix-02).

**RL fine-tuning of VLAs and real-world RL (manipulation)**
- HIL-SERL (UC Berkeley, Oct 2024) [PREPRINT]: human-in-the-loop vision-based RL (demonstrations plus corrections plus efficient off-policy RL). Reaches "near-perfect success rates" within 1–2.5 hours of training, with 2x the success and 1.8x faster execution than imitation baselines — [arXiv 2410.21845](https://arxiv.org/abs/2410.21845).
- π*0.6 / Recap [PREPRINT and COMPANY]: offline RL pretraining, then on-robot RL with interventions. About 2x throughput and about half the failure rate on hard tasks — [arXiv 2511.14759](https://arxiv.org/abs/2511.14759).
  - PI argues the reason for RL is that imitation-trained VLAs suffer compounding errors: "it's relatively easy to get VLAs to succeed at a task some of the time, it's quite hard to make them succeed reliably" [COMPANY/OPINION] — [PI π*0.6 blog](https://www.pi.website/blog/pistar06).
- RL Tokens (PI, Mar 19 2026) [COMPANY]: the VLA produces a compact "RL token" consumed by a small actor-critic trained online with off-policy RL. This speeds up the most precise task stages by up to 3x within hours and "can surpass the speed of human teleoperation" — [PI RLT](https://www.pi.website/research/rlt).
- π0.7 distils RL-generated experience back into one generalist model, so RL becomes a data engine for the base model [COMPANY] — [PI π0.7 blog](https://www.pi.website/blog/pi07).
- SimpleVLA-RL (Sep 2025) [PREPRINT]: scalable RL on OpenVLA-OFT reaches state of the art on LIBERO, beats π0 on RoboTwin, and "surpasses SFT in real-world tasks" — [arXiv 2509.09674](https://arxiv.org/abs/2509.09674).
- πRL (Oct 2025) [PREPRINT]: online RL for flow-based VLAs (π0, π0.5) via Flow-Noise and Flow-SDE formulations that address intractable likelihoods. Gains in-distribution and out-of-distribution — [arXiv 2510.25889](https://arxiv.org/abs/2510.25889).
- Real-Time EXPO-FT (Stanford, Sep 2026) [PREPRINT]: inference latency makes observations stale. The method splits a slow VLA chunk proposer from a fast, lightweight RL "edit" policy — [arXiv 2609.18207](https://arxiv.org/abs/2609.18207).
- NVIDIA/KAIST ACCRUE (Oct 2026) [PREPRINT]: continual off-policy RL for robot foundation models that keeps prior skills — [alphaXiv 2610.18596](https://www.alphaxiv.org/abs/2610.18596).
- An alphaXiv search returned more than 20 VLA-RL papers from Jul–Oct 2026 alone (world-model critics, real-world online RL, subtask RL), showing how crowded the area has become — e.g. [WoVR+ 2610.17922](https://www.alphaxiv.org/abs/2610.17922), [WCM 2607.29613](https://www.alphaxiv.org/abs/2607.29613), [Low-rank structure of VLA RL 2609.34599](https://www.alphaxiv.org/abs/2609.34599).

**RL from human feedback, preferences and learned rewards**
- RL-VLM-F [PEER: ICML 2024]: queries VLMs for *preferences* over pairs of image observations and learns a reward from them. Outperforms raw VLM reward scores on rigid, articulated and deformable manipulation — [arXiv 2402.03681](https://arxiv.org/abs/2402.03681).
- Large Reward Models (USC/TRI, Mar 2026) [PREPRINT]: a VLM specialised into frame-level progress, completion and contrastive rewards. Progress rewards were "the strongest non-privileged online refinement signal" for PPO refinement — [arXiv 2603.16065](https://arxiv.org/abs/2603.16065).
- Freeform Preference Learning (Stanford, Jun 2026) [PREPRINT]: annotators define natural-language preference axes (speed, safety, carefulness). Reports +38 percentage points over sparse-reward and binary-preference baselines on 4 real and 2 simulated long-horizon tasks — [arXiv 2606.32027](https://arxiv.org/abs/2606.32027).
- SARM2 (Jun 2026) multi-task stage-aware reward modelling — [alphaXiv 2606.10305](https://www.alphaxiv.org/abs/2606.10305).
- Recap's value function, which predicts negative steps-to-completion, is a learned progress model at frontier scale [COMPANY] — [PI π*0.6 blog](https://www.pi.website/blog/pistar06).
- GEN-1 frames emergent behaviour as an *alignment* problem ("what it should not do") [COMPANY/OPINION] — [Generalist GEN-1](https://generalistai.com/blog/gen-1).

### Inferences
- The 2022 view that RL was impractical on real robots outside locomotion has been replaced by a hybrid default: imitation-pretrain, then RL or interventions post-train, then distil back into the generalist. This mirrors the LLM pretrain, then RLHF/RLVR, sequence. Credible signals of this shift are PI's Recap, RL Tokens and π0.7, and NVIDIA's ACCRUE.
- For 2030 forecasts, the key open variable is *reward specification at scale*. Learned VLM progress and reward models are the main candidate, and their reliability (reward hacking, false progress) is still under-tested on real robots.
- Locomotion RL is mature. The remaining work is whole-body loco-manipulation, closing the sim-to-real dynamics gap (see ASAP, Q5) and integration under VLA high-level control.

### Gaps
- I found no independent, multi-lab replication of real-world VLA-RL gains on standardised tasks. Most results are on LIBERO or ManiSkill simulation, or on in-house tasks.
- I found no peer-reviewed comparison of RLHF-style preference learning against intervention-based (DAgger-style) correction at scale.
- I did not verify the venue of HIL-SERL.

---

## Q4. World models and video-prediction models for robotics (Genie, Cosmos, V-JEPA 2, etc.): have they shown policy gains?

### Takeaway
Yes, with caveats. World and video models now produce measurable policy gains through three routes:
1. **Synthetic data generation**: DreamGen.
2. **Policy backbones ("world action models")**: Cosmos Policy and Cosmos 3 Policy, which report state of the art on LIBERO and RoboCasa and top RoboArena rankings. π0.7 also uses world-model-generated subgoal images.
3. **Evaluation and RL simulators**: WorldGym, WoVR+.

Zero-shot planning with a latent world model (V-JEPA 2-AC) works only for short-horizon pick-and-place with image goals. Genie 3 has not been shown, in primary sources I found, to improve real robot policies.

### Cited Findings
- **UniPi** (Jan 2023) [PEER: NeurIPS 2023]: casts decision-making as text-conditioned video generation followed by action extraction — an early "policy-as-video" approach — [arXiv 2302.00111](https://arxiv.org/abs/2302.00111).
- **NVIDIA Cosmos WFM** (Jan 2025) [PREPRINT]: an open-weight world foundation model platform (video curation, tokenizers, pretrained models) for physical AI — [arXiv 2501.03575](https://arxiv.org/abs/2501.03575).
- **DreamGen** (NVIDIA, May 2025) [PREPRINT]:
  - Video world models generate "neural trajectories"; pseudo-actions are recovered with latent-action or inverse-dynamics models.
  - A humanoid performed 22 new behaviours in seen and unseen environments using teleoperation data from only one pick-and-place task.
  - DreamGen Bench scores correlate with downstream policy success.
  - Source: [arXiv 2505.12705](https://arxiv.org/abs/2505.12705).
- **V-JEPA 2** (Meta, Jun 2025) [PREPRINT]:
  - Self-supervised pretraining on over 1M hours of video, then an action-conditioned V-JEPA 2-AC post-trained on under 62 hours of unlabeled DROID video.
  - Planned zero-shot pick-and-place with image goals on Franka arms in two labs without in-environment data.
  - Limits: predictions only up to about 16 s; longer-horizon tasks "will require further innovations"; image-goal specification only.
  - Source: [arXiv 2506.09985](https://arxiv.org/abs/2506.09985); [V-JEPA 2 paper limitations](https://arxiv.org/html/2506.09985v1).
- **Cosmos Policy** (NVIDIA, Jan 2026) [PREPRINT]:
  - Fine-tunes Cosmos-Predict2 into a policy in one stage, with no architectural changes. Actions, future states and values are encoded as latent frames.
  - Reports 98.5% on LIBERO and 67.1% on RoboCasa, and the highest average on real bimanual tasks, beating VLAs fine-tuned on the same data.
  - Supports model-based planning from rollout data.
  - Source: [arXiv 2601.16163](https://arxiv.org/abs/2601.16163).
- **Cosmos 3** (NVIDIA, Jun 2026) [PREPRINT]:
  - Omnimodal mixture-of-transformers covering language, image, video, audio and action.
  - Its post-trained policy was "best policy model by RoboArena at the time the technical report was written" — [arXiv 2606.02800](https://arxiv.org/abs/2606.02800).
  - NVIDIA's blog: models at 4B, 16B and 64B parameters; trained on about 767M images, 348M dynamics videos and 8M action samples; the 4B Edge policy runs at 15 Hz on Jetson Thor [COMPANY] — [NVIDIA "Beyond VLAs" blog, Aug 4 2026](https://developer.nvidia.com/blog/beyond-vlas-how-world-action-models-reshape-robot-manipulation/).
  - The same blog quotes Jim Fan's framing "VLAs are dead, long live World Action Models" [OPINION] and argues that VLM backbones "describe the world, not predict how it evolves" — [NVIDIA blog](https://developer.nvidia.com/blog/beyond-vlas-how-world-action-models-reshape-robot-manipulation/).
- **World models as evaluators and simulators**:
  - WorldGym (co-authored with Google DeepMind researchers): success rates inside the world model "highly correlate with real-world success rates" and preserve policy rankings. Realistic object interaction remains hard — [arXiv 2506.00613](https://arxiv.org/abs/2506.00613).
  - World-model-as-simulator RL for VLAs is an active 2026 thread: [WoVR+ 2610.17922](https://www.alphaxiv.org/abs/2610.17922); [WorldSample 2607.02431](https://www.alphaxiv.org/abs/2607.02431).
- **Inside frontier VLAs**:
  - π0.7 uses "synthetically generated visual subgoals produced by a lightweight world model" [COMPANY] — [PI π0.7](https://www.pi.website/blog/pi07).
  - GR00T N1.6 is trained jointly with "flow matching and world-modeling objectives" [COMPANY] — [HF model card](https://huggingface.co/nvidia/GR00T-N1.6-3B).
- **Genie 3** (DeepMind, Aug 2025):
  - Secondary coverage says DeepMind positions it as a training environment for embodied agents (the SIMA agent was tested inside it). It is a limited research preview with a constrained action space and physics errors [SECONDARY] — [YourStory](https://yourstory.com/ai-story/deepmind-genie-3-ai-world-model).
  - DeepMind's models page lists Genie 3 as "Generate and explore interactive worlds" — [DeepMind Gemini Robotics page](https://deepmind.google/models/gemini-robotics/).
  - I found no primary source showing Genie 3 improving a physical robot policy.
- **Generalist AI**: its April 2026 post "Going Beyond World Models & VLAs" argues for training from scratch rather than for either paradigm [OPINION/COMPANY; title seen only] — [Generalist GEN-1 page links](https://generalistai.com/blog/gen-1).

### Inferences
- The strongest evidence of policy gains comes from *world-action models* (a video backbone plus an action head) and *synthetic-trajectory* pipelines. The weakest comes from purely interactive world simulators (Genie-style) for physical robots.
- A live architectural contest has opened for 2026–2030 between VLM-backbone VLAs (PI, DeepMind, Figure) and video-world-model-backbone WAMs (NVIDIA). PI and NVIDIA are already hybridising: π0.7 uses world-model subgoals, and GR00T adds world-modelling losses. Hybrids look more likely than either side winning outright.
- WAM results are mostly from simulation benchmarks (LIBERO, RoboCasa) and RoboArena on DROID, where saturation and benchmark gaming are concerns (see LIBERO-Plus).

### Gaps
- No primary DeepMind source tying Genie 3 to robot policy training was found (the Genie 3 page fetched contained only navigation text).
- I did not research 1X's world model, Wayve-style approaches applied to robotics, or the "Genie Envisioner" paper.
- I found no independent real-world head-to-head of a WAM against π0.5-class VLAs on identical hardware.

---

## Q5. Humanoid-specific learning: whole-body control and teleoperation-to-policy pipelines

### Takeaway
A standard humanoid stack emerged between 2024 and 2026:
1. retarget large human motion-capture or video corpora;
2. train a general whole-body motion-tracking controller with sim-to-real RL;
3. use that controller as both a teleoperation interface and the low-level "System 0";
4. collect whole-body teleoperation demonstrations;
5. train a VLA or behaviour-cloning policy on top.

By 2026 frontier companies (Figure, DeepMind, BD/TRI, NVIDIA) claim *single-network* whole-body loco-manipulation. Public evidence is still demos measured in minutes, not audited deployments.

### Cited Findings
- **HumanPlus** (Stanford, Jun 2024) [PREPRINT]: a low-level policy trained in simulation with RL on 40 hours of human motion lets a humanoid "shadow" a human from a single RGB camera. That shadowing serves as teleoperation for collecting whole-body data, then behaviour cloning from egocentric vision — [arXiv 2406.10454](https://arxiv.org/abs/2406.10454).
- **OmniH2O** (CMU, Jun 2024) [PREPRINT]: kinematic pose as a universal control interface (VR, voice, RGB, or GPT-4 driving it). RL sim-to-real with a privileged-teacher distillation. Released the OmniH2O-6 dataset — [arXiv 2406.08858](https://arxiv.org/abs/2406.08858).
- **HOVER** (NVIDIA, Oct 2024) [PEER: ICRA 2025]: one policy distilled across multiple control modes, with full-body motion imitation as the common abstraction — [arXiv 2410.21229](https://arxiv.org/abs/2410.21229).
- **ASAP** (CMU/NVIDIA, Feb 2025) [PEER: RSS 2025]: pre-train motion tracking in simulation, then learn a delta (residual) action model from real data to align simulator dynamics and fine-tune. Targets agile whole-body skills where SysID and domain randomisation are "overly conservative" — [arXiv 2502.01143](https://arxiv.org/abs/2502.01143).
- **TWIST** (Stanford, May 2025) [PREPRINT]: whole-body teleoperation through motion imitation with an RL+BC controller. Privileged future frames and real MoCap data improve tracking — [arXiv 2505.02833](https://arxiv.org/abs/2505.02833).
- **VideoMimic** (UC Berkeley, May 2025) [PREPRINT]: real-to-sim-to-real from everyday videos, reconstructing both the human and the environment. One policy does stair ascent and descent and sitting on chairs — [arXiv 2505.03729](https://arxiv.org/abs/2505.03729).
- **BeyondMimic** (Aug 2025) [PREPRINT]: a compact motion-tracking formulation for highly agile skills (aerial cartwheels, spin-kicks, sprinting) with shared hyperparameters, plus guided latent diffusion for composing skills on unseen tasks — [arXiv 2508.08241](https://arxiv.org/abs/2508.08241).
- **Figure Helix 02** [COMPANY]: S0 trained on more than 1,000 hours of retargeted human motion with sim RL at 1 kHz; S1 maps pixels to whole-body joints at 200 Hz; 4-minute autonomous dishwasher task; uses its hip and foot as tools — [Figure Helix 02](https://www.figure.ai/news/helix-02).
- **Gemini Robotics 2** [COMPANY]: the first DeepMind model to control the whole Apollo 2 humanoid. Earlier models controlled the upper body for tabletop tasks. Movement speed is acknowledged as a weakness — [DeepMind GR2 blog](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/).
- **BD/TRI Atlas LBM** [COMPANY]: a single LBM controls the whole Atlas. Skills are "added quickly via demonstrations from humans", and Russ Tedrake is quoted saying LBMs "require less and less demonstrations" as they strengthen — [TRI press release](https://www.tri.global/news/ai-powered-robot-boston-dynamics-and-toyota-research-institute-takes-key-step-towards-general).
- **GR00T N1.6** [COMPANY]: adds Unitree G1 whole-body loco-manipulation teleoperation data to pretraining — [NVIDIA GR00T N1.6](https://research.nvidia.com/labs/gear/gr00t-n1_6/).
- **GR00T N1 and DreamGen** use human video and synthetic video for humanoids — [arXiv 2503.14734](https://arxiv.org/abs/2503.14734); [arXiv 2505.12705](https://arxiv.org/abs/2505.12705).

### Inferences
- The humanoid route is a hybrid of modular and end-to-end control. RL motion priors (System 0) sit under end-to-end VLAs, so "end-to-end" in humanoid marketing usually means *pixels to joint targets*, with a separate learned balance controller underneath.
- Human motion data (MoCap, video, wearables) has become a scalable substitute for robot teleoperation at the low level. GEN-1 and PI's human-to-robot results suggest the same could happen at the manipulation level by 2030.

### Gaps
- No published reliability statistics exist for humanoid loco-manipulation in real deployments (mean time between interventions, success over hundreds of trials).
- Figure's shift-length claims are unverified.
- Tesla Optimus and Unitree learning pipelines were not researched.

---

## Q6. Open technical debates: end-to-end vs modular; scaling laws for robot data; cross-embodiment transfer; long-horizon tasks; dexterity

### Takeaway
- **End-to-end versus modular:** in practice everyone builds learned hierarchies (System 2/1/0). The debate is now about *where the interfaces sit* (language, latents, subgoal images, motion priors) and whether the backbone should be a VLM or a video world model.
- **Scaling laws:** there is real but limited evidence that pretraining scales: a power law in environment and object diversity (2024), TRI's steady gains, and company-claimed scaling laws (GEN-0) and "emergent" transfer (PI). No published compute-optimal law exists.
- **Cross-embodiment transfer:** works with motion-transfer or heterogeneous tokenisation.
- **Long-horizon tasks:** have moved from seconds to minutes (4–15 minutes) through hierarchy and memory.
- **Dexterity:** multi-finger dexterity is the frontier that leading labs themselves still call unsolved. Rodney Brooks argues that the vision-only data approach cannot solve it.

### Cited Findings

**End-to-end versus modular**
- Figure claims a "single unified visuomotor neural network" from sensors to actuators, yet structures it as S2/S1/S0 at different rates — [Figure Helix 02](https://www.figure.ai/news/helix-02).
- GEN-0 explicitly avoids "System1-System2 architectures" by using a single stream of "harmonic reasoning" [COMPANY] — [Generalist GEN-0](https://generalistai.com/blog/gen-0).
- DeepMind pairs an ER agent with a VLA: the ER model plans, tracks progress and refuses unsafe VLA tool calls (ASIMOV-Agentic safety benchmark) [COMPANY] — [DeepMind GR2 blog](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/).
- NVIDIA argues the VLM backbone itself is the wrong module and should be a world model [OPINION] — [NVIDIA blog](https://developer.nvidia.com/blog/beyond-vlas-how-world-action-models-reshape-robot-manipulation/).
- Rodney Brooks: the "let's just do end-to-end learning" approach to dexterity is misguided; believing humanoids will be "plug compatible" with human workers "any time within decades is pure fantasy thinking" [OPINION, Sep 2025] — [Brooks essay](https://rodneybrooks.com/why-todays-humanoids-wont-learn-dexterity/); coverage: [TechCrunch](https://techcrunch.com/2025/09/26/famed-roboticist-says-humanoid-robot-bubble-is-doomed-to-burst).

**Scaling laws for robot data**
- RT-1 already studied generalisation as a function of data size, model size and diversity — [arXiv 2212.06817](https://arxiv.org/abs/2212.06817).
- Data Scaling Laws in Imitation Learning (Tsinghua, Oct 2024) [PREPRINT]:
  - Over 40,000 demonstrations and more than 15,000 real rollouts.
  - Generalisation follows a "roughly power-law relationship with the number of environments and objects".
  - Diversity matters "far more" than demonstration count, which saturates past a per-environment threshold.
  - Source: [arXiv 2410.18647](https://arxiv.org/abs/2410.18647).
- HPT (MIT/Meta, Sep 2024) [PREPRINT] studies scaling of heterogeneous pretraining across embodiments — [arXiv 2409.20537](https://arxiv.org/abs/2409.20537).
- TRI LBM [PEER]: "performance predictably increases as pretraining scale and diversity grows"; benefits "appear far before" internet scale — [arXiv 2507.05331](https://arxiv.org/abs/2507.05331); [TRI LBM](https://toyotaresearchinstitute.github.io/lbm1/).
- AgiBot GO-1 claims "predictable performance scaling with increased data volume" — [arXiv 2503.06669](https://arxiv.org/abs/2503.06669).
- GEN-0 claims "strong scaling laws" and an ossification "phase transition" at about 7B parameters, with more than 270k hours of data. GEN-1 reports 500k hours [COMPANY] — [GEN-0](https://generalistai.com/blog/gen-0); [GEN-1](https://generalistai.com/blog/gen-1).
- PI says human-to-robot transfer "emerges" with robot-data scale [COMPANY] — [PI](https://www.pi.website/research/human_to_robot).
- Counterpoints:
  - π0's authors note "it remains unclear how to predict how much and what kind of data is needed to attain near-perfect performance" — [π0 paper](https://arxiv.org/html/2410.24164v1).
  - A Bytedance Seed paper (Jul 2026) says scaling laws for learning from real-world environments after deployment are "far less understood" — [EdgeBench 2607.05155](https://www.alphaxiv.org/abs/2607.05155).
  - A representation-centric paper (Aug 2026) argues for gains "beyond data scaling" — [alphaXiv 2608.27550](https://www.alphaxiv.org/abs/2608.27550).

**Cross-embodiment transfer**
- RT-X showed positive transfer across 22 robots — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864).
- Octo and OpenVLA fine-tune to new embodiments — [arXiv 2405.12213](https://arxiv.org/abs/2405.12213); [arXiv 2406.09246](https://arxiv.org/abs/2406.09246).
- Gemini Robotics 1.5 "Motion Transfer" — [arXiv 2510.03342](https://arxiv.org/abs/2510.03342).
- GR2 adapts On-Device to new bi-arm robots with fewer than 200 examples, and one checkpoint controls Apollo with two different hands and a Franka Duo [COMPANY] — [DeepMind GR2 blog](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/).
- π0.7 does zero-data laundry folding on a UR5e [COMPANY] — [PI π0.7](https://www.pi.website/blog/pi07).
- π0's own caveat: "it remains to be seen how much positive transfer there is in combining highly diverse data" — [π0 paper](https://arxiv.org/html/2410.24164v1).

**Long-horizon tasks**
- π0.5 cleans kitchens and bedrooms in new homes — [arXiv 2504.16054](https://arxiv.org/abs/2504.16054).
- PI's MEM handles tasks up to about 15 minutes and notes "causal confusion" risks from naive memory — [PI MEM](https://www.pi.website/research/memory).
- Helix 02's 4-minute, 61-action task — [Figure](https://www.figure.ai/news/helix-02).
- GR2 tasks of "several minutes… hundreds of decisions" — [DeepMind](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/).
- V-JEPA 2 planning is limited to about 16 s horizons — [V-JEPA 2](https://arxiv.org/html/2506.09985v1).
- TRI reports LBM gains on novel long-horizon tasks (apple coring, bike-rotor install) — [TRI LBM](https://toyotaresearchinstitute.github.io/lbm1/).

**Dexterity**
- DeepMind GR2: "the multi-finger dexterous manipulation remains challenging" — [DeepMind GR2 blog](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/).
- Helix 02 uses fingertip tactile sensing (3 g) and palm cameras for pill extraction and syringe dosing; Figure says this is the first time its policies depend on these modalities — [Figure](https://www.figure.ai/news/helix-02).
- PI Robot Olympics: 52% average success; two gold tasks were "physically impossible for our robot" because of the gripper — [PI](https://www.pi.website/blog/olympics).
- Brooks: robots lack anything like the human hand's touch sensing, there is no data "tradition for touch", and video and teleoperation data are crude in force and touch [OPINION] — [Brooks essay](https://rodneybrooks.com/why-todays-humanoids-wont-learn-dexterity/); [TechCrunch](https://techcrunch.com/2025/09/26/famed-roboticist-says-humanoid-robot-bubble-is-doomed-to-burst).
- A 2026 VLA post-training study targets high-DoF dexterous hands — [alphaXiv 2609.19666](https://www.alphaxiv.org/abs/2609.19666).

### Inferences
- The scaling-law question has moved from "do they exist?" to "what is the scaled variable?". Candidates are hours of diverse, especially human-wearable, interaction data, environment and object diversity, and autonomous RL experience. Model size may also need a threshold, per GEN-0's ossification claim.
- Publicly verifiable scaling evidence (Lin et al. 2024, TRI LBM) is small-scale, at thousands of hours. The 100k+ hour claims are proprietary. For forecasting, treat robot "scaling laws" as plausible but unverified at frontier scale.
- Dexterity and tactile sensing are the likeliest bottleneck to persist to 2030. Both pro-scaling labs (DeepMind) and sceptics (Brooks) identify multi-finger contact-rich manipulation as unsolved, and the hardware (tactile hands) is only arriving in 2025–26 (Figure 03, SharpaWave).

### Gaps
- I found no peer-reviewed robot scaling law with fitted exponents at more than 10k hours. GEN-0's curves are on company pages.
- I found no independent long-horizon benchmark with minutes-long tasks evaluated blind across labs.
- I did not read Benjie Holson's original Robot Olympics essay (only PI's description of it).

---

## Q7. How the research frontier shifted, about 2022 to 2026 (synthesis for forecasting)

### Takeaway
The frontier moved in five steps:
- **2022–23**: single-lab, large-teleoperation-fleet transformers (RT-1), web-knowledge VLAs (RT-2), and generative imitation (Diffusion Policy, ACT).
- **2023–24**: open, cross-embodiment datasets and models (OXE, Octo, OpenVLA), cheap hardware and data interfaces (ALOHA, UMI), and the first flow-matching VLA (π0).
- **2025**: hierarchical generalists with open-world claims (π0.5, Gemini Robotics, GR00T N1, Helix), mature humanoid whole-body RL, and rigorous-evaluation pushback (TRI LBM, STAR-Gen, LIBERO-Plus).
- **Late 2025–2026**: RL post-training and learning from experience (π*0.6, RL Tokens), heterogeneous and human data at hundreds of thousands of hours (GEN-0/1), compositional and steerable generalists (π0.7), world-action models (Cosmos Policy and Cosmos 3), and whole-body humanoid VLAs (Helix 02, Gemini Robotics 2).
- **By Oct 2026**: commercial API access to foundation models (Pi API beta).

### Cited Findings
- 2022–23:
  - RT-1 used 130k episodes from 13 robots over 17 months — [RT-1](https://robotics-transformer1.github.io/).
  - RT-2's action-as-text VLA — [arXiv 2307.15818](https://arxiv.org/abs/2307.15818).
  - Diffusion Policy — [arXiv 2303.04137](https://arxiv.org/abs/2303.04137).
  - ACT — [arXiv 2304.13705](https://arxiv.org/abs/2304.13705).
- 2023–24:
  - OXE — [arXiv 2310.08864](https://arxiv.org/abs/2310.08864).
  - Octo — [arXiv 2405.12213](https://arxiv.org/abs/2405.12213).
  - OpenVLA — [arXiv 2406.09246](https://arxiv.org/abs/2406.09246).
  - UMI — [arXiv 2402.10329](https://arxiv.org/abs/2402.10329).
  - π0 — [arXiv 2410.24164](https://arxiv.org/abs/2410.24164).
- 2025:
  - π0.5 — [arXiv 2504.16054](https://arxiv.org/abs/2504.16054).
  - Gemini Robotics — [arXiv 2503.20020](https://arxiv.org/abs/2503.20020).
  - GR00T N1 — [arXiv 2503.14734](https://arxiv.org/abs/2503.14734).
  - Helix — [Figure](https://www.figure.ai/news/helix).
  - TRI LBM — [arXiv 2507.05331](https://arxiv.org/abs/2507.05331).
  - LIBERO-Plus — [arXiv 2510.13626](https://arxiv.org/abs/2510.13626).
- 2025–26:
  - π*0.6 — [arXiv 2511.14759](https://arxiv.org/abs/2511.14759).
  - GEN-0 — [Generalist](https://generalistai.com/blog/gen-0).
  - Helix 02 — [Figure](https://www.figure.ai/news/helix-02).
  - Cosmos Policy — [arXiv 2601.16163](https://arxiv.org/abs/2601.16163).
  - RLT — [PI](https://www.pi.website/research/rlt).
  - GEN-1 — [Generalist](https://generalistai.com/blog/gen-1).
  - π0.7 — [PI](https://www.pi.website/blog/pi07).
  - Cosmos 3 — [arXiv 2606.02800](https://arxiv.org/abs/2606.02800).
  - Gemini Robotics 2 — [DeepMind](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/).
  - Pi API beta — [PI](https://www.pi.website/blog/api-beta).
- Data scale moved from about 130k episodes (RT-1) to about 1M trajectories (OXE, AgiBot World), then about 10k hours (π0), about 1.7k hours with rigorous evaluation (TRI), and about 270k–500k hours claimed (GEN-0/GEN-1) — sources as above.

### Inferences (for the 2030 forecast)
- **Likely continuations**, given strong multi-source momentum:
  - RL and experience-based post-training becomes standard.
  - Human wearable and egocentric data becomes a major pretraining source.
  - Hybrid VLA/world-model backbones.
  - Memory and hierarchical agents for tasks of tens of minutes or more.
  - Foundation-model-as-a-service distribution (Pi API, Gemini ER in AI Studio, open GR00T and Cosmos).
- **Key uncertainties**:
  - Whether proprietary scaling claims hold up under independent evaluation.
  - Multi-finger and tactile dexterity.
  - Real-world reliability (99%+ over long deployments).
  - Reward specification for RL at scale.
  - Safety and alignment of emergent physical behaviour, raised explicitly by GEN-1 and DeepMind's ASIMOV-Agentic.
- **Evidence-quality warning**: the frontier has shifted toward company blogs with videos and self-selected metrics. Peer-reviewed confirmation lags by about 6–12 months (for example, π0 was released Oct 2024 and appeared at RSS 2025, and TRI's LBM was posted Jul 2025 and published in Science Robotics in 2026). Forecasts should weight independent evaluations such as RoboArena, LIBERO-Plus and STAR-Gen.

### Gaps
- No single primary source quantifies the industry-wide total of robot data or compute.
- Investment and funding figures were not verified. Search snippets gave conflicting PI valuations, so they are excluded.
