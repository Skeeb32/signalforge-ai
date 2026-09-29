"""Reference-based drift and quality reports, including delayed-label performance."""
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from signalforge.data import CATEGORIES, INPUTS
from signalforge.evaluation import metrics


def psi(reference, current) -> float:
    reference, current = np.asarray(reference), np.asarray(current)
    reference, current = reference[np.isfinite(reference)], current[np.isfinite(current)]
    if not len(reference) or not len(current):
        return 0.0
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, 11)))
    edges = np.r_[-np.inf, edges[1:-1], np.inf]
    if len(edges) == 2:
        center = reference[0]
        edges = np.array([-np.inf, center - 1e-6, center + 1e-6, np.inf])
    expected = np.histogram(reference, edges)[0].astype(float) + 0.5
    observed = np.histogram(current, edges)[0].astype(float) + 0.5
    expected /= expected.sum()
    observed /= observed.sum()
    return float(np.sum((observed - expected) * np.log(observed / expected)))


def monitor(reference: pd.DataFrame, current: pd.DataFrame) -> dict:
    if current.empty:
        return {"status": "NO_DATA", "rows": 0, "features": {}, "significant_drift": False}
    missing_columns = sorted(set(INPUTS) - set(current.columns))
    features = {}
    for column in INPUTS:
        if column not in current:
            continue
        r = pd.to_numeric(reference[column], errors="coerce").dropna()
        c = pd.to_numeric(current[column], errors="coerce")
        valid = c.dropna()
        score = psi(r, valid)
        ks = ks_2samp(r, valid) if len(valid) else None
        features[column] = {"psi": score, "missing_rate": float(c.isna().mean()),
                            "out_of_range_rate": float(((c < r.min()) | (c > r.max())).mean()),
                            "unexpected_categories": sorted(set(valid) - set(CATEGORIES[column])) if column in CATEGORIES else [],
                            "ks_statistic": float(ks.statistic) if ks else None,
                            "ks_pvalue": float(ks.pvalue) if ks else None,
                            "drift": bool(score > 0.2)}
    drift = any(f["drift"] for f in features.values())
    quality = bool(missing_columns) or any(f["missing_rate"] > 0.05 or f["unexpected_categories"] for f in features.values())
    return {"status": "ALERT" if drift or quality else "HEALTHY", "rows": len(current),
            "significant_drift": drift, "quality_alert": quality,
            "missing_columns": missing_columns, "features": features,
            "policy": "PSI > 0.2 is a heuristic alert; KS descriptive only; minimum retraining window 100 labeled records"}


def labeled_performance(labels, probabilities, threshold: float) -> dict:
    if len(labels) < 2 or len(set(labels)) < 2:
        return {"status": "INSUFFICIENT_LABELS", "rows": len(labels)}
    return {"status": "AVAILABLE", "rows": len(labels), **metrics(labels, probabilities, threshold)}
