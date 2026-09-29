"""One inference contract for the API, CLI and workers."""
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

from signalforge.config import MODEL_DIR
from signalforge.data import INPUTS, validate


class Predictor:
    def __init__(self, directory: Path = MODEL_DIR):
        # Only load trusted, locally generated artifacts; pickle is not a safe upload format.
        self.metadata = json.loads((directory / "metadata.json").read_text())
        self.model = joblib.load(directory / "model.joblib")
        self.value_model = joblib.load(directory / "value.joblib")
        self.background = pd.read_csv(directory / "background.csv")[INPUTS]
        self.reference = pd.read_csv(directory / "reference.csv")[INPUTS]

    def predict(self, frame: pd.DataFrame) -> list[dict]:
        validate(frame, labeled=False)
        p = self.model.predict_proba(frame[INPUTS])[:, 1]
        value = self.value_model.predict(frame[INPUTS])
        now = datetime.now(timezone.utc).isoformat()
        results = []
        for i, probability in enumerate(p):
            risk = "HIGH" if probability >= self.metadata["threshold"] else "LOW"
            results.append({"customer_id": str(frame.iloc[i].get("customer_id", f"row-{i}")),
                            "prediction": {"churn_probability": float(probability), "risk_level": risk,
                                           "value_at_risk_index": float(probability * max(0, value[i]))},
                            "model": {"name": self.metadata["name"], "version": self.metadata["version"]},
                            "timestamp": now})
        return results

    def explain(self, frame: pd.DataFrame) -> dict:
        prediction = self.predict(frame)[0]
        def probability(values):
            return self.model.predict_proba(pd.DataFrame(values, columns=INPUTS))[:, 1]
        # Permutation SHAP explains the entire calibrated pipeline in probability units.
        explainer = shap.Explainer(probability, self.background, algorithm="permutation", seed=42)
        explanation = explainer(frame[INPUTS], max_evals=2 * len(INPUTS) * 12 + 1)
        values = explanation.values[0]
        prediction["explanation"] = [{"feature": INPUTS[j],
                                      "value": None if pd.isna(frame.iloc[0][INPUTS[j]]) else float(frame.iloc[0][INPUTS[j]]),
                                      "contribution": float(values[j]),
                                      "impact": "positive" if values[j] > 0 else "negative"}
                                     for j in np.argsort(-np.abs(values))]
        prediction["base_probability"] = float(explanation.base_values[0])
        prediction["explanation_note"] = "Approximate permutation SHAP for calibrated probability; associations, not causal effects. Correlated features can share attribution."
        return prediction
