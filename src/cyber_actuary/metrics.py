from __future__ import annotations

import numpy as np


def var(x: np.ndarray, alpha: float) -> float:
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0,1)")
    return float(np.quantile(x, alpha, method="linear"))


def tvar(x: np.ndarray, alpha: float) -> float:
    """
    Empirical TVaR: mean of samples exceeding VaR_alpha.
    """
    v = var(x, alpha)
    tail = x[x > v]
    if tail.size == 0:
        return v
    return float(tail.mean())


def summarize_tail(x: np.ndarray, alphas=(0.90, 0.95, 0.99)) -> dict:
    out = {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        "min": float(np.min(x)),
        "max": float(np.max(x)),
    }
    for a in alphas:
        out[f"VaR_{int(a*100)}"] = var(x, a)
        out[f"TVaR_{int(a*100)}"] = tvar(x, a)
    return out
