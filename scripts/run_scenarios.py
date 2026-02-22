from __future__ import annotations

import sys
from pathlib import Path

# Allow running without installing the package (adds ./src to sys.path)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from cyber_actuary.config import ScenarioParams, default_benchmarks
from cyber_actuary.frequency import PoissonFrequency
from cyber_actuary.metrics import summarize_tail
from cyber_actuary.mixture import MixtureSeverity
from cyber_actuary.portfolio import PortfolioScenario, simulate_many_years
from cyber_actuary.report import write_csv, write_json
from cyber_actuary.severity import (
    calibrate_lognormal_from_mean,
    fit_lognormal_mu_sigma_from_mean_and_var99,
)


def main() -> None:
    out_dir = Path("artifacts")
    b = default_benchmarks()
    p = ScenarioParams()  # edit src/cyber_actuary/config.py to change assumptions

    # --- Severity calibration (typical) ---
    mean_typical = b.ibm_global_avg_breach_cost_usd_2025
    typical = calibrate_lognormal_from_mean(mean_x=mean_typical, sigma=p.sigma_typical)

    # "AI savings" scenario: mean reduced by configured amount (floor at >0)
    mean_ai = max(1.0, mean_typical - b.ai_savings_usd)
    typical_ai = calibrate_lognormal_from_mean(mean_x=mean_ai, sigma=p.sigma_typical)

    # --- Mega-breach severity calibration (stress) ---
    mega = fit_lognormal_mu_sigma_from_mean_and_var99(
        mean_x=p.mega_mean_usd,
        var99_x=p.mega_var99_target_usd,
    )

    sev_base = MixtureSeverity(typical=typical, mega=mega, p_mega=p.mixture_p_mega)
    sev_ai = MixtureSeverity(typical=typical_ai, mega=mega, p_mega=p.mixture_p_mega)

    # --- Frequency trend factor from ITRC ---
    ref = b.itrc_compromises_by_year[p.itrc_reference_year]
    itrc_2024 = b.itrc_compromises_by_year.get(2024, ref)
    itrc_2025 = b.itrc_compromises_by_year.get(2025, ref)

    trend_2024 = itrc_2024 / ref
    trend_2025 = itrc_2025 / ref

    # --- Portfolio simulations ---
    n_years = 50_000  # Monte Carlo size

    scenarios = []
    for year, trend in [(2024, trend_2024), (2025, trend_2025)]:
        freq = PoissonFrequency(
            n_policies=p.n_policies,
            base_rate_per_policy=p.base_annual_incident_rate_per_policy,
            trend_factor=trend,
        )

        for label, sev in [("BASE", sev_base), ("AI", sev_ai)]:
            seed = p.random_seed + year + (0 if label == "BASE" else 1)
            scn = PortfolioScenario(frequency=freq, severity=sev, seed=seed)
            sims = simulate_many_years(scn, n_years=n_years)
            agg = sims["agg_loss"]

            summary = summarize_tail(agg, alphas=(0.90, 0.95, 0.99))
            summary.update(
                {
                    "scenario": label,
                    "year": year,
                    "n_years_mc": n_years,
                    "lambda_total": freq.lambda_total(),
                    "p_mega": sev.p_mega,
                    "typical_mean": sev.typical.mean(),
                    "mega_mean": sev.mega.mean(),
                    "trend_factor": trend,
                }
            )
            scenarios.append(summary)

    df = pd.DataFrame(scenarios)
    write_csv(out_dir / "scenario_summaries.csv", df)
    write_json(out_dir / "scenario_summaries.json", {"rows": scenarios})

    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
