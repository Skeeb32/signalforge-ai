import os
from pathlib import Path

import pandas as pd
import pytest

from signalforge.data import INPUTS


@pytest.fixture
def customer():
    frame = pd.read_csv("data/sample/customers.csv")
    return frame[["customer_id"] + INPUTS].iloc[0].to_dict()


@pytest.fixture
def predictor():
    if not Path("models/production/metadata.json").exists():
        pytest.skip("Run train and promote for artifact integration tests")
    from signalforge.inference import Predictor

    return Predictor()


@pytest.fixture
def client(tmp_path, monkeypatch, predictor):
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import sessionmaker

    import signalforge.api as api
    from signalforge.storage import Base, make_engine

    database = make_engine(os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path}/test.db"))
    Base.metadata.create_all(database)
    monkeypatch.setattr(api, "engine", database)
    monkeypatch.setattr(api, "Session", sessionmaker(database, expire_on_commit=False))
    monkeypatch.setattr(api, "_predictor", predictor)
    api._windows.clear()
    with TestClient(api.app) as test_client:
        yield test_client
    database.dispose()
