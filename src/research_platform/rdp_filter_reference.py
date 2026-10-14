"""Reference fully adaptive RDP filter for a remove-neighbor Gaussian mixture.

This is a theorem-backed *formula* and a test reference, not a certified
floating-point accountant or a production implementation. See Feldman and
Zrnic (NeurIPS 2021), Theorem 4.3, and the module documentation in
reports/dp158_accountant_audit.json.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


def revealed_coin_rdp_upper(alpha: float, q: float, signal_to_noise: float) -> float:
    """Upper-bound both directions' order-alpha RDP by revealing sample coin.

    For P=(1-q)N(0,1)+qN(r,1), Q=N(0,1), augment both with the same
    Bernoulli(q) coin. At C=0 the conditional pair agrees; at C=1 its
    RDP in either direction is alpha*r**2/2. Forgetting C is postprocessing.
    """
    if not math.isfinite(alpha) or alpha <= 1:
        raise ValueError("alpha must be finite and greater than 1")
    if not math.isfinite(q) or not 0 <= q <= 1:
        raise ValueError("q must be in [0,1]")
    if not math.isfinite(signal_to_noise) or signal_to_noise < 0:
        raise ValueError("signal_to_noise must be finite and nonnegative")
    if q == 0 or signal_to_noise == 0:
        return 0.0
    gaussian_rdp = alpha * signal_to_noise**2 / 2.0
    if q == 1:
        return math.nextafter(gaussian_rdp, math.inf)
    exponent = (alpha - 1.0) * gaussian_rdp
    if exponent < 700:
        log_moment = math.log1p(q * math.expm1(exponent))
    else:
        log_moment = math.log(q) + exponent + math.log1p((1.0 - q) / q * math.exp(-exponent))
    return math.nextafter(log_moment / (alpha - 1.0), math.inf)


@dataclass
class FixedOrderRdpFilter:
    """Pre-release pathwise sum filter at one frozen RDP order and budget."""

    alpha: float
    budget: float
    charges: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not math.isfinite(self.budget) or self.budget < 0:
            raise ValueError("budget must be finite and nonnegative")
        if not math.isfinite(self.alpha) or self.alpha <= 1:
            raise ValueError("alpha must be finite and greater than 1")

    @property
    def spent(self) -> float:
        return math.fsum(self.charges)

    def try_release(self, q: float, signal_to_noise: float) -> bool:
        charge = revealed_coin_rdp_upper(self.alpha, q, signal_to_noise)
        if math.fsum((*self.charges, charge)) > self.budget:
            return False
        self.charges.append(charge)
        return True
