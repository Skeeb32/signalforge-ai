# Validation evidence

## Verified local execution

- **33 Python tests passed** in the final local suite. Unit/integration pytest coverage is **66%** across all modules; this excludes separately executed training and worker processes.
- A **fresh clone and fresh virtual environment** downloaded data, trained all four families, registered and promoted the model, migrated a new database, scored a CSV and passed the then-current 32-test suite. Combined training-plus-test coverage was **85%**. Dataset hash, chosen model and every compared test metric matched exactly (maximum absolute difference **0.0**). See [reproduction.json](reproduction.json).
- **Six API integration tests passed against actual PostgreSQL 17**, separately from SQLite-based tests.
- Real Redis **7.0.11** and Celery batch/monitoring jobs completed with persisted prediction IDs. Compose uses Redis 7.4; [queue evidence](queue-results.json) records the native run.
- **Three frontend tests passed**; TypeScript production build, ESLint, Prettier and Ruff passed.
- Chromium exercised four live views, customer search and a real SHAP explanation. There were **zero browser errors** and **zero horizontal-overflow failures** across four 390px mobile layouts. [Browser evidence](browser-results.json).
- Both analysis notebooks were executed against real dataset/model outputs.
- Drift simulation: unchanged reference window **HEALTHY**, intentionally shifted window **ALERT**.
- Terraform **1.13.5** initialized with AWS provider **5.100.0** and validated successfully. **No AWS resources were applied.**
- Python and frontend dependency audits found **zero known vulnerabilities** after fixes. Gitleaks scanned the initial complete seven-commit history with **zero leaks**; subsequent GitHub security jobs also passed.
- All relative Markdown links resolved. Screenshots and GIF are actual browser captures, not generated mockups.

Native environment: macOS 14.2.1 ARM64, Python 3.12.14. The local machine has no Docker runtime; native PostgreSQL and Redis were used for local full-stack execution. GitHub's Linux jobs independently build the containers and now exercise the entire Compose stack.

## GitHub Actions

The first runs exposed a dependency lock mismatch, a first-push secret-scan history issue and a formatting difference. These were fixed. Full Python training/tests/worker checks, frontend checks, security scanning and image builds are configured. The [complete Linux validation run](https://github.com/Skeeb32/signalforge-ai/actions/runs/36560138750) passed all four jobs: Python, frontend, security and containers. The container job built both images, started the full six-service Compose stack, trained/registered the initial model, seeded actual predictions, executed Redis/Celery jobs, verified web/API HTTP responses and shut the stack down cleanly. The [final code revision verification](https://github.com/Skeeb32/signalforge-ai/actions/runs/36560453497) also passed every job, including the 33-test Python suite and the full Docker stack. The tested implementation commit is `de446fb`; [ci-results.json](ci-results.json) records the exact SHA and outcomes. The subsequent documentation-only receipt commit uses `[skip ci]` because it changes no implementation or configuration. An unrun or pending check is never counted as passed.

## What is not demonstrated

No AWS deployment, production customer traffic, real future-revenue forecast, business savings, independently labeled production retraining promotion, saturation load test or enterprise security certification is claimed. The static dataset supplies no genuinely new production label window. Candidate promotion safety is covered by tests and explicit refusal paths.
