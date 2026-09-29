# Resume bullets — evidence-backed variants

## ML Engineer
- Built an end-to-end churn platform comparing Logistic Regression, Random Forest, XGBoost and a PyTorch neural network with grouped cross-validation, held-out calibration and validation-based selection on 3,150 public telecom records.
- Selected XGBoost using validation average precision; reported held-out ROC-AUC 0.985, average precision 0.943 and F1 0.882, with calibrated SHAP explanations and reproducible drift simulation.
- Implemented MLflow experiment tracking and model aliases, delayed-label monitoring and a retraining promotion gate that checks ranking, calibration and recall.

## ML Platform Engineer
- Engineered FastAPI model serving with Pydantic validation, PostgreSQL/SQLAlchemy audit persistence, Alembic migrations and Redis/Celery batch and monitoring jobs.
- Measured 29.4 ms median and 48.0 ms p95 HTTP prediction latency in a local sequential benchmark including PostgreSQL persistence; documented test conditions and scaling limits.
- Added container configurations, CI quality/security checks and a validated Terraform AWS foundation; distinguished native local validation from cloud deployment work.

## Full Stack AI Engineer
- Built a React/TypeScript analytics dashboard with live customer risk, model comparisons, SHAP detail, CSV scoring and drift/quality monitoring backed by a shared Python inference service.
- Implemented responsive customer filtering, prediction history, loading/error/empty states and accessible controls; captured actual running-app screenshots and a walkthrough GIF.

Do not claim this demo served paying customers, saved revenue, ran on AWS or sustained production traffic. Use the latest docs/VALIDATION.md for current test and CI status.
