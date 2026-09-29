"""Save actual calibrated SHAP explanations and a feature summary."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from signalforge.inference import Predictor

predictor = Predictor()
frame = pd.read_csv("data/processed/test.csv").sample(20, random_state=42)
results = [predictor.explain(frame.iloc[[i]]) for i in range(len(frame))]
Path("docs/explanation-example.json").write_text(json.dumps(results[0], indent=2))
values = pd.DataFrame([{e["feature"]: e["contribution"] for e in r["explanation"]} for r in results])
importance = values.abs().mean().sort_values()
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(importance.index, importance.values, color="#299e8a")
ax.set(title="Calibrated permutation SHAP • 20 held-out records", xlabel="Mean absolute probability contribution")
fig.tight_layout(); fig.savefig("docs/assets/shap-summary.png", dpi=160); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 5))
row = values.iloc[0].sort_values()
ax.barh(row.index, row.values, color=np.where(row.values > 0, "#de926b", "#299e8a"))
ax.set(title="Individual prediction • calibrated probability contributions", xlabel="SHAP contribution")
fig.tight_layout(); fig.savefig("docs/assets/shap-individual.png", dpi=160); plt.close(fig)
