"""Redis-backed Celery jobs keep expensive work off HTTP request threads."""
from pathlib import Path

import pandas as pd
from celery import Celery

from signalforge.config import REDIS_URL

celery = Celery("signalforge", broker=REDIS_URL, backend=REDIS_URL)
celery.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"],
                   result_expires=3600, task_time_limit=1800, worker_prefetch_multiplier=1)


@celery.task
def batch_predict(records: list[dict]) -> list[dict]:
    from signalforge.api import get_predictor, persist
    frame = pd.DataFrame(records)
    return persist(frame, get_predictor().predict(frame))


@celery.task
def run_monitoring() -> dict:
    from signalforge.api import save_monitoring
    return save_monitoring()


@celery.task
def retrain_job(training_path: str, evaluation_path: str) -> dict:
    from signalforge.retraining import retrain
    return retrain(Path(training_path), Path(evaluation_path))
