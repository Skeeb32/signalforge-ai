"""Train, calibrate, compare and register models without choosing on the test set."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow import MlflowClient
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from signalforge.config import FEATURE_VERSION, MODEL_NAME, SEED, TRACKING_URI
from signalforge.data import INPUTS, prepare
from signalforge.evaluation import choose_threshold, metrics, plots
from signalforge.features import preprocessing
from signalforge.neural import TorchClassifier


def families():
    return {
        "logistic": (
            LogisticRegression(max_iter=1500, class_weight="balanced", random_state=SEED),
            {"model__C": [0.1, 1.0]},
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=180, class_weight="balanced", n_jobs=1, random_state=SEED
            ),
            {"model__min_samples_leaf": [2, 5]},
        ),
        "xgboost": (
            XGBClassifier(
                n_estimators=180,
                learning_rate=0.05,
                n_jobs=1,
                random_state=SEED,
                eval_metric="logloss",
            ),
            {"model__max_depth": [3, 5]},
        ),
        "pytorch": (TorchClassifier(), {"model__hidden": [16, 32]}),
    }


def train(
    output: Path = Path("models/candidate"),
    register: bool = True,
    data_path: Path = Path("data/raw/churn.csv"),
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    parts, dataset = prepare(data_path)
    tr, cal, val, test = [parts[k] for k in ["train", "calibration", "validation", "test"]]
    groups = pd.util.hash_pandas_object(tr[INPUTS], index=False)
    cv = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("SignalForge churn comparison")
    fitted, comparisons, predictions = {}, {}, {}
    start_all = time.perf_counter()
    for name, (estimator, grid) in families().items():
        start = time.perf_counter()
        print(f"Training {name}...", flush=True)
        with mlflow.start_run(run_name=name) as run:
            pipeline = Pipeline([("preprocess", preprocessing()), ("model", estimator)])
            search = GridSearchCV(pipeline, grid, scoring="average_precision", cv=cv, n_jobs=1)
            search.fit(tr[INPUTS], tr.churn, groups=groups)
            model = CalibratedClassifierCV(
                FrozenEstimator(search.best_estimator_), method="sigmoid"
            )
            model.fit(cal[INPUTS], cal.churn)
            p = model.predict_proba(val[INPUTS])[:, 1]
            threshold = choose_threshold(val.churn, p)
            raw_p = search.best_estimator_.predict_proba(val[INPUTS])[:, 1]
            result = {
                "validation": metrics(val.churn, p, threshold),
                "uncalibrated_validation": metrics(val.churn, raw_p, threshold),
                "cv_pr_auc": float(search.best_score_),
                "threshold": threshold,
                "parameters": search.best_params_,
                "run_id": run.info.run_id,
                "training_seconds": time.perf_counter() - start,
            }
            mlflow.log_params(
                {
                    **search.best_params_,
                    "dataset_sha256": dataset["sha256"],
                    "feature_version": FEATURE_VERSION,
                    "seed": SEED,
                }
            )
            mlflow.log_metrics(
                {k: v for k, v in result["validation"].items() if isinstance(v, float)}
            )
            mlflow.log_metric("training_seconds", result["training_seconds"])
            mlflow.sklearn.log_model(
                model,
                name="model",
                input_example=val[INPUTS].head(2).astype(float),
                serialization_format="cloudpickle",
            )
            fitted[name] = model
            comparisons[name] = result
    # Freeze choice BEFORE looking at any test metric.
    selected = max(comparisons, key=lambda n: comparisons[n]["validation"]["pr_auc"])
    threshold = comparisons[selected]["threshold"]
    for name, model in fitted.items():
        p = model.predict_proba(test[INPUTS])[:, 1]
        comparisons[name]["test"] = metrics(test.churn, p, comparisons[name]["threshold"])
        predictions[name] = p
    # Auxiliary regression: predict the observed calculated value, not future revenue.
    regression = Pipeline(
        [
            ("preprocess", preprocessing()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=160, min_samples_leaf=3, n_jobs=1, random_state=SEED
                ),
            ),
        ]
    )
    regression.fit(tr[INPUTS], tr.customer_value)
    rpred = regression.predict(test[INPUTS])
    regression_metrics = {
        "mae": float(mean_absolute_error(test.customer_value, rpred)),
        "rmse": float(root_mean_squared_error(test.customer_value, rpred)),
        "r2": float(r2_score(test.customer_value, rpred)),
        "target": "observed customer value index; not future revenue",
    }
    version = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    metadata = {
        "name": MODEL_NAME,
        "version": version,
        "selected": selected,
        "threshold": threshold,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset,
        "feature_version": FEATURE_VERSION,
        "selection_policy": "Highest validation average precision after sigmoid calibration; validation F1 threshold; test untouched until frozen choice",
        "comparison": comparisons,
        "regression": regression_metrics,
        "training_seconds": time.perf_counter() - start_all,
    }
    joblib.dump(fitted[selected], output / "model.joblib")
    joblib.dump(regression, output / "value.joblib")
    tr[INPUTS].sample(min(80, len(tr)), random_state=SEED).to_csv(
        output / "background.csv", index=False
    )
    tr[INPUTS].to_csv(output / "reference.csv", index=False)
    pre = fitted[selected].calibrated_classifiers_[0].estimator.estimator.named_steps["preprocess"]
    np.save("data/features/train.npy", pre.transform(tr[INPUTS]))
    if register:
        source_run = comparisons[selected]["run_id"]
        registry = mlflow.register_model(f"runs:/{source_run}/model", MODEL_NAME)
        MlflowClient().set_registered_model_alias(MODEL_NAME, "candidate", registry.version)
        metadata["registry_version"] = registry.version
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2))
    Path("docs/results.json").write_text(json.dumps(metadata, indent=2))
    plots(test.churn, predictions, selected, threshold, Path("docs/assets"))
    print(json.dumps({"selected": selected, "test": comparisons[selected]["test"]}, indent=2))
    with mlflow.start_run(run_id=comparisons[selected]["run_id"]):
        mlflow.log_dict(metadata, "evaluation/metadata.json")
        mlflow.log_artifacts("docs/assets", artifact_path="evaluation/figures")
    return metadata
