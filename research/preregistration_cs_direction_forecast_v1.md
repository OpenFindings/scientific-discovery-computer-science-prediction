# Preregistration: CS research-direction growth forecast (v1)

Frozen: 2026-10-17, **before any topic-level data is retrieved**. This is a new unit of analysis:
OpenAlex research topics, not single papers. The paper-level study found that momentum dominates
(G2 failed; amendment 7). This study asks whether any direction-level signal beats momentum, and
registers a five-year forecast.

## Question

Using only data up to year *t*, can we rank existing CS research topics by their relative growth
over *t → t+5* better than simple momentum baselines?

## Units and data (frozen)

- **Topics:** the 302 OpenAlex topics with field Computer Science (`fields/17`), as listed on
  2026-10-17.
- Per topic and publication year 2000–2025, three counts (OpenAlex `group_by=publication_year`):
  - `P`: works whose primary topic is the topic.
  - `A`: works with the topic in any topic slot.
  - `X`: works with the topic in any slot whose primary topic is in a non-CS field. This is the
    cross-field diffusion count.
- Plus the total CS primary-topic works per year.
- **Known bias, stated now:** OpenAlex topics were defined around 2024 and assigned to older works
  retroactively, so the topic list itself uses hindsight. To limit this, a topic enters an origin
  only if `P_t ≥ 100` and `P_{t-5} ≥ 20`, so it already existed at size. The study therefore
  forecasts changes in existing directions. It cannot detect directions that did not yet exist.

## Target (frozen)

- `G = log((P_{t+5}+1)/(P_t+1)) − log(CS_{t+5}/CS_t)`: growth relative to all of CS.
- **Label:** top-decile `G` within each origin. These are the strongest risers.

## Features at origin t (years ≤ t only)

- Size: `log P_t`.
- Momentum: `g1, g3, g5` (log growth of P over 1, 3 and 5 years, CS-relative).
- Acceleration: `g3 − g3 lagged 3 years`.
- Share: `P_t / CS_t`.
- Breadth: `A_t / P_t`.
- Diffusion: `X_t / A_t` and its 3-year change.
- Volatility: standard deviation of yearly CS-relative growth over `t−5..t`.

## Models and baselines (frozen; no tuning)

- **Baselines:** `g1`, `g3` and `g5` used directly as scores, plus random.
- **Models:** `ridge_all` (standardised ridge regression on all features, α = 1, predicting `G`)
  and `gbm_all` (gradient boosting, 300 trees, depth 3, learning rate 0.05, seed 7).
  `ridge_nomomentum` uses all features except `g1`, `g3`, `g5` and acceleration; it tests the
  non-momentum signals alone.
- **Rolling origin:** test origins *t* = 2011…2019 (targets 2016…2024); train on origins ≤ *t*−5
  from 2006 on. Predictions are pooled over test origins.

## Metrics, uncertainty and gates

- Pooled AUROC for the top-decile label; Spearman correlation of score with `G` per origin; precision
  in the top 10%.
- 95% intervals from 2,000 bootstrap replicates resampling topics (clusters spanning origins),
  seed 20261017; paired differences use the same replicates.
- **F1:** `ridge_all` AUROC lower bound > 0.5.
- **F2:** `ridge_all` minus the best momentum baseline (best chosen on pooled AUROC) has ΔAUROC lower
  bound > 0.
- **F3:** `ridge_nomomentum` AUROC lower bound > 0.5. This asks whether non-momentum signals carry
  anything at all.
- **Descriptive:** per-origin results, especially origin 2019 (target 2024, which spans the LLM
  shift).

## Prospective registration (frozen)

- **Origin:** 2025. Train on all origins with mature targets (≤ 2020). Rank the eligible topics by
  each model and baseline, predicting relative growth 2025 → 2030.
- Before predicting, check 2025 completeness: if CS total 2025 / 2024 < 0.9, also register an
  origin-2024 version and flag 2025 as possibly incompletely indexed.
- Registered ranking: `results/cs_direction_forecast_v1/prospective_2030.csv`, with its sha256 in
  the manifest, committed and pushed before any post-2025 data exists in full. Evaluate on or after
  2031-06-01 with the same target.
- **The registered output is a ranking of existing directions by forecast relative growth.** It is
  not a list of breakthroughs and not a judgement of research value.

## Budget

At most 1,000 OpenAlex requests (free key). No paid calls.

Code sha256 at freeze: `scripts/run_cs_direction_forecast.py` `19dfde26079fd65b99fe787a869d26955c747454b772b6348a09b5191ce7eef5`.

## Addendum 1 (2026-10-17, after the fetch, before any backtest result)

Code bug fixed: the panel required 8 prior years (`o − 8 ≥ 2000`), but the deepest lag any
feature uses is 6 years (`P[o−6]`, for acceleration). With 8 years the first training origin
became 2008, contrary to the frozen 2006, and the 2011 test origin had no training data, so the
run crashed before producing results. The check is now `o − 6 ≥ 2000`, as frozen. Nothing else
changed. New code sha256: `1a5916b5ea38d7d2130f0c358548c4631c55ef57d5588f42b5c2f703eeee1156`. Data note: CS totals are 714,868 in 2024 and 903,012 in 2025
(ratio 1.26 ≥ 0.9), so the 2024 fallback origin does not apply.
