"""Licensed dataset ingestion, validation and leakage-aware splits."""
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from signalforge.config import SEED

URL = "https://archive.ics.uci.edu/static/public/563/iranian+churn+dataset.zip"
NAMES = ["call_failures", "complaints", "tenure", "charge_band", "seconds_of_use",
         "call_count", "sms_count", "distinct_contacts", "age_group", "tariff_plan",
         "status", "age", "customer_value", "churn"]
INPUTS = NAMES[:8] + ["tariff_plan", "age"]
CATEGORIES = {"complaints": [0, 1], "tariff_plan": [1, 2]}


def ingest(path: Path = Path("data/raw/churn.csv")) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with urllib.request.urlopen(URL, timeout=60) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
        path.write_bytes(archive.read("Customer Churn.csv"))
    return path


def validate(frame: pd.DataFrame, labeled: bool = True) -> dict:
    required = INPUTS + (["churn", "customer_value"] if labeled else [])
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    for column in required:
        values = pd.to_numeric(frame[column], errors="raise")
        if np.isinf(values).any() or (values.dropna() < 0).any():
            raise ValueError(f"{column}: expected finite nonnegative values")
    for column, allowed in {**CATEGORIES, **({"churn": [0, 1]} if labeled else {})}.items():
        if not frame[column].dropna().isin(allowed).all():
            raise ValueError(f"{column}: unexpected category")
    if labeled and frame[["churn", "customer_value"]].isna().any().any():
        raise ValueError("Targets must not be missing")
    if not frame.charge_band.dropna().between(0, 9).all():
        raise ValueError("charge_band must be in 0..9")
    if not frame.age.dropna().between(0, 120).all():
        raise ValueError("age must be in 0..120")
    return {"rows": len(frame), "missing": frame[required].isna().sum().to_dict()}


def load(path: Path = Path("data/raw/churn.csv")) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "churn" not in frame.columns:
        if len(frame.columns) != len(NAMES):
            raise ValueError("Unexpected raw schema")
        frame.columns = NAMES
    validate(frame)
    frame["customer_id"] = [f"UCI-{i:05d}" for i in frame.index]
    return frame


def prepare(path: Path = Path("data/raw/churn.csv")) -> tuple[dict, dict]:
    frame = load(ingest(path))
    # Identical predictor profiles must stay together, including conflicting labels.
    groups = pd.util.hash_pandas_object(frame[INPUTS], index=False)
    splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=SEED)
    fold = np.zeros(len(frame), dtype=int)
    for i, (_, indices) in enumerate(splitter.split(frame, frame.churn, groups)):
        fold[indices] = i
    masks = {"train": fold < 6, "calibration": (fold >= 6) & (fold < 8),
             "validation": fold == 8, "test": fold == 9}
    parts = {name: frame.loc[mask].copy() for name, mask in masks.items()}
    for name, part in parts.items():
        Path("data/processed").mkdir(parents=True, exist_ok=True)
        part.to_csv(f"data/processed/{name}.csv", index=False)
    Path("data/sample").mkdir(parents=True, exist_ok=True)
    frame.head(25).to_csv("data/sample/customers.csv", index=False)
    report = {**validate(frame), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "source": URL, "license": "CC BY 4.0", "seed": SEED,
              "churn_rate": float(frame.churn.mean()), "raw_features": 13,
              "duplicate_predictor_profiles": int(groups.duplicated().sum()),
              "splits": {k: {"rows": len(v), "churn_rate": float(v.churn.mean())}
                         for k, v in parts.items()}}
    Path("docs/data-report.json").write_text(json.dumps(report, indent=2))
    return parts, report
