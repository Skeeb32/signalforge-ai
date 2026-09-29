# Technical interview guide

**Why XGBoost?** It had the highest validation average precision under the fixed search/calibration protocol. Random Forest slightly won on test; switching afterward would tune to the test set. This is a measured choice, not a universal claim about algorithms.

**Why compare logistic regression?** It establishes a fast, interpretable linear baseline. If it performed similarly, simpler serving and explanation could favor it. Here nonlinear models captured additional structure.

**Why PyTorch on tabular data?** To test a different model family through the same preprocessing and sklearn-compatible interface. Weighted BCE, deterministic seeds and a bounded MLP make the comparison reproducible. It did not win, which is a useful result.

**How is leakage prevented?** Labels, value, status and IDs are excluded; exact profiles are grouped across partitions and CV; learned imputation/scaling/encoding happen inside folds. Calibration, threshold/family selection and final evaluation use separate data. Lack of timestamps prevents a genuine chronological backtest.

**How is imbalance handled?** Compare AP/recall/precision instead of relying on accuracy. Logistic/RF use class weights, the MLP uses positive-weighted BCE, and all outputs receive separate calibration. The threshold is validation-selected; no oversampling is applied across split boundaries.

**Why PR-AUC?** Average precision emphasizes positive-class retrieval and reflects the precision/recall tradeoff in an imbalanced dataset. It depends on prevalence and is not interchangeable with ROC-AUC or trapezoidal PR area.

**How did you select the threshold?** Maximize validation F1 on a documented 0.01 grid. In a company, obtain false-positive/negative and intervention costs and choose a business utility policy; never derive the threshold from the test set.

**Does calibration guarantee correct probabilities?** No. Sigmoid calibration learns a correction on a separate sample; Brier/log loss and calibration plots check behavior. Population shift can break calibration. A small calibration set adds uncertainty.

**How does SHAP work here?** Permutation SHAP estimates each feature's marginal contribution relative to training background rows while evaluating the full calibrated pipeline. Baseline plus contributions approximates the prediction; a test checks additivity. Correlated features complicate attribution and contributions are not causal effects.

**What is revenue risk?** An honestly named value-index exposure proxy: churn probability times predicted observed value index. The source has no currency/future realized-revenue labels. The regression result is not evidence of future revenue prediction or savings.

**What happens during drift?** Report schema/quality, PSI and KS comparisons, inspect sample size and the affected features, and collect outcomes. A candidate can be trained when drift and labels exist, but a disjoint labeled-window gate must pass before promotion.

**How would you retrain and roll back?** Immutable versioned bundles, candidate/production/archived MLflow aliases, explicit metric guardrails and atomic local version switching. Keep the old bundle. A cloud rollout needs a reconciled release controller, canary traffic and automatic rollback; local alias/filesystem updates are not a distributed transaction.

**Why PostgreSQL and Redis?** PostgreSQL provides durable auditable prediction/label/version records and transactions. Redis implements a shared rate-limit counter and Celery messaging/results; its use is functional rather than decorative.

**What if a job is delivered twice?** Celery may deliver at least once. This demo can record duplicate events; production should require idempotency keys with a database uniqueness constraint and transactionally deduplicated job effects.

**How do you measure production model quality?** Join delayed actual labels to prediction IDs and version, compute metrics only when enough labeled classes exist, track label coverage/lag and calibration, and segment cohorts. Missing labels must not become fake performance statistics.

**How would you scale to 10,000 predictions/s?** First measure concurrent saturation and SLOs. Profile preprocessing and dual-model cost, batch where possible, vectorize row serialization, separate explanations, scale stateless replicas, tune DB pools/write queues, and size infrastructure from load tests. Current sequential local benchmarks do not establish that capacity.

**How would you deploy on AWS?** Private ECS/Fargate tasks, ECR digests, signed/versioned S3 bundles, RDS, private Redis/MLflow, CloudWatch and HTTPS/OIDC at the edge. Terraform currently provisions only the foundation; the runbook documents remaining service/network/auth configuration.

**How is the API secured?** Strict schemas, bounded CSV/batches, formula-safe identifiers, constant-time optional API-key comparison, CORS, rate limits and non-root containers. Enterprise identity, tenant authorization, privacy controls and gateway protections remain required.

**What happens if the model is biased?** Evaluate meaningful groups with uncertainty and adequate sample sizes, examine proxy features and collection bias, review harm with stakeholders, and constrain or withdraw deployment where appropriate. The coarse age-slice report is exploratory, not a fairness certification.

**What was the most important lesson?** Good metrics cannot replace correct evaluation boundaries, traceable data, honest semantics, actual integration tests and clear statements of what has not been deployed or measured.
