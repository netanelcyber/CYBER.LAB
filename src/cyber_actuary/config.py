from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Benchmarks:
    """
    Public benchmark calibration anchors (configure as needed).

    - IBM 'Cost of a Data Breach' style mean cost (used as a *target mean*).
    - AI/automation savings: modeled as a *mean reduction* (delta).
    - ITRC compromise counts: used only as a trend scaler for frequency (NOT per-org frequency).
    """
    ibm_global_avg_breach_cost_usd_2025: float = 4.4e6
    ai_savings_usd: float = 1.9e6

    itrc_compromises_by_year: Optional[Dict[int, int]] = None


@dataclass(frozen=True)
class ScenarioParams:
    """
    Actuarial scenario parameters.

    - sigma_typical: tail heaviness for typical breach lognormal
    - mixture_p_mega: probability an incident is a mega event (tail component)
    - mega_mean_usd + mega_var99_target_usd: stress calibration anchors for mega component
    """
    sigma_typical: float = 1.0

    mixture_p_mega: float = 0.005  # 0.5% of incidents are mega events (assumption)

    mega_mean_usd: float = 1.0e8  # 100M mean megabreach loss (assumption)
    mega_var99_target_usd: float = 3.5e8  # 350M VaR99 stress target (assumption)

    n_policies: int = 10_000
    base_annual_incident_rate_per_policy: float = 0.02  # 2% expected incidents per policy-year
    itrc_reference_year: int = 2024  # scale frequency by ITRC trend vs this year

    random_seed: int = 42


def default_benchmarks() -> Benchmarks:
    b = Benchmarks()
    object.__setattr__(
        b,
        "itrc_compromises_by_year",
        {
            2024: 3152,
            2025: 3322,
        },
    )
    return b
