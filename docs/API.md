# HTTP API

Interactive OpenAPI: `/docs`; machine schema: `/openapi.json`. Run at `http://127.0.0.1:8000`. All endpoints accept optional `X-API-Key` when `API_KEY` is configured; the dashboard shield button stores a key for the current browser session. In the default loopback demo, authentication is disabled.

| Method | Path | Contract |
|---|---|---|
| GET | /health | Database reachability and loaded model version; 503 when no artifact |
| GET | /model/info | Model/version, comparison, split lineage and selection policy |
| POST | /predict | One strictly validated Customer |
| POST | /predict/batch | `{ "customers": [...] }`, 1–500 customers |
| POST | /predict/csv | Multipart `file`, ≤2 MB, 1–500 rows; CSV download |
| POST | /explain | One Customer; approximate calibrated SHAP contributions |
| GET | /customers | `q`, `risk=HIGH|LOW`, `limit` (max 500), newest prediction events |
| GET | /dashboard | Latest-500 event summary, distribution and recent predictions |
| GET | /monitoring | Current model's recent quality/drift and available label metrics |
| POST | /monitoring/run | Compute and persist a monitoring snapshot |
| POST | /feedback | `{ "prediction_id": 123, "label": 0 }`; actual delayed outcome |
| POST | /jobs/batch | Queue batch; return job ID with HTTP 202 |
| GET | /jobs/{job_id} | Queue state and completed result; results expire after one hour |
| GET | /metrics | Prometheus HTTP request counts and duration histogram |

Generate a valid request from the included sample:

```sh
python - <<'PY' > /tmp/signalforge-customer.json
import json, pandas as pd
from signalforge.data import INPUTS
print(json.dumps(pd.read_csv('data/sample/customers.csv')[['customer_id'] + INPUTS].iloc[0].to_dict()))
PY
curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' --data-binary @/tmp/signalforge-customer.json
curl -X POST http://localhost:8000/explain -H 'Content-Type: application/json' --data-binary @/tmp/signalforge-customer.json
```

Each response includes customer ID, actual churn probability, HIGH/LOW risk using the model's validation threshold, value-at-risk index, model name/version, UTC timestamp and (for persisted predictions) prediction ID. `/explain` also supplies training-background baseline, signed contributions, observed values and a non-causal interpretation note. See [a real saved explanation](explanation-example.json).

CSV input headers must be exactly `customer_id` and the ten inputs listed in DATA.md. The labeled sample contains extra columns; produce an upload file with:

```sh
python - <<'PY'
import pandas as pd
from signalforge.data import INPUTS
pd.read_csv('data/sample/customers.csv')[['customer_id']+INPUTS].to_csv('customers-upload.csv',index=False)
PY
curl -F file=@customers-upload.csv http://localhost:8000/predict/csv --output predictions.csv
```

Validation errors use 422, oversized CSV 413, missing record 404, authentication 401, rate limit 429 and unavailable model/Redis limiter 503. Local rate limiting is process-local; `RATE_LIMIT_REDIS=1` uses a shared atomic counter. The limit is 120 requests/client-IP/minute including reads. Trusted proxy handling and per-user/tenant quotas are deployment concerns, not implemented here. Input IDs exclude formula-leading characters to prevent CSV formula injection.

Synchronous batch is bounded. Use jobs for background work; model training is an operator workflow, not an unauthenticated arbitrary-code endpoint. Celery's delivery can be at-least-once; request idempotency/deduplication is a documented production improvement. Do not put personal data into this public demo.
