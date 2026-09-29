"""Versioned artifacts and atomic local promotion with registry aliases."""
import json
import os
import shutil
from pathlib import Path

import mlflow
from mlflow import MlflowClient

from signalforge.config import MODEL_NAME, TRACKING_URI
from signalforge.evaluation import metrics
from signalforge.inference import Predictor


def promotion_gate(candidate: dict, champion: dict) -> bool:
    return (candidate["pr_auc"] >= champion["pr_auc"] + 0.005
            and candidate["brier"] <= champion["brier"] + 0.005
            and candidate["recall"] >= champion["recall"] - 0.02)


def promote(candidate: Path, production: Path = Path("models/production"), evaluation=None) -> dict:
    challenger = Predictor(candidate)
    if production.exists():
        if evaluation is None or len(evaluation) < 100 or evaluation.churn.nunique() < 2:
            return {"promoted": False, "reason": "An independent, labeled evaluation window (>=100) is required"}
        incumbent = Predictor(production)
        c = metrics(evaluation.churn, challenger.model.predict_proba(evaluation)[:, 1], challenger.metadata["threshold"])
        p = metrics(evaluation.churn, incumbent.model.predict_proba(evaluation)[:, 1], incumbent.metadata["threshold"])
        if not promotion_gate(c, p):
            return {"promoted": False, "reason": "Candidate failed improvement/calibration/recall gate", "candidate": c, "champion": p}
    else:
        p, c = None, challenger.metadata["comparison"][challenger.metadata["selected"]]["validation"]
    version = challenger.metadata["version"]
    destination = production.parent / "versions" / version
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(candidate, destination, dirs_exist_ok=True)
    temporary = production.parent / ".next-production"
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(Path("versions") / version)
    if production.exists() and not production.is_symlink():
        raise ValueError("Production must be a version symlink, not a directory")
    os.replace(temporary, production)
    if challenger.metadata.get("registry_version"):
        mlflow.set_tracking_uri(TRACKING_URI)
        client = MlflowClient()
        try:
            previous = client.get_model_version_by_alias(MODEL_NAME, "production")
            client.set_registered_model_alias(MODEL_NAME, "archived", previous.version)
        except mlflow.exceptions.MlflowException:
            pass
        client.set_registered_model_alias(MODEL_NAME, "production", challenger.metadata["registry_version"])
    report = {"promoted": True, "version": version, "candidate": c, "champion": p,
              "reason": "Bootstrap" if p is None else "Independent-window gate passed"}
    (destination / "promotion.json").write_text(json.dumps(report, indent=2))
    return report
