import numpy as np

from cyber_actuary.mixture import MixtureSeverity, sample_mixture
from cyber_actuary.severity import calibrate_lognormal_from_mean


def test_mixture_sampling_runs():
    rng = np.random.default_rng(0)
    typical = calibrate_lognormal_from_mean(1.0, 1.0)
    mega = calibrate_lognormal_from_mean(100.0, 0.8)
    mix = MixtureSeverity(typical=typical, mega=mega, p_mega=0.1)
    x = sample_mixture(mix, n=1000, rng=rng)
    assert x.shape == (1000,)
    assert float(x.mean()) > 0.0
