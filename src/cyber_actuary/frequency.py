from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PoissonFrequency:
    """
    Portfolio frequency model:
      N ~ Poisson(lambda_total)
    where lambda_total = n_policies * rate_per_policy * trend_factor
    """
    n_policies: int
    base_rate_per_policy: float
    trend_factor: float

    def lambda_total(self) -> float:
        if self.n_policies <= 0:
            raise ValueError("n_policies must be positive")
        if self.base_rate_per_policy < 0:
            raise ValueError("base_rate_per_policy must be >= 0")
        if self.trend_factor <= 0:
            raise ValueError("trend_factor must be positive")
        return float(self.n_policies) * float(self.base_rate_per_policy) * float(self.trend_factor)


def sample_poisson(freq: PoissonFrequency, rng: np.random.Generator) -> int:
    return int(rng.poisson(lam=freq.lambda_total()))
