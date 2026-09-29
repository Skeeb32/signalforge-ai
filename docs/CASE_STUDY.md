# SignalForge AI — from a model to a maintained system

## Problem

A churn score is useful only if a team can reproduce it, inspect its evidence, serve it reliably and notice when its inputs stop resembling training data. SignalForge demonstrates that lifecycle on openly licensed telecom research data.

## Approach and data

The pipeline validates 3,150 UCI records, excludes a potential status shortcut and a calculated-value feature, engineers behavior ratios and groups identical profiles before splitting. Four model families receive grouped cross-validation. Calibration, selection and final test evaluation use separate partitions. Production logic lives in Python modules; notebooks only inspect the results.

## Architecture

FastAPI and the CLI call the same feature/preprocessing and prediction service. PostgreSQL stores predictions, source feature values, versions and monitoring snapshots. Redis supports shared rate limits and Celery jobs. MLflow stores experiment and model-registry lineage. A React/TypeScript dashboard turns that evidence into customer, model and monitoring views.

## Experimentation and selection

XGBoost won validation average precision and was selected before test inspection. Random Forest did slightly better on the held-out test set; the project preserves the original choice rather than rewriting the selection story. The README and MODEL_CARD contain exact measured metrics. The auxiliary value model predicts an observed index, not future monetary revenue.

## Explainability and monitoring

Approximate permutation SHAP explains the calibrated probability, with additive contributions checked in tests. Missingness, unexpected categories, ranges, PSI and descriptive KS statistics detect data changes. A deliberately shifted dataset triggers the drift demonstration. Delayed outcome labels unlock actual performance metrics. Drift alone does not justify production promotion; independent labeled evaluation and ranking/calibration/recall guards are required.

## Challenges and tradeoffs

The source dictionary and observed charge bands disagreed. Exact duplicate profiles made naive row-level splitting inappropriate. Neural complexity did not beat the selected tabular model. Local infrastructure required native PostgreSQL and a portable Redis because Docker was unavailable. These constraints shaped a reproducible demo with explicitly bounded claims.

## Results and deployment

The application ran locally, stored real predictions, completed actual Celery jobs and produced real dashboard screenshots, SHAP/ROC/PR/calibration/drift figures and measured latency. Tests exercise model, API and database contracts. Container definitions and an optional validated AWS Terraform foundation support further deployment work; no AWS production deployment or revenue impact is claimed. Consult VALIDATION.md for the latest CI and clean-checkout status.

## Next steps

Obtain recent event-level data and independent outcomes; validate chronologically; use intervention costs for threshold policy; audit demographic performance; add OIDC/RBAC, idempotency and signed artifacts; test concurrent load, canary releases, rollback and backups. The strongest portfolio evidence is the reproducible lifecycle and its honest limits.
