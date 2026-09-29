"""Environment-based configuration. All paths resolve from the repository working directory."""

import os
from pathlib import Path

SEED = 42
FEATURE_VERSION = "1.0.0"
MODEL_NAME = "signalforge-churn"
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models/production"))
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///signalforge.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
