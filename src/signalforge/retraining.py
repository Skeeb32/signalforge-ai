"""Drift-triggered candidate training with disjoint, labeled promotion evaluation."""

from pathlib import Path

import pandas as pd

from signalforge.data import INPUTS, load
from signalforge.inference import Predictor
from signalforge.monitoring import monitor
from signalforge.registry import promote
from signalforge.training import train


def retrain(training_path: Path, evaluation_path: Path) -> dict:
    current = Predictor()
    training, evaluation = load(training_path), load(evaluation_path)
    if len(training) < 100 or len(evaluation) < 100:
        return {"promoted": False, "reason": "Need >=100 labeled training and evaluation rows"}
    if training.churn.nunique() < 2 or evaluation.churn.nunique() < 2:
        return {"promoted": False, "reason": "Both classes are required"}
    train_hash = set(pd.util.hash_pandas_object(training[INPUTS], index=False))
    eval_hash = set(pd.util.hash_pandas_object(evaluation[INPUTS], index=False))
    old_hash = set(pd.util.hash_pandas_object(current.reference[INPUTS], index=False))
    if train_hash & eval_hash or old_hash & eval_hash:
        return {
            "promoted": False,
            "reason": "Evaluation profiles overlap candidate or champion training",
        }
    report = monitor(current.reference, training)
    if not report["significant_drift"]:
        return {"promoted": False, "reason": "No significant drift", "monitoring": report}
    candidate = Path("models/retraining-candidate")
    train(output=candidate, data_path=training_path)
    result = promote(candidate, evaluation=evaluation)
    return {**result, "monitoring": report}
