# Dataset, lineage and feature contract

Source: [UCI Iranian Churn, DOI 10.24432/C5JW3Z](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset). License: **Creative Commons Attribution 4.0**. The preserved UCI response is [dataset-source.json](dataset-source.json). Credit UCI and the original dataset contributors when redistributing. This repository's MIT license applies to code; it does not replace the dataset license.

The downloadable dataset contains 3,150 customer records, 13 original attributes and a binary churn label. UCI describes attributes aggregated over the first nine months, with churn measured at month twelve: a three-month planning gap. There are no real identifiers in the file; `UCI-xxxxx` IDs are deterministic row references created here. The full raw data is downloaded, not committed. A 25-row attributed sample is included.

[The measured data report](data-report.json) records the SHA-256, missingness, prevalence, duplicate profiles and split sizes. Original data has no missing values. Numeric missing values are nevertheless supported by median imputation learned within training folds; categorical values use most-frequent imputation. Extra API fields are rejected; valid tariff/complaint categories and finite nonnegative ranges are enforced with Pydantic. Offline checks enforce the same core schema with explicit pandas validation; a second schema framework would add little value here.

| Field | Meaning / units | Model use |
|---|---|---|
| call_failures | Number of failed calls | Numeric |
| complaints | Complaint indicator, 0/1 | Categorical |
| tenure | Subscription length, months | Numeric |
| charge_band | Ordinal spending band | Numeric; **0–10 observed** |
| seconds_of_use | Aggregated call duration, seconds | Numeric |
| call_count | Aggregated number of calls | Numeric |
| sms_count | Aggregated message count | Numeric |
| distinct_contacts | Distinct called numbers | Numeric |
| tariff_plan | 1 pay-as-you-go, 2 contractual | One-hot categorical |
| age | Age in years | Numeric; requires fairness review |
| age_group | Coarser age encoding | Excluded as redundant |
| status | Active/inactive indicator | Excluded as a potential churn shortcut |
| customer_value | Source's calculated value index | Auxiliary regression target only |
| churn | 0 retained / 1 churned | Classification target only |

Source discrepancy: UCI documents charge bands 0–9, but seven records have value 10. These are retained with a documented 0–10 contract, rather than silently dropped or clipped.

Engineered features (all deterministic; denominator clipped to at least one):
- `seconds_per_call = seconds_of_use / call_count`.
- `failure_rate = call_failures / call_count`; this can exceed one and is a ratio, not a bounded probability.
- `calls_per_month = call_count / tenure` and `sms_per_month = sms_count / tenure`. These are **tenure-normalized engagement proxies**. Since usage covers nine months while tenure spans the subscription, they are not observed monthly event rates.
- `contact_diversity = distinct_contacts / call_count`.

No fabricated support history, usage trend, actual monthly spend, contract duration or future revenue is added. Static aggregates cannot provide those signals.

Identical ten-feature predictor profiles are grouped, including conflicting labels. A seeded ten-fold StratifiedGroupKFold assigns six folds to training, two to calibration, one to validation and one to test. Three-fold grouped CV is nested inside training. IDs, labels, value, status and age group never enter predictors. The same FeatureBuilder and ColumnTransformer run in training and inference.

Limitations: one telecom company, historical Iranian customer population, coarse ages, small positive test count, no timestamps for chronological splitting, no causal intervention data and incomplete documentation of the source value formula. Near-duplicate profiles can still exist after exact-profile grouping. Geographic, demographic and collection bias limit transfer. Age-slice metrics are exploratory, not a fairness certification. Obtain recent consented event data, perform temporal validation and a proper group audit before business use.
