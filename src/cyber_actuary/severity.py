from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class LognormalParams:
    mu: float
    sigma: float

    def mean(self) -> float:
        return math.exp(self.mu + 0.5 * self.sigma**2)

    def median(self) -> float:
        return math.exp(self.mu)

    def var(self) -> float:
        m = self.mean()
        return (math.exp(self.sigma**2) - 1.0) * m**2

    def quantile(self, alpha: float) -> float:
        z = norm.ppf(alpha)
        return math.exp(self.mu + self.sigma * z)

    def tvar(self, alpha: float) -> float:
        """
        TVaR (Conditional Tail Expectation) for lognormal:
          TVaR_alpha = E[X | X > VaR_alpha]
                     = mean * Phi(sigma - z_alpha) / (1 - alpha)
        """
        z = norm.ppf(alpha)
        m = self.mean()
        tail = 1.0 - alpha
        return m * norm.cdf(self.sigma - z) / tail


def calibrate_lognormal_from_mean(mean_x: float, sigma: float) -> LognormalParams:
    """
    Solve mu from mean and sigma:
      mean = exp(mu + 0.5*sigma^2)  =>  mu = ln(mean) - 0.5*sigma^2
    """
    if mean_x <= 0:
        raise ValueError("mean_x must be positive")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    mu = math.log(mean_x) - 0.5 * sigma**2
    return LognormalParams(mu=mu, sigma=sigma)


def fit_lognormal_mu_sigma_from_mean_and_var99(mean_x: float, var99_x: float) -> LognormalParams:
    """
    Fit (mu, sigma) for a lognormal using two constraints:
      E[X] = mean_x
      VaR_0.99 = var99_x

    Solve for sigma numerically (bisection), then mu from mean.
    """
    if mean_x <= 0 or var99_x <= 0:
        raise ValueError("mean_x and var99_x must be positive")
    z99 = norm.ppf(0.99)

    def f(sigma: float) -> float:
        mu = math.log(mean_x) - 0.5 * sigma**2
        return math.exp(mu + sigma * z99) - var99_x

    lo, hi = 1e-6, 5.0
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        # Fallback: calibrate by mean only if bracket fails
        return calibrate_lognormal_from_mean(mean_x=mean_x, sigma=1.0)

    for _ in range(120):
        mid = 0.5 * (lo + hi)
        fmid = f(mid)
        if abs(fmid) < 1e-8:
            lo = hi = mid
            break
        if flo * fmid <= 0:
            hi, fhi = mid, fmid
        else:
            lo, flo = mid, fmid

    sigma = 0.5 * (lo + hi)
    mu = math.log(mean_x) - 0.5 * sigma**2
    return LognormalParams(mu=mu, sigma=sigma)


def sample_lognormal(params: LognormalParams, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.lognormal(mean=params.mu, sigma=params.sigma, size=n)
