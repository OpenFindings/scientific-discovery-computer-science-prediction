# Assistant judgement: CS directions 2025 → 2030 (unvalidated, registered for scoring)

Written 2026-10-17 by the assistant (Claude) as **judgement, not a model output**. It is
registered so it can be scored against the direction-forecast system in 2031, with the same target
as `research/preregistration_cs_direction_forecast_v1.md`: CS-relative log growth of
primary-topic works from 2025 to 2030, scored among the eligible topics in
`prospective_2030.csv`.

Caveats: this judgement can reflect remembered hype rather than insight, which is the failure
found for LLM raters in amendment 4. The assistant's knowledge extends past the 2025 origin
(into 2026), which is a small head start the system did not have. Growth is not research value
and not a breakthrough.

## Predicted in the TOP QUARTILE of relative growth (2025 → 2030)

| Topic | System rank (of 270) | Reasoning |
|---|---|---|
| T10142 Formal Methods in Verification | 152 | LLM-assisted proof and verified code generation makes formal methods cheaper |
| T10462 Reinforcement Learning in Robotics | 77 | Data-scaled robot learning and robot foundation models |
| T10211 Computational Drug Discovery Methods | 204 | AI-for-science transfer from structure prediction to design |
| T10456 Multi-Agent Systems and Negotiation | 28 | LLM agent systems revive multi-agent coordination |
| T10682 Quantum Computing Algorithms and Architecture | 30 | Error-correction milestones pull algorithm and architecture work |
| T14098 Energy Efficiency in Computing | 5 | AI compute energy constraints |
| T12026 Explainable Artificial Intelligence (XAI) | 19 | Regulation and model auditing |
| T11424 Security and Verification in Computing | 76 | Agent and LLM security, supply-chain verification |

## Predicted in the BOTTOM HALF

| Topic | System rank | Reasoning |
|---|---|---|
| T10270 Blockchain Technology Applications and Security | 207 | Post-hype decline continues |
| T10775 Generative Adversarial Networks and Image Synthesis | 16 | GAN-specific work keeps shrinking as diffusion and autoregressive models replace it |

## Scoring rule (fixed now)

Hit rate is the fraction of the 10 claims that land in the stated half or quartile. The system's
claims on the same 10 topics are scored with the same rule, taking the system as predicting the
top quartile for ranks 1–67 and the bottom half for ranks 136–270. Both hit rates are reported
together. The disagreement topics (T10142, T10211 and T10775) are the informative ones.
