"""Intentionally shifted research data; not an observed production incident."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from signalforge.inference import Predictor
from signalforge.monitoring import monitor

predictor = Predictor()
baseline = pd.read_csv("data/processed/test.csv")
shifted = baseline.copy()
shifted["seconds_of_use"] *= 0.1
shifted["call_count"] = (shifted.call_count * 0.2).astype(int)
shifted["complaints"] = 1
shifted.to_csv("data/processed/drift-simulation.csv", index=False)
report = {"label": "INTENTIONAL SIMULATION", "baseline": monitor(predictor.reference, baseline),
          "shifted": monitor(predictor.reference, shifted)}
Path("docs/drift-results.json").write_text(json.dumps(report, indent=2))
fig, ax = plt.subplots(figsize=(9, 4))
columns = list(report["shifted"]["features"])
ax.barh(columns, [report["shifted"]["features"][c]["psi"] for c in columns], color="#279b87")
ax.axvline(0.2, color="#d78758", linestyle="--", label="Alert threshold")
ax.set(xlabel="Population stability index", title="Intentional drift simulation • not production data")
ax.legend()
fig.tight_layout()
fig.savefig("docs/assets/drift.png", dpi=150)
print(json.dumps({"baseline": report["baseline"]["status"], "shifted": report["shifted"]["status"]}))
