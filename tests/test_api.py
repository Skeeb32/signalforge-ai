import io

import pandas as pd


def test_api_model_database_roundtrip(client, customer):
    response = client.post("/predict", json=customer)
    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction_id"] > 0
    rows = client.get("/customers", params={"q": customer["customer_id"]}).json()
    assert rows[0]["probability"] == payload["prediction"]["churn_probability"]
    assert (
        client.post(
            "/feedback", json={"prediction_id": payload["prediction_id"], "label": 1}
        ).status_code
        == 200
    )
    assert client.get("/health").json()["status"] == "ok"
    assert "signalforge_request_seconds" in client.get("/metrics").text


def test_validation_and_authentication(client, customer, monkeypatch):
    assert client.post("/predict", json={**customer, "age": -10}).status_code == 422
    assert client.post("/predict", json={**customer, "churn": 1}).status_code == 422
    monkeypatch.setenv("API_KEY", "test-only-key")
    assert client.post("/predict", json=customer).status_code == 401
    assert (
        client.post("/predict", json=customer, headers={"X-API-Key": "test-only-key"}).status_code
        == 200
    )


def test_csv_batch_and_limits(client, customer):
    csv = pd.DataFrame([customer, customer]).to_csv(index=False)
    response = client.post("/predict/csv", files={"file": ("customers.csv", csv, "text/csv")})
    assert response.status_code == 200
    assert len(pd.read_csv(io.StringIO(response.text))) == 2
    assert client.post("/predict/batch", json={"customers": []}).status_code == 422
    assert (
        client.post(
            "/predict/csv", files={"file": ("bad.csv", "not,the,schema\n1,2,3", "text/csv")}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/predict/csv", files={"file": ("large.csv", b"x" * 2_000_001, "text/csv")}
        ).status_code
        == 413
    )


def test_feedback_missing_prediction(client):
    assert (
        client.post("/feedback", json={"prediction_id": 999999999, "label": 1}).status_code == 404
    )


def test_monitoring_snapshot_is_persisted(client, customer):
    client.post("/predict", json=customer)
    report = client.post("/monitoring/run").json()
    assert report["rows"] >= 1
    assert report["performance"]["status"] in ["INSUFFICIENT_LABELS", "AVAILABLE"]


def test_csv_customer_id_cannot_inject_formulas(client, customer):
    csv = pd.DataFrame([{**customer, "customer_id": "=1+1"}]).to_csv(index=False)
    assert (
        client.post("/predict/csv", files={"file": ("attack.csv", csv, "text/csv")}).status_code
        == 422
    )
