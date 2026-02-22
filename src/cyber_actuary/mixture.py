from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .severity import LognormalParams, sample_lognormal


@dataclass(frozen=True)
class MixtureSeverity:
    """
    Two-component severity mixture:
      with probability p_mega: mega lognormal
      else: typical lognormal
    """
    typical: LognormalParams
    mega: LognormalParams
    p_mega: float

    def validate(self) -> None:
        if not (0.0 <= self.p_mega <= 1.0):
            raise ValueError("p_mega must be in [0,1]")


def sample_mixture(sev: MixtureSeverity, n: int, rng: np.random.Generator) -> np.ndarray:
    sev.validate()
    is_mega = rng.random(n) < sev.p_mega
    out = np.empty(n, dtype=float)
    n_mega = int(is_mega.sum())
    n_typ = n - n_mega
    if n_typ > 0:
        out[~is_mega] = sample_lognormal(sev.typical, n_typ, rng)
    if n_mega > 0:
        out[is_mega] = sample_lognormal(sev.mega, n_mega, rng)
    return out
