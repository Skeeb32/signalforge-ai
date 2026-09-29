# Validation evidence

Native development environment: macOS ARM64, Python 3.12.14, local PostgreSQL 17 and loopback Redis 7.0.11 with a real Celery worker. Compose specifies PostgreSQL 17 and Redis 7.4. Model and benchmark results are saved as JSON; screenshots come from the running API-backed application.

- Four-family full training, calibration, final evaluation and MLflow registration completed.
- Initial model promotion completed; guardrail tests reject later unsafe promotions.
- Actual API requests stored predictions in PostgreSQL; CSV scoring and explanations work.
- Python suite, separate PostgreSQL API integration, frontend tests/build/lint and Terraform validation are recorded during final verification below.
- Real Celery batch/monitoring tasks returned SUCCESS; docs/queue-results.json records evidence.
- Deterministic drift simulation produced HEALTHY baseline and ALERT shifted data.
- Real Chromium desktop/detail/model/monitoring/mobile captures completed without browser errors.
- No AWS infrastructure was applied. Docker is unavailable on this Mac; container validation is delegated to CI and must be distinguished from native execution.

Final clean-checkout and GitHub Actions status will be recorded after the final verification run. No unrun check is considered passed.
