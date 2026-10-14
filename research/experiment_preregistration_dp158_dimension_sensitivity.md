# Preregistration: dimensional sensitivity in the DP158 q=0.1 Monte Carlo

> **Post-run source-audit correction, 2026-10-13 UTC (not part of the preregistration):** Appendix G.2 writes `y_i^2`, without an explicit vector norm or output dimension, while the main algorithm permits vector outputs; that notation alone does not settle whether the authors intended a scalar simulation or vector shorthand. More decisively, the paper explicitly defines `Budg(0,q,sigma,mu)=q^2/2*(exp(mu^2/sigma^2)-1)`, whereas this sweep used exact one-step mixture KL. Its numbers are valid only for that independent vector-output model; they are **not** a paper reproduction or evidence of an omitted-parameter reporting gap. The original plan is preserved below as an audit trail.

- **Study ID:** `EXP-DP158-DIMENSION-SENSITIVITY-2026`
- **Registered:** 2026-10-13 UTC, before this sensitivity block.
- **Motivation:** An implementation smoke test with 1,000 one-dimensional trajectories did not closely match the paper's reported stop rate. The paper's adaptive schedule depends on `sum_i ||y_i||^2` for vector-valued Gaussian outputs, but Appendix G.2 does not report the output dimension. That smoke is diagnostic only, not confirmatory and not retained as the confirmatory sample.
- **Question:** How much do the reported halt rate, mean stopping step, PLRV moments, and Gaussian-CDF discrepancies depend on the omitted output dimension, holding all reported parameters fixed?
- **Scope:** Sensitivity analysis of an independent implementation. Not a production-accountant audit, not proof of a privacy failure, and not a theorem claim.

## Frozen setup

- Use the parameters explicitly reported for Figure 12: `q=0.1`, `T=120`, `sigma_0=8`, `sigma_min=2`, `C_0=1`, and `B=2000*Budg(q,sigma_0,1)`.
- Sweep output dimensions `[1, 2, 4, 8, 16]`; the privacy-loss signal affects one coordinate and the remaining coordinates contribute independent Gaussian noise to the adaptive norm, matching a one-record neighboring pair with zero unaffected-data mean.
- Run 100,000 independent trajectories per arm and dimension. Use NumPy PCG64 seeds `P=261000+2*d`, `Q=261001+2*d`; no replacement or optional stopping.
- Preserve halt probability, censored-at-T probability, mean active steps, PLRV mean/variance, and max empirical CDF distance to `N(+B,2B)`/`N(-B,2B)`.
- Reproduce the paper's published targets as reference points, but report the entire dimension curve; do not select the dimension that best matches the paper and then treat it as confirmation.

## Decision rules

- The dimension is practically material in this simulation if the max-minus-min halt probability across the frozen sweep is at least 0.01 or the mean active-step range is at least 1.0.
- A close numerical match is not evidence of an error in the theorem or any deployed accountant. If the output dimension is a material undocumented dependency, the conclusion is limited to a reproducibility/reporting gap until the authors' exact code/configuration is located.
- This exploratory sweep does not use a p-value to generalize beyond the specified simulation. Include Monte Carlo uncertainty intervals for halt rates in the report.

## Reproduction command

Run each arm/dimension from a wrapper that passes the frozen dimension and seeds to `scripts/reproduce_dp158_q01_filter.py`; save a distinct JSON artifact per dimension. Keep the initial one-dimensional smoke test out of the confirmatory results directory.
