"""
Data preprocessing pipeline (Phase 2).

Design notes:
- Every step is a standalone function so it can be unit-tested and reused
  independently by both the ML (tabular) and DL (time-series) pipelines.
- `preprocess_pipeline()` orchestrates the full flow and returns both the
  cleaned DataFrame and a report describing what was done — useful for the
  frontend EDA/preprocessing summary screens.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split


@dataclass
class PreprocessReport:
    initial_rows: int = 0
    final_rows: int = 0
    duplicates_removed: int = 0
    missing_value_summary: dict = field(default_factory=dict)
    outliers_capped: dict = field(default_factory=dict)
    encoded_columns: List[str] = field(default_factory=list)
    engineered_features: List[str] = field(default_factory=list)


def load_dataset(filepath: str) -> pd.DataFrame:
    """Load CSV (or parquet) traffic dataset from disk."""
    if filepath.endswith(".parquet"):
        return pd.read_parquet(filepath)
    return pd.read_csv(filepath)


def handle_missing_values(df: pd.DataFrame, report: PreprocessReport) -> pd.DataFrame:
    """
    Numeric columns: median imputation (robust to outliers).
    Categorical columns: mode imputation.
    """
    missing_before = df.isnull().sum()
    report.missing_value_summary = {
        col: int(count) for col, count in missing_before.items() if count > 0
    }

    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            mode_val = df[col].mode()
            df[col] = df[col].fillna(mode_val.iloc[0] if not mode_val.empty else "unknown")
    return df


def remove_duplicates(df: pd.DataFrame, report: PreprocessReport) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    report.duplicates_removed = before - len(df)
    return df


def cap_outliers_iqr(df: pd.DataFrame, report: PreprocessReport, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Cap outliers using the IQR method rather than dropping rows (preserves data volume)."""
    numeric_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
        if n_outliers > 0:
            df[col] = df[col].clip(lower, upper)
            report.outliers_capped[col] = n_outliers
    return df


def encode_categorical(df: pd.DataFrame, report: PreprocessReport) -> pd.DataFrame:
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    report.encoded_columns = cat_cols
    return df


def generate_time_features(df: pd.DataFrame, report: PreprocessReport, datetime_col: str = "timestamp") -> pd.DataFrame:
    """Derives hour/day/week/month/is_weekend/is_peak_hour from a timestamp column, if present."""
    if datetime_col not in df.columns:
        return df

    df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")
    df["hour"] = df[datetime_col].dt.hour
    df["day_of_week"] = df[datetime_col].dt.dayofweek
    df["day_of_month"] = df[datetime_col].dt.day
    df["week"] = df[datetime_col].dt.isocalendar().week.astype(int)
    df["month"] = df[datetime_col].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_peak_hour"] = df["hour"].isin([7, 8, 9, 17, 18, 19]).astype(int)

    report.engineered_features.extend(
        ["hour", "day_of_week", "day_of_month", "week", "month", "is_weekend", "is_peak_hour"]
    )
    return df


def normalize_features(df: pd.DataFrame, exclude: Optional[List[str]] = None) -> tuple[pd.DataFrame, StandardScaler]:
    exclude = exclude or []
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df, scaler


def train_val_test_split(
    df: pd.DataFrame, target_col: str, test_size: float = 0.15, val_size: float = 0.15, random_state: int = 42
):
    """70/15/15 split by default. Stratifies on target if it looks categorical."""
    stratify = df[target_col] if df[target_col].nunique() < 20 else None

    train_val, test = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=stratify
    )
    stratify_tv = train_val[target_col] if stratify is not None else None
    relative_val_size = val_size / (1 - test_size)
    train, val = train_test_split(
        train_val, test_size=relative_val_size, random_state=random_state, stratify=stratify_tv
    )
    return train, val, test


def preprocess_pipeline(
    filepath: str,
    target_col: str,
    datetime_col: str = "timestamp",
    normalize: bool = True,
) -> tuple[pd.DataFrame, PreprocessReport]:
    """Full Phase 2 pipeline: load -> clean -> engineer -> encode -> (optionally) normalize."""
    report = PreprocessReport()

    df = load_dataset(filepath)
    report.initial_rows = len(df)

    df = remove_duplicates(df, report)
    df = handle_missing_values(df, report)
    df = generate_time_features(df, report, datetime_col=datetime_col)
    df = cap_outliers_iqr(df, report, columns=[c for c in df.select_dtypes(include=[np.number]).columns if c != target_col])
    df = encode_categorical(df, report)

    if normalize:
        df, _ = normalize_features(df, exclude=[target_col])

    report.final_rows = len(df)
    return df, report
