import math

from cyber_actuary.severity import calibrate_lognormal_from_mean


def test_calibrate_lognormal_from_mean_recovers_mean():
    mean_target = 4.4e6
    sigma = 1.0
    p = calibrate_lognormal_from_mean(mean_x=mean_target, sigma=sigma)
    assert math.isfinite(p.mu)
    assert abs(p.mean() - mean_target) / mean_target < 1e-10
