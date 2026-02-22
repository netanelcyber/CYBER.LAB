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
    # Optional risk modifiers
    cvss_score: float = 5.0  # CVSS v3 score (0-10)
    users_with_access: int = 1  # count of users who can access the position/system
    priv_esc_prob: float = 0.0  # estimated probability of privilege escalation (0-1)

    def lambda_total(self) -> float:
        if self.n_policies <= 0:
            raise ValueError("n_policies must be positive")
        if self.base_rate_per_policy < 0:
            raise ValueError("base_rate_per_policy must be >= 0")
        if self.trend_factor <= 0:
            raise ValueError("trend_factor must be positive")

        # CVSS multiplier: maps 0-10 -> ~1.0-2.0 (linear)
        cvss = float(self.cvss_score)
        if cvss < 0 or cvss > 10:
            raise ValueError("cvss_score must be in [0,10]")
        cvss_mult = 1.0 + (cvss / 10.0)

        # Access multiplier: more users with access increases likelihood (log scaling)
        users = int(self.users_with_access)
        if users < 0:
            raise ValueError("users_with_access must be >= 0")
        access_mult = 1.0 + (np.log1p(users) / 5.0)

        # Privilege escalation multiplier: linear mapping from probability to factor (0->1,1->3)
        pe = float(self.priv_esc_prob)
        if pe < 0.0 or pe > 1.0:
            raise ValueError("priv_esc_prob must be in [0,1]")
        priv_mult = 1.0 + 2.0 * pe

        adjusted_rate = float(self.base_rate_per_policy) * cvss_mult * access_mult * priv_mult
        return float(self.n_policies) * adjusted_rate * float(self.trend_factor)


def sample_poisson(freq: PoissonFrequency, rng: np.random.Generator) -> int:
    return int(rng.poisson(lam=freq.lambda_total()))
