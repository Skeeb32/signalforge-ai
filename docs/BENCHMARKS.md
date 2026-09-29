# Measured local benchmarks

Source: [benchmarks.json](benchmarks.json). Hardware/platform: `macOS-14.2.1-arm64-arm-64bit`, architecture `arm64`, Python `3.12.14`. One loaded model, CPU inference, warm-up before timing. Single-process sequential requests; no concurrency or saturation test.

| Measurement | Result | Scope |
|---|---:|---|
| Four-family search/calibration pipeline | 28.68 s | Includes per-family MLflow logging; excludes final figure rendering/registration |
| Single inference p50 | 22.05 ms | 50 warm calls; includes validation, preprocessing, churn and value models |
| Single inference p95 | 22.61 ms | Same sample |
| HTTP p50 | 29.43 ms | 30 local POSTs including PostgreSQL audit persistence |
| HTTP p95 | 47.98 ms | Same sample; includes first HTTP request |
| Batch elapsed | 0.03932 s | 313 rows, one in-process call |
| Batch throughput | 7959 rows/s | Batch size / elapsed; not HTTP capacity |
| Benchmark process RSS | 276.28 MiB | Client plus both loaded models, not the whole stack |

Run `python scripts/benchmark.py` with the API running. Record OS, CPU, dataset/model versions and service configuration alongside results. Redis, Celery, PostgreSQL and the API have separate memory footprints not measured here. No extrapolated 10,000 requests/s, cost savings or production user counts are claimed.
