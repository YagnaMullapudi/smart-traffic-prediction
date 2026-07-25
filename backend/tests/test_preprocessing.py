"""Unit tests for the preprocessing pipeline (Module 13: Testing)."""
import numpy as np
import pandas as pd

from app.ml.preprocessing import (
    handle_missing_values, remove_duplicates, cap_outliers_iqr,
    encode_categorical, generate_time_features, PreprocessReport,
)


def make_sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=10, freq="h"),
        "speed": [30, 32, np.nan, 31, 29, 1000, 33, 34, 30, 30],  # includes missing + outlier
        "road_type": ["highway", "highway", "local", None, "local", "highway", "local", "local", "highway", "highway"],
        "accident": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    })


def test_handle_missing_values_fills_numeric_and_categorical():
    df = make_sample_df()
    report = PreprocessReport()
    df = handle_missing_values(df, report)
    assert df["speed"].isnull().sum() == 0
    assert df["road_type"].isnull().sum() == 0
    assert "speed" in report.missing_value_summary


def test_remove_duplicates():
    df = make_sample_df()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    report = PreprocessReport()
    df = remove_duplicates(df, report)
    assert report.duplicates_removed == 1


def test_cap_outliers_iqr_reduces_extreme_value():
    df = make_sample_df()
    report = PreprocessReport()
    df["speed"] = df["speed"].fillna(df["speed"].median())
    df = cap_outliers_iqr(df, report, columns=["speed"])
    assert df["speed"].max() < 1000
    assert "speed" in report.outliers_capped


def test_generate_time_features_adds_expected_columns():
    df = make_sample_df()
    report = PreprocessReport()
    df = generate_time_features(df, report, datetime_col="timestamp")
    for col in ["hour", "day_of_week", "is_weekend", "is_peak_hour"]:
        assert col in df.columns


def test_encode_categorical_converts_to_numeric():
    df = make_sample_df()
    df["road_type"] = df["road_type"].fillna("unknown")
    report = PreprocessReport()
    df = encode_categorical(df, report)
    assert pd.api.types.is_numeric_dtype(df["road_type"])
    assert "road_type" in report.encoded_columns
