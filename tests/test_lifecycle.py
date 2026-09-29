import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from signalforge.data import INPUTS
from signalforge.neural import TorchClassifier
from signalforge.registry import promote


def test_torch_clone_and_probability_contract():
    from sklearn.base import clone

    model = clone(TorchClassifier(hidden=4, epochs=3))
    x = np.random.default_rng(42).normal(size=(40, 3))
    model.fit(x, np.tile([0, 1], 20))
    p = model.predict_proba(x)
    assert p.shape == (40, 2)
    np.testing.assert_allclose(p.sum(axis=1), 1, atol=1e-6)
    assert np.isfinite(p).all()


def test_bootstrap_and_missing_evaluation_guard(predictor, tmp_path):
    import shutil

    candidate = tmp_path / "candidate"
    shutil.copytree(Path("models/production").resolve(), candidate)
    metadata = json.loads((candidate / "metadata.json").read_text())
    metadata.pop("registry_version", None)
    (candidate / "metadata.json").write_text(json.dumps(metadata))
    production = tmp_path / "production"
    assert promote(candidate, production)["promoted"]
    assert production.is_symlink()
    assert not promote(candidate, production)["promoted"]


def test_retraining_blocks_overlapping_evaluation(predictor, tmp_path):
    from signalforge.retraining import retrain

    frame = pd.read_csv("data/processed/train.csv").head(150)
    path = tmp_path / "window.csv"
    frame.to_csv(path, index=False)
    report = retrain(path, path)
    assert not report["promoted"]
    assert "overlap" in report["reason"]


def test_null_input_is_imputed(client, customer):
    customer["seconds_of_use"] = None
    result = client.post("/predict", json=customer)
    assert result.status_code == 200
    assert 0 <= result.json()["prediction"]["churn_probability"] <= 1


def test_reference_monitoring_labeled_metrics():
    from signalforge.monitoring import labeled_performance

    report = labeled_performance([0, 0, 1, 1], [0.1, 0.2, 0.7, 0.9], 0.5)
    assert report["f1"] == 1
    assert report["roc_auc"] == 1


def test_schema_missing_and_invalid_frame():
    from signalforge.data import validate

    frame = pd.read_csv("data/sample/customers.csv")
    with pytest.raises(ValueError, match="Missing"):
        validate(frame.drop(columns=INPUTS[0]))
    frame["age"] = -1
    with pytest.raises(ValueError, match="nonnegative"):
        validate(frame)
