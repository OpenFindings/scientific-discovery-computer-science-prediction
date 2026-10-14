# DP158 next experiment: regime-boundary diagnostic, not a privacy certificate

Recorded 2026-10-14 UTC before any boundary-rate simulation. This is a proposed **new** experiment; no results are claimed here.

Primary sources: Tran et al., arXiv:2602.06756v2 (Theorem 4.2, Algorithm 2, Appendix G.2), https://arxiv.org/html/2602.06756v2; Feldman and Zrnic, NeurIPS 2021 Theorem 4.3, https://papers.nips.cc/paper/2021/file/ec7f346604f518906d35ef0492709f78-Paper.pdf.

## Frozen diagnostic design

Use independent one-dimensional subsampled Gaussian remove-neighbor mechanisms and the published adaptive `sigma_t/C_t` schedule. Set `sigma_0=8`, `sigma_min=2`, `C_0=1`, `T=120`, and `B(q)=2000*Budg(0,q,8,1)` with the paper's explicit small-q budget. Compare `q∈{0.1,0.19,0.3,0.5}` at 1,000,000 terminal PLRV paths per P and Q arm. In that q order, freeze fresh NumPy PCG64 seed pairs `(P,Q)=(260500,260501),(260502,260503),(260504,260505),(260506,260507)` before execution. Preserve every q, not only positive contrasts.

Primary diagnostic is the maximum P/Q empirical-CDF distance to `N(±B,2B)`; use a simultaneous Dvoretzky–Kiefer–Wolfowitz bound for the eight empirical CDFs (familywise alpha .05) to separate Monte Carlo noise from changes in mismatch. A boundary contrast is practically material only if the lower confidence bound for the larger-q discrepancy minus the upper bound for q=.1 exceeds .01. Record halt rates, active steps, moments and assumptions as secondary outcomes.

This tests the approximation's empirical behavior in one implementation, **not** whether Theorem 4.2 is false at finite q. Its theorem is asymptotic and does not promise an exact finite-q threshold. A measured discrepancy cannot establish any deployed accountant undercount.

## Valid fallback and comparison gate

The local `research_platform.rdp_filter_reference` uses a per-step revealed-coin upper bound for both directions of fixed-order RDP and Feldman–Zrnic's pre-release pathwise-sum stopping rule. Test that every adaptive path keeps the sum of theoretical upper charges at or below its frozen RDP budget. This checks the implementation, not its mathematical proof or numerical certification.

Do **not** compare active-step counts against the approximate GDP filter as a claim of better privacy–utility until both are converted to the same adjacency, `(epsilon,delta)` target, and finite-q error accounting. Google `dp-accounting` can supply fixed-schedule per-step calculations, but ordinary composition is not itself a fully adaptive filter. If matched guarantees or exact pairwise privacy metrics cannot be computed with certified error, report the comparison as unexecuted and retain only the boundary diagnostic.

Falsification/stop conditions: reject any local RDP implementation that releases a step whose validated theoretical charge would push the path above its budget; reject any proposed fixed `q` guard threshold as a **formal guarantee** if it lacks a finite-q theorem or a certified worst-case privacy calculation. Report inconclusive data honestly, with no seed replacement or optional stopping.
