"""Validated serving API with durable audit history and bounded batch jobs."""

import io
import json
import os
import secrets
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import ValidationError
from sqlalchemy import select, text

from signalforge.config import MODEL_DIR
from signalforge.inference import Predictor
from signalforge.monitoring import labeled_performance, monitor
from signalforge.schemas import Batch, Customer, Feedback
from signalforge.storage import ModelVersion, MonitoringRun, Prediction, Session, engine

REQUESTS = Counter("signalforge_requests_total", "HTTP requests", ["method", "status"])
LATENCY = Histogram("signalforge_request_seconds", "HTTP request duration")
_predictor = None
_lock = threading.Lock()
_windows = defaultdict(deque)


def get_predictor() -> Predictor:
    global _predictor
    try:
        metadata = json.loads((MODEL_DIR / "metadata.json").read_text())
        with _lock:
            if _predictor is None or _predictor.metadata["version"] != metadata["version"]:
                _predictor = Predictor(MODEL_DIR)
        return _predictor
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(503, "No healthy production model; run training and promotion") from exc


def authorize(request: Request):
    key = os.getenv("API_KEY", "")
    if key and not secrets.compare_digest(request.headers.get("x-api-key", ""), key):
        raise HTTPException(401, "Invalid API key")
    # Optional Redis limiter shares the window across API replicas.
    if os.getenv("RATE_LIMIT_REDIS") == "1":
        from redis import Redis
        from redis.exceptions import RedisError

        from signalforge.config import REDIS_URL

        try:
            client = Redis.from_url(REDIS_URL, socket_timeout=2)
            bucket = f"rate:{request.client.host}:{int(time.time() // 60)}"
            count = client.eval(
                "local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],61) end; return n",
                1,
                bucket,
            )
            if count > 120:
                raise HTTPException(429, "Rate limit exceeded")
        except RedisError as exc:
            raise HTTPException(503, "Rate limiter unavailable") from exc
    else:
        now = time.monotonic()
        with _lock:
            host = request.client.host if request.client else "local"
            window = _windows[host]
            while window and window[0] < now - 60:
                window.popleft()
            if len(window) >= 120:
                raise HTTPException(429, "Rate limit exceeded")
            window.append(now)
            if len(_windows) > 10000:
                _windows.clear()


@asynccontextmanager
async def lifespan(app):
    # Migrations run explicitly before the server starts.
    yield


