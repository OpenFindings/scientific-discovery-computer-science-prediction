# Preregistration: forecasting "surprise risers" among CS directions (v1)

Frozen: 2026-10-17, **before this analysis is run**. It reuses the direction panel and data of
`research/preregistration_cs_direction_forecast_v1.md`; no new data. That study showed five-year
growth is mostly predictable from momentum. A breakthrough-like event is better described as
growth **well beyond what momentum predicts**. This study asks whether anything forecasts that.

## Target (frozen)

- For each test origin *t*, fit `G ~ g3` (ordinary least squares) on the training origins
  (≤ *t*−5). The residual on the test origin is `S = G − Ĝ`.
- **Label:** top-decile `S` within each origin, i.e. directions that took off unexpectedly.
- This is a proxy for surprise. It is not proof of a breakthrough: it can also come from
  reclassification, fads or external shocks.

## Scores (frozen; same rolling origins 2011–2019; trained on origins ≤ t−5)

- `ridge_resid_all`: ridge regression (α = 1) predicting `S` from all features (`log_p, g1, g3,
  g5, accel, share, breadth, diffusion, d_diffusion3, volatility`).
- `ridge_resid_nomomentum`: the same without `g1, g3, g5, accel`.
- Single-signal scores used directly: `accel`, `d_diffusion3`, `diffusion`, `volatility`, and
  `-log_p` (smaller directions).
- Plus `g3` (expected near 0.5 by construction) and `random`.

## Metrics and gates

- Pooled AUROC for the surprise label, with 2,000 topic-cluster bootstrap replicates, seed
  20261017. Per-origin AUROC is reported.
- **S1:** `ridge_resid_all` AUROC lower 95% bound > 0.5.
- **S2:** at least one single signal has an AUROC lower bound > 0.5. Every single signal is
  reported, and the multiple comparisons are stated next to the result.
- If S1 passes, register the 2025-origin ranking of surprise scores as a candidate list,
  evaluated on or after 2031-06-01 with the same target. If S1 fails, register nothing and report
  that surprises were not forecastable with these signals.

## Separate from this test

Any opinion by the assistant about likely breakthrough areas is reported separately and labelled
unvalidated judgement. It never enters a model and is not presented as a forecast of this system.

Code sha256 at freeze: `382b17ac6eb7d43a182a56a4c771bb29f92e5bef2ae3165c865b25c06ac00dec`.

## Addendum 1 (2026-10-17)

The first run crashed in the registration step after the backtest gates had been computed but not printed: an empty frame was passed to the residualizer. Only that line was changed, so the training set is residualized directly. The backtest code is unchanged. New code sha256: `d8704fa66ae717c0945682275c5a4bdaba3692225a21e1d4c123983cb99b9f0c`.

## Exploratory check (not preregistered, run after the frozen result)

Concern: small, volatile directions swing more, so the top-decile raw residual may favour them
mechanically. The residual was rescaled by a size-dependent expected spread fitted on training
origins (`log|S| ~ log_p`), and the ridge model was refit. Pooled AUROC fell from 0.674 to 0.618.
By origin, the AUROC fell from 0.66–0.76 (2011–2014) to 0.51–0.53 (2017–2019). Only nonlinear momentum
stayed strong (g3 0.727). Read the S1/S2 pass as mostly reflecting variance and momentum, not as
a forecast of breakthroughs. The registered surprise list should be read with that caveat.
