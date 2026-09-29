# Model card

Intended use: educational churn-risk prioritization and ML lifecycle demonstration. Not an autonomous retention decision system.

Selected family: **xgboost**, model version `20260929T031916Z`, threshold `0.10`, seed 42, dataset SHA-256 `90d5fb6bd1630cd4de4b4d28fcf8b4cb92a8f6ab7484605b0799d47386f7dbe1`.

| Model | Validation AP | Test ROC-AUC | Test AP | Precision | Recall | F1 | Fit/search s |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic | 0.7010 | 0.9312 | 0.7673 | 0.6964 | 0.7959 | 0.7429 | 0.64 |
| random_forest | 0.9340 | 0.9892 | 0.9437 | 0.8519 | 0.9388 | 0.8932 | 3.61 |
| xgboost **(selected)** | 0.9392 | 0.9852 | 0.9425 | 0.8491 | 0.9184 | 0.8824 | 1.05 |
| pytorch | 0.8278 | 0.9465 | 0.8087 | 0.7750 | 0.6327 | 0.6966 | 7.04 |


## Selection and calibration

Choose the highest calibrated validation average precision, then maximize validation F1 over thresholds 0.05–0.95 in steps of 0.01. This demo policy treats precision/recall symmetrically; real intervention costs may call for another threshold. Logistic regression and Random Forest use class weights; PyTorch uses positive-class-weighted BCE; XGBoost is an unweighted probability baseline. Every family receives three-fold grouped CV with two configurations. A small equal search budget does not establish each family's best possible performance.

Sigmoid calibration is fitted on separate data. Both uncalibrated and calibrated validation metrics are saved; calibration is not claimed to improve every metric for every model. PR ranking can remain unchanged under monotonic calibration. No model is retuned after test inspection.

324 duplicate predictor profiles were detected and grouped. Test confusion matrix (actual rows 0/1, predicted columns 0/1): `[[256, 8], [4, 45]]`. See uncertainty.json for bootstrap and coarse age-slice diagnostics. These are not a complete fairness or temporal-generalization assessment.

Excluded fields: account status (shortcut risk), customer value (derived target), age group (redundant), row ID and churn. Current behavioral attributes are nine-month aggregates; source data has no usable event timestamps. See DATA.md for intended units, missingness and schema discrepancy.

## Limitations

One company and historical geography; coarse demographic fields; small positive test count; near duplicates may remain; no external validation; no causal retention evidence; no audited future-revenue labels. The auxiliary value regression may reconstruct a source formula and should not be marketed as future revenue prediction. Retrain on recent consented data and evaluate temporal/business/fairness outcomes before operational use.
