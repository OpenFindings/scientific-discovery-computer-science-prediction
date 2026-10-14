# Preregistration: independent reproduction of the q=0.1 approximate-GDP filter simulation

> **Pre-execution source-audit amendment, 2026-10-13 UTC:** An implementation smoke test had already used the frozen seeds, and source review showed that this plan misidentified the paper's explicit small-`q` approximation `Budg` as exact mixture KL. No million-path run was executed under this plan. It is withdrawn as a confirmatory preregistration; neither its seeds nor gate may be used to claim confirmation. See the later source-matched exploratory protocol and raw outputs. The original text below is retained unaltered as an audit trail.

- **Study ID:** `EXP-DP158-GDP-FILTER-Q01-REPRO-2026`
- **Registered:** 2026-10-13 UTC, before confirmatory simulation.
- **Primary source:** Tran et al., *f-Differential Privacy Filters: Validity and Approximate Solutions*, arXiv:2602.06756v2, Appendix G.2 and Figure 12/Table 3.
- **Question:** Can an independent implementation of the paper's fully adaptive subsampled-Gaussian filter reproduce its reported q=0.1 stopping behavior, PLRV moments and Gaussian-CDF discrepancy?
- **Scope:** Reproduce the published simulation only. This does not audit any production privacy accountant, prove the filter invalid, or establish a general privacy failure.

## Frozen design

- Fixed `q=0.1`, `T=120`, `sigma_0=8`, `sigma_min=2`, `C_0=1`, one-dimensional remove-neighbor sensitivity, and initial budget `B=2000 * Budg(q, sigma_0, 1)` using the exact one-step KL of the subsampled-Gaussian mixture.
- Simulate `N=1,000,000` independent trajectories under each arm, P and Q, using NumPy PCG64 seeds 260213 and 260214 respectively.
- Implement the paper's adaptive rule `sigma_t=clamp(sigma_0/sqrt(sum_{i<t} y_i^2), [sigma_min,sigma_0])`, `C_t=C_0/sqrt(sum_{i<t} y_i^2)`, budget-aware clipping, and stop when the remaining budget forces clipping below `C_t`.
- Evaluate exact mixture log-likelihood ratios. Compute the maximum two-sided empirical-CDF distance between each terminal PLRV sample and the corresponding `N(+B,2B)` or `N(-B,2B)` GDP PLRV.
- Use Gauss-Hermite quadrature to tabulate the one-step mixture KL and invert it by interpolation; preserve quadrature grid/resolution and approximation metadata. This is an independent implementation, not source-identical code.

## Outcomes and interpretation gate

Primary: P- and Q-arm maximum CDF discrepancies. Secondary: halt probability, mean active steps, PLRV mean/variance, and comparison with the paper's reported values.

The replication is considered numerically consistent if: (1) each arm halts on at least 97% of paths; (2) mean active steps are within 2.0 of 113.1; (3) each empirical PLRV mean/variance is within 0.02/0.04 of the respective published P/Q values; and (4) each CDF discrepancy is within 0.003 of its published value (P 0.01247, Q 0.01464). Report exact deviations regardless of this gate. These tolerances account for Monte Carlo error and independent quadrature/interpolation implementation.

## Integrity and limitations

- No exclusions, seed replacement, or optional stopping. Any implementation failure is reported and corrected before using the preregistered RNG seeds.
- The paper's appendix reports 1,000,000 trajectories and uses a peaks-over-threshold GPD tail fit for very small delta; this reproduction's primary CDF-distance analysis is the direct empirical PLRV CDF, not that tail-fit epsilon/delta curve.
- No production accountant or competing multi-order RDP baseline is evaluated. This reproduction alone is not evidence of a deployed undercount or a novel theorem.
- Reproduction command: `python3.12 scripts/reproduce_dp158_q01_filter.py --output results/dp158_filter_reproduction_q01/analysis.json`.
