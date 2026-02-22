from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .frequency import PoissonFrequency
from .mixture import MixtureSeverity, sample_mixture


@dataclass(frozen=True)
class PortfolioScenario:
    """
    One-year aggregate loss simulation for a portfolio.
    """
    frequency: PoissonFrequency
    severity: MixtureSeverity
    seed: int = 42


def simulate_one_year(scn: PortfolioScenario) -> Tuple[int, float]:
    rng = np.random.default_rng(scn.seed)
    n_events = int(rng.poisson(lam=scn.frequency.lambda_total()))
    if n_events == 0:
        return 0, 0.0
    losses = sample_mixture(scn.severity, n_events, rng)
    return n_events, float(losses.sum())


def simulate_many_years(scn: PortfolioScenario, n_years: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(scn.seed)
    events = np.zeros(n_years, dtype=int)
    agg = np.zeros(n_years, dtype=float)

    lam = scn.frequency.lambda_total()
    for y in range(n_years):
        n_events = int(rng.poisson(lam=lam))
        events[y] = n_events
        if n_events > 0:
            agg[y] = float(sample_mixture(scn.severity, n_events, rng).sum())
        else:
            agg[y] = 0.0

    return {"n_events": events, "agg_loss": agg}
