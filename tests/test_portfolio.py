import numpy as np

from cyber_actuary.frequency import PoissonFrequency
from cyber_actuary.mixture import MixtureSeverity
from cyber_actuary.portfolio import PortfolioScenario, simulate_many_years
from cyber_actuary.severity import calibrate_lognormal_from_mean


def test_portfolio_simulation_shapes():
    typical = calibrate_lognormal_from_mean(1.0e6, 1.0)
    mega = calibrate_lognormal_from_mean(1.0e8, 0.8)
    sev = MixtureSeverity(typical=typical, mega=mega, p_mega=0.01)

    freq = PoissonFrequency(n_policies=1000, base_rate_per_policy=0.01, trend_factor=1.0)
    scn = PortfolioScenario(frequency=freq, severity=sev, seed=123)

    sims = simulate_many_years(scn, n_years=1000)
    assert sims["n_events"].shape == (1000,)
    assert sims["agg_loss"].shape == (1000,)
    assert np.all(sims["agg_loss"] >= 0.0)
