"""Send real held-out records through the live API, explicitly as a research demo."""

import os

import httpx
import pandas as pd

from signalforge.data import INPUTS

frame = pd.read_csv("data/processed/test.csv")
with httpx.Client(
    base_url=os.getenv("API_URL", "http://127.0.0.1:8000"),
    timeout=60,
    headers={"X-API-Key": os.getenv("API_KEY", "")},
) as client:
    for start in range(0, len(frame), 100):
        batch = frame.iloc[start : start + 100]
        response = client.post(
            "/predict/batch", json={"customers": batch[["customer_id"] + INPUTS].to_dict("records")}
        )
        response.raise_for_status()
    print(
        f"Recorded {len(frame)} actual predictions. Labels remain unsubmitted to demonstrate delayed outcomes."
    )
