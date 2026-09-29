# Engineering decisions and lessons

- **UCI rather than ambiguous sample licensing:** explicit CC BY 4.0 and an outcome gap support honest attribution and modeling. Cost: no monetary spend or future revenue target; we clearly use a value index.
- **Pydantic plus explicit dataframe checks:** the same bounded input domain serves HTTP and offline data. Median/most-frequent imputation is fold-local; no all-data preprocessing before CV.
- **Exact-profile grouping:** the dataset contains repeated predictor profiles. Random row splitting can inflate metrics. Grouping applies to train/calibration/validation/test and CV; near duplicates remain a limitation.
- **Status exclusion:** active/inactive status might supply an overly convenient shortcut. Excluding it favors a behavior-based demonstration. This is a conservative design choice, not proof that the source field was collected after the outcome.
- **Classical and neural comparison:** different inductive biases matter. A small CPU MLP is a legitimate comparison, not a claim that neural networks should win tabular problems.
- **Separate calibration and selection:** class weights alter probability interpretation. Separate sigmoid calibration is reproducible; validation metrics document whether it helped. Test observations do not change the winner.
- **Value-index regression:** demonstrates a regression pipeline while explicitly limiting the interpretation. Reconstructing an observed formula is easier than predicting business revenue.
- **Model-agnostic SHAP:** explains calibrated output directly across all families. More expensive than native tree SHAP, so explanations are separate from synchronous scoring and use bounded permutations.
- **MLflow plus local serving bundle:** experiment/registry provenance with fast self-contained serving. Local promotion is atomic, but alias changes and filesystem state are not a distributed transaction. A deployment controller is future work.
- **PostgreSQL by default in Compose, SQLite for quick start:** both share SQLAlchemy models and migrations. Native PostgreSQL tests demonstrate actual JSON/transaction behavior rather than pretending SQLite validates every database semantic.
- **Redis has two concrete uses:** shared rate-limit windows and Celery broker/result storage. No speculative prediction cache is added; every scored event is persisted.
- **React/Vite:** simpler static deployment than server rendering for an authenticated analytics product. Pages and shared components are separated; Tailwind and a small semantic CSS system maintain the visual language.
- **Infrastructure foundation only:** a validated Terraform module is useful without pretending account-specific edge/auth/networking has been deployed. The AWS runbook states the remaining production integration.

Unexpected issues found during implementation: source charge-band documentation mismatch; missing macOS OpenMP; current MLflow serialization defaults rejecting custom estimators; isolated PostgreSQL encoding mismatch; missing local compiler/Docker; frontend test-runner audit findings. Fixes were verified rather than hidden. Trusted cloudpickle serialization is explicitly documented; an untrusted model artifact is never accepted over HTTP.

Known operational gaps: job idempotency, distributed promotion locking, cloud artifact hydration/signing, frontend end-user authentication, multi-tenant authorization, audited privacy retention, background request cancellation, load saturation tests and real chronological drift windows. The live UI's totals count prediction events, not unique accounts; repeated benchmark requests therefore change the displayed totals.
