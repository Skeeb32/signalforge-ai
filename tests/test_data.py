import numpy as np
import pandas as pd
import pytest

from signalforge.data import INPUTS, load, validate
from signalforge.features import FeatureBuilder, preprocessing
from signalforge.schemas import Customer


def test_feature_ratios_are_finite_at_zero(customer):
    customer.update(tenure=0, call_count=0)
    values = FeatureBuilder().transform(pd.DataFrame([customer]))
    assert np.isfinite(values.to_numpy(dtype=float)).all()
    assert values.seconds_per_call.iloc[0] == customer["seconds_of_use"]


def test_target_and_shortcut_are_not_features():
    frame = pd.read_csv("data/sample/customers.csv")
    built = FeatureBuilder().transform(frame)
    assert not {"churn", "status", "customer_value", "age_group", "customer_id"} & set(
        built.columns
    )


def test_imputation_fits_on_training_only():
    frame = pd.read_csv("data/sample/customers.csv")
    pre = preprocessing().fit(frame)
    original = (
        pre.named_steps["columns"]
        .named_transformers_["numeric"]
        .named_steps["impute"]
        .statistics_.copy()
    )
    test = frame.head(2).copy()
    test["seconds_of_use"] = np.nan
    transformed = pre.transform(test)
    assert np.isfinite(transformed).all()
    np.testing.assert_equal(
        original,
        pre.named_steps["columns"].named_transformers_["numeric"].named_steps["impute"].statistics_,
    )


@pytest.mark.parametrize(
    "change",
    [
        {"age": -1},
        {"tariff_plan": 9},
        {"complaints": 2},
        {"call_count": float("inf")},
        {"charge_band": 11},
    ],
)
def test_schema_rejects_invalid_values(customer, change):
    customer.update(change)
    with pytest.raises(ValueError):
        Customer.model_validate(customer)


def test_documented_charge_band_discrepancy_is_accepted(customer):
    customer["charge_band"] = 10
    assert Customer.model_validate(customer).charge_band == 10


def test_dataset_contract():
    assert validate(load(__import__("pathlib").Path("data/sample/customers.csv")))["rows"] == 25


def test_split_profiles_disjoint():
    from pathlib import Path

    if not Path("data/processed/test.csv").exists():
        pytest.skip("Prepare data first")
    splits = [
        pd.read_csv(f"data/processed/{name}.csv")
        for name in ["train", "calibration", "validation", "test"]
    ]
    groups = [set(pd.util.hash_pandas_object(frame[INPUTS], index=False)) for frame in splits]
    for i, left in enumerate(groups):
        for right in groups[i + 1 :]:
            assert not left & right
