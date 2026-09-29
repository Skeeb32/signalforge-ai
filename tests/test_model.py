import numpy as np
import pandas as pd
import pytest

from signalforge.monitoring import labeled_performance, monitor, psi
from signalforge.registry import promotion_gate


def test_prediction_artifact_contract(predictor, customer):
    frame = pd.DataFrame([customer, customer])
    p = predictor.predict(frame)
    assert len(p) == 2
    assert p[0]["prediction"] == p[1]["prediction"]
    assert 0 <= p[0]["prediction"]["churn_probability"] <= 1
    assert p[0]["model"]["version"] == predictor.metadata["version"]


def test_explanation_additivity(predictor, customer):
    e = predictor.explain(pd.DataFrame([customer]))
    assert e["base_probability"] + sum(
        x["contribution"] for x in e["explanation"]
    ) == pytest.approx(e["prediction"]["churn_probability"], abs=1e-5)


def test_drift_and_quality_alerts(predictor):
    frame = predictor.reference.copy()
    assert monitor(frame, frame)["status"] == "HEALTHY"
    shifted = frame.copy()
    shifted["complaints"] = 1
    assert monitor(frame, shifted)["significant_drift"]
    assert monitor(frame, shifted.drop(columns="age"))["quality_alert"]
    shifted["tariff_plan"] = 99
    assert monitor(frame, shifted)["features"]["tariff_plan"]["unexpected_categories"] == [99]
    assert monitor(frame, frame.head(0))["status"] == "NO_DATA"


def test_psi_constant_distribution():
    assert psi(np.zeros(100), np.zeros(100)) == pytest.approx(0)
    assert psi(np.zeros(100), np.ones(100)) > 0.2


def test_absent_labels_do_not_produce_metrics():
    assert labeled_performance([], [], 0.5)["status"] == "INSUFFICIENT_LABELS"


@pytest.mark.parametrize(
    "candidate,accepted",
    [
        ({"pr_auc": 0.82, "brier": 0.1, "recall": 0.8}, True),
        ({"pr_auc": 0.79, "brier": 0.1, "recall": 0.8}, False),
        ({"pr_auc": 0.85, "brier": 0.2, "recall": 0.8}, False),
        ({"pr_auc": 0.85, "brier": 0.1, "recall": 0.7}, False),
    ],
)
def test_promotion_rejects_regressions(candidate, accepted):
    assert promotion_gate(candidate, {"pr_auc": 0.8, "brier": 0.1, "recall": 0.8}) is accepted