app = FastAPI(
    title="SignalForge AI", version="0.1.0", lifespan=lifespan, dependencies=[Depends(authorize)]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def instrumentation(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    LATENCY.observe(time.perf_counter() - start)
    REQUESTS.labels(request.method, str(response.status_code)).inc()
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def persist(frame: pd.DataFrame, predictions: list[dict]) -> list[dict]:
    with Session.begin() as session:
        for record, result in zip(frame.to_dict("records"), predictions, strict=True):
            clean = {k: None if pd.isna(v) else v for k, v in record.items()}
            row = Prediction(
                customer_id=result["customer_id"],
                probability=result["prediction"]["churn_probability"],
                risk=result["prediction"]["risk_level"],
                model_version=result["model"]["version"],
                features=clean,
                value_at_risk=result["prediction"]["value_at_risk_index"],
            )
            session.add(row)
            session.flush()
            result["prediction_id"] = row.id
        model = get_predictor().metadata
        session.merge(ModelVersion(version=model["version"], metadata_json=model))
    return predictions


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "model_version": get_predictor().metadata["version"]}


@app.get("/model/info")
def model_info():
    return get_predictor().metadata


@app.post("/predict")
def predict(customer: Customer):
    frame = pd.DataFrame([customer.model_dump()])
    return persist(frame, get_predictor().predict(frame))[0]


@app.post("/predict/batch")
def predict_batch(batch: Batch):
    frame = pd.DataFrame([c.model_dump() for c in batch.customers])
    return {"predictions": persist(frame, get_predictor().predict(frame))}


@app.post("/predict/csv")
async def predict_csv(file: UploadFile = File(...)):
    contents = await file.read(2_000_001)
    if len(contents) > 2_000_000:
        raise HTTPException(413, "CSV limit is 2 MB")
    try:
        frame = pd.read_csv(io.BytesIO(contents))
        if not 1 <= len(frame) <= 500:
            raise ValueError("CSV must contain 1..500 rows")
        batch = Batch(
            customers=[
                Customer.model_validate(row)
                for row in frame.where(pd.notnull(frame), None).to_dict("records")
            ]
        )
    except (ValueError, ValidationError) as exc:
        raise HTTPException(422, str(exc)[:800]) from exc
    predictions = predict_batch(batch)["predictions"]
    output = pd.json_normalize(predictions).to_csv(index=False)
    return Response(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"},
    )


@app.post("/explain")
def explain(customer: Customer):
    return get_predictor().explain(pd.DataFrame([customer.model_dump()]))


@app.get("/customers")
def customers(q: str = "", risk: str = "", limit: int = 100):
    with Session() as session:
        query = select(Prediction).order_by(Prediction.id.desc())
        if q:
            query = query.where(Prediction.customer_id.contains(q, autoescape=True))
        if risk in ["HIGH", "LOW"]:
            query = query.where(Prediction.risk == risk)
        rows = session.scalars(query.limit(max(1, min(limit, 500)))).all()
        return [
            {
                "id": r.id,
                "customer_id": r.customer_id,
                "probability": r.probability,
                "risk": r.risk,
                "value_at_risk": r.value_at_risk,
                "model_version": r.model_version,
                "features": r.features,
                "timestamp": r.timestamp.isoformat(),
                "label": r.label,
            }
            for r in rows
        ]


@app.get("/dashboard")
def dashboard():
    rows = customers(limit=500)
    probabilities = [r["probability"] for r in rows]
    return {
        "window": "latest 500 predictions",
        "total_predictions": len(rows),
        "high_risk": sum(r["risk"] == "HIGH" for r in rows),
        "average_probability": sum(probabilities) / len(rows) if rows else None,
        "value_at_risk": sum(r["value_at_risk"] for r in rows),
        "recent": rows[:12],
        "distribution": [
            {
                "range": f"{i * 10}–{(i + 1) * 10}%",
                "count": sum(
                    i / 10 <= p < (i + 1) / 10 or (i == 9 and p == 1) for p in probabilities
                ),
            }
            for i in range(10)
        ],
    }


@app.post("/feedback")
def feedback(body: Feedback):
    with Session.begin() as session:
        row = session.get(Prediction, body.prediction_id)
        if row is None:
            raise HTTPException(404, "Prediction not found")
        row.label = body.label
    return {"saved": True}


@app.get("/monitoring")
def monitoring():
    predictor = get_predictor()
    rows = [r for r in customers(limit=500) if r["model_version"] == predictor.metadata["version"]]
    report = monitor(predictor.reference, pd.DataFrame([r["features"] for r in rows]))
    labeled = [r for r in rows if r["label"] is not None]
    report["performance"] = labeled_performance(
        [r["label"] for r in labeled],
        [r["probability"] for r in labeled],
        predictor.metadata["threshold"],
    )
    return report


@app.post("/monitoring/run")
def save_monitoring():
    report = monitoring()
    with Session.begin() as session:
        session.add(MonitoringRun(report=report))
    return report


@app.post("/jobs/batch", status_code=202)
def batch_job(batch: Batch):
    from signalforge.tasks import batch_predict

    job = batch_predict.delay([c.model_dump() for c in batch.customers])
    return {"job_id": job.id}


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    from signalforge.tasks import celery

    job = celery.AsyncResult(job_id)
    return {
        "job_id": job_id,
        "state": job.state,
        "result": job.result if job.successful() else None,
    }


@app.get("/metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
