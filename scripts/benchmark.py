"""Local single-process warm-model measurements; no extrapolated throughput claims."""

import json
import os
import platform
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
import psutil

from signalforge.data import INPUTS
from signalforge.inference import Predictor

predictor = Predictor()
frame = pd.read_csv("data/processed/test.csv")
predictor.predict(frame.head(1))
latencies = []
for _ in range(50):
    start = time.perf_counter()
    predictor.predict(frame.head(1))
    latencies.append((time.perf_counter() - start) * 1000)
start = time.perf_counter()
predictor.predict(frame)
batch_seconds = time.perf_counter() - start
api_latencies = []
with httpx.Client(
    base_url=os.getenv("API_URL", "http://127.0.0.1:8000"),
    timeout=30,
    headers={"X-API-Key": os.getenv("API_KEY", "")},
) as client:
    for _ in range(30):
        start = time.perf_counter()
        result = client.post("/predict", json=frame[["customer_id"] + INPUTS].iloc[0].to_dict())
        result.raise_for_status()
        api_latencies.append((time.perf_counter() - start) * 1000)
report = {
    "platform": platform.platform(),
    "python": platform.python_version(),
    "cpu": platform.machine(),
    "single_inference_runs": 50,
    "single_inference_p50_ms": float(np.median(latencies)),
    "single_inference_p95_ms": float(np.percentile(latencies, 95)),
    "batch_rows": len(frame),
    "batch_seconds": batch_seconds,
    "batch_rows_per_second": len(frame) / batch_seconds,
    "http_requests": 30,
    "http_p50_ms": float(np.median(api_latencies)),
    "http_p95_ms": float(np.percentile(api_latencies, 95)),
    "client_process_rss_mb": psutil.Process().memory_info().rss / 1024**2,
    "training_seconds": predictor.metadata["training_seconds"],
    "scope": "warm local sequential requests, PostgreSQL persistence, no concurrency; RSS is benchmark client plus loaded models",
}
Path("docs/benchmarks.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
