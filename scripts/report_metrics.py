"""Additional figures and uncertainty estimates derived from real saved artifacts."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import average_precision_score

from signalforge.inference import Predictor

model = Predictor()
results = model.metadata
frame = pd.read_csv("data/processed/test.csv")
p = model.model.predict_proba(frame)[:, 1]
rng = np.random.default_rng(42)
scores = []
for _ in range(1000):
    idx = rng.choice(len(frame), len(frame), replace=True)
    if frame.churn.iloc[idx].nunique() == 2:
        scores.append(average_precision_score(frame.churn.iloc[idx], p[idx]))
report = {
    "bootstrap_replicates": len(scores),
    "test_average_precision_95_percentile_interval": np.quantile(scores, [0.025, 0.975]).tolist(),
    "note": "Row bootstrap on one held-out research split; does not capture training, temporal or deployment uncertainty",
    "age_slices": {},
}
for name, mask in {"under_30": frame.age < 30, "30_and_over": frame.age >= 30}.items():
    report["age_slices"][name] = {
        "rows": int(mask.sum()),
        "positive_labels": int(frame.churn[mask].sum()),
        "mean_probability": float(p[mask].mean()),
        "recall": float(
            ((p[mask] >= results["threshold"]) & (frame.churn[mask] == 1)).sum()
            / max(1, frame.churn[mask].sum())
        ),
    }
Path("docs/uncertainty.json").write_text(json.dumps(report, indent=2))
fig, ax = plt.subplots(figsize=(8, 4))
labels = list(results["comparison"])
ax.bar(
    np.arange(4) - 0.18,
    [results["comparison"][n]["validation"]["pr_auc"] for n in labels],
    0.36,
    label="Validation",
    color="#2a9b87",
)
ax.bar(
    np.arange(4) + 0.18,
    [results["comparison"][n]["test"]["pr_auc"] for n in labels],
    0.36,
    label="Test",
    color="#a2cec3",
)
ax.set(
    xticks=np.arange(4),
    xticklabels=labels,
    ylim=(0, 1),
    ylabel="Average precision",
    title="Model comparison • production choice uses validation only",
)
ax.legend()
fig.tight_layout()
fig.savefig("docs/assets/model-comparison.png", dpi=160)
plt.close(fig)
observed, predicted = calibration_curve(frame.churn, p, n_bins=8, strategy="quantile")
fig, ax = plt.subplots(figsize=(5, 5))
ax.plot([0, 1], [0, 1], "--", color="#aaa")
ax.plot(predicted, observed, "o-", color="#2a9b87")
ax.set(
    xlabel="Mean calibrated probability",
    ylabel="Observed churn fraction",
    title="Held-out calibration • quantile bins",
)
fig.tight_layout()
fig.savefig("docs/assets/calibration.png", dpi=160)
plt.close(fig)
