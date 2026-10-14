# DP158 source-matched scalar simulation: prospective exploratory protocol

Recorded 2026-10-13 UTC before the run below. This is **not confirmatory**: earlier 1,000-path diagnostic output using different budget accounting and already-consumed seeds prompted the source audit. The original preregistration is explicitly withdrawn, and no numerical gate from it will be reused as a confirmatory test.

Source: Tran et al., *f-Differential Privacy Filters: Validity and Approximate Solutions*, arXiv:2602.06756v2, main-text budget formula, Algorithm 2, Appendix G.2 and Figure 12: https://arxiv.org/html/2602.06756v2

Run a one-dimensional scalar remove pair at `q=.1`, `T=120`, `sigma_0=8`, `sigma_min=2`, `C_0=1`, `B=2000 * q²/2 * (exp(1/sigma_0²)-1)`, with `N=1,000,000` independent trajectories per P and Q arm. Use NumPy PCG64 seeds P=260315 and Q=260316, one fixed run, no seed replacement. Output `results/dp158_filter_source_matched_q01/analysis.json`. Compare halt rate, mean active steps, PLRV mean/variance, and empirical-CDF distance to the published figure; report every deviation without a success/failure gate.

The code uses exact mixture log-likelihood ratios but the paper's **approximate** budget formula and its algebraic inverse. At zero history, set `sigma_1=sigma_0` and `C_1=C_0` to avoid division by zero; Appendix G.2 explicitly discusses the ceiling for the first step but does not spell out the clipping convention. It also writes `y_i²` without clarifying scalar output versus vector shorthand. These assumptions can affect exact reproduction. The paper does not provide linked executable simulation code; this remains an independent one-dimensional instantiation, not a claim of author-code reproduction or of a privacy theorem counterexample.

Command: `python3.12 scripts/reproduce_dp158_q01_filter.py --budget-model paper_small_q --dimension 1 --trajectories 1000000 --seed-p 260315 --seed-q 260316 --output results/dp158_filter_source_matched_q01/analysis.json`.
