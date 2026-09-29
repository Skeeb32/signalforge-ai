"""Deterministic features; all learned preprocessing is fitted inside CV folds."""
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from signalforge.data import INPUTS

ENGINEERED = ["seconds_per_call", "failure_rate", "calls_per_month", "sms_per_month",
              "contact_diversity"]
NUMERIC = [x for x in INPUTS if x not in ["tariff_plan", "complaints"]] + ENGINEERED


class FeatureBuilder(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        frame = pd.DataFrame(X).copy()
        frame["seconds_per_call"] = frame.seconds_of_use / frame.call_count.clip(lower=1)
        frame["failure_rate"] = frame.call_failures / frame.call_count.clip(lower=1)
        frame["calls_per_month"] = frame.call_count / frame.tenure.clip(lower=1)
        frame["sms_per_month"] = frame.sms_count / frame.tenure.clip(lower=1)
        frame["contact_diversity"] = frame.distinct_contacts / frame.call_count.clip(lower=1)
        return frame[INPUTS + ENGINEERED]


def preprocessing() -> Pipeline:
    numeric = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return Pipeline([("features", FeatureBuilder()), ("columns", ColumnTransformer([
        ("numeric", numeric, NUMERIC), ("category", categorical, ["tariff_plan", "complaints"])
    ]))])
