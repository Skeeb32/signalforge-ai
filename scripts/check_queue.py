"""Integration check using an actual running Redis broker and Celery worker."""

import json
from pathlib import Path

import pandas as pd

from signalforge.data import INPUTS
from signalforge.tasks import batch_predict, run_monitoring

frame = pd.read_csv("data/sample/customers.csv")
job = batch_predict.delay(frame[["customer_id"] + INPUTS].head(3).to_dict("records"))
result = job.get(timeout=90)
assert len(result) == 3 and all(r["prediction_id"] > 0 for r in result)
monitoring = run_monitoring.delay().get(timeout=90)
report = {
    "state": job.state,
    "predictions": len(result),
    "persisted_ids": [r["prediction_id"] for r in result],
    "monitoring_status": monitoring["status"],
}
Path("docs/queue-results.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report))
