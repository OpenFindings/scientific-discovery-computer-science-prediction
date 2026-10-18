# Preregistration: robotics research-direction growth forecast (v1)

Frozen: 2026-10-18, **before any robotics topic-year data or the robotics topic list is
retrieved in this study**. It narrows `research/preregistration_cs_direction_forecast_v1.md` to
robotics. Robotics topics are spread over several OpenAlex fields (CS, Engineering, Medicine,
Social Sciences), so the topic set is chosen by name across all fields.

## Question

Using only data up to year *t*, can we rank robotics research topics by their growth over
*t → t+5*? Does anything beat momentum: a model trained on the 272-topic CS panel and transferred
to robotics, or a model trained on robotics alone?

## Units and data (frozen)

- **Topics:** OpenAlex `/topics?search=robot` (one request, 200 per page). Keep topics whose
  `display_name` contains "robot" (case-insensitive), across all fields.
  - **Excluded before seeing data:** "Robotic Process Automation Applications". It is software
    automation, not robots.
  - If the search returns other names that only contain "robot" by accident, they are kept anyway
    (the rule is mechanical) and flagged in the report.
- **Counts per topic and year, 2000–2025:**
  - `P`: primary-topic works.
  - `A`: any-slot works.
  - `X`: any-slot works whose primary topic is in a **different field from the topic's own
    field** (cross-field diffusion).
- **Normaliser:** the CS primary-topic total per year already retrieved for the CS study (no new
  request). Because it subtracts the same amount from every topic in an origin, it does not affect
  within-origin Spearman. It keeps features on the same scale as the CS panel used for transfer.
- **Eligibility:** `P_t ≥ 30` and `P_{t−5} ≥ 5`. This is relaxed from 100/20 because robotics
  topics are smaller.
- **Known biases:**
  - Topics were defined around 2024 and applied retroactively (hindsight topic list).
  - The set is small (expected about 15–20 topics), so per-origin rank statistics are noisy.
  - Topic labels come from a classifier and may drift.

## Target and metric (frozen)

- `G = log((P_{t+5}+1)/(P_t+1)) − log(CS_{t+5}/CS_t)`.
- With so few topics a top-decile label is not meaningful. The metric is the **per-origin
  Spearman correlation between score and `G`, averaged over test origins 2011–2019**.
- 95% intervals from 2,000 bootstrap replicates resampling topics (clusters across origins), seed
  20261017. Paired differences use the same replicates.

## Scores (frozen; no tuning)

- **Momentum baselines:** `g1`, `g3`, `g5`. The best of the three is chosen on its point
  estimate.
- **`ridge_transfer_cs` and `gbm_transfer_cs`:** the frozen CS-study ridge and GBM specifications,
  trained on CS panel origins ≤ *t*−5 and applied to robotics features.
- **`ridge_robotics`:** the same ridge specification trained on robotics panel origins ≤ *t*−5.

## Gates

- **R1:** the best momentum baseline has mean-Spearman lower bound > 0, i.e. robotics direction
  growth is forecastable at all.
- **R2:** `ridge_transfer_cs` minus the best momentum baseline has a lower bound > 0.
- **R3:** `ridge_robotics` minus the best momentum baseline has a lower bound > 0.

## Prospective registration (frozen)

- Origin 2025: train on origins ≤ 2020 and rank the eligible robotics topics by every score.
- The **primary registered ranking is `ridge_transfer_cs`**, whatever the gates say. The gates
  decide how much it should be trusted; if R2 fails, the report says momentum is as good.
- Output: `results/robotics_direction_forecast_v1/prospective_2030.csv`, with its sha256, pushed
  before 2030 data exist. Evaluate on or after 2031-06-01 with the same target, using Spearman.
- This is a ranking of existing robotics directions by forecast growth, not breakthroughs or
  research value.

## Budget

At most 300 OpenAlex requests (free key; expected about 60). No paid calls.

Code sha256 at freeze: `scripts/run_robotics_direction_forecast.py`
`541ff0bf456db2bc274ed46154202fd0600441c08f2036e70a3bcd0612b0f9d6`.
