"""
Machine Learning module (Phase 4): accident-risk prediction.

Trains multiple classifiers, evaluates them on a common metric set, and
automatically selects the best performer by ROC-AUC (a good choice for
imbalanced accident data, where raw accuracy is misleading).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from app.core.config import settings


@dataclass
class MLResult:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    artifact_path: str


MODEL_REGISTRY = {
    "random_forest": lambda rs: RandomForestClassifier(n_estimators=300, max_depth=12, random_state=rs, n_jobs=-1),
    "xgboost": lambda rs: XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.05, eval_metric="logloss", random_state=rs, n_jobs=-1
    ),
    "lightgbm": lambda rs: LGBMClassifier(n_estimators=300, max_depth=-1, learning_rate=0.05, random_state=rs),
    "decision_tree": lambda rs: DecisionTreeClassifier(max_depth=10, random_state=rs),
}


def _evaluate(model, X_test, y_test) -> Dict[str, float]:
    y_pred = model.predict(X_test)
    # roc_auc needs probability scores; fall back gracefully if unavailable
    try:
        y_proba = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_proba)
    except Exception:
        roc_auc = float("nan")

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc,
    }


def train_and_compare(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str,
    model_names: List[str],
    model_dir: str = None,
    random_state: int = None,
) -> tuple[List[MLResult], MLResult]:
    """
    Trains each requested model, evaluates on the held-out test set, saves
    every artifact to disk, and returns (all_results, best_result).
    """
    model_dir = model_dir or settings.MODEL_DIR
    random_state = random_state if random_state is not None else settings.RANDOM_STATE
    os.makedirs(model_dir, exist_ok=True)

    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]

    results: List[MLResult] = []

    for name in model_names:
        if name not in MODEL_REGISTRY:
            continue
        model = MODEL_REGISTRY[name](random_state)
        model.fit(X_train, y_train)

        metrics = _evaluate(model, X_test, y_test)
        artifact_path = os.path.join(model_dir, f"accident_{name}.joblib")
        joblib.dump(model, artifact_path)

        results.append(MLResult(model_name=name, artifact_path=artifact_path, **metrics))

    # Best model = highest ROC-AUC (falls back to F1 if AUC is NaN for all)
    valid = [r for r in results if not np.isnan(r.roc_auc)]
    best = max(valid, key=lambda r: r.roc_auc) if valid else max(results, key=lambda r: r.f1_score)

    # Persist a small metadata file pointing to the best model for quick lookup at inference time
    best_meta_path = os.path.join(model_dir, "accident_best_model.json")
    with open(best_meta_path, "w") as f:
        json.dump(asdict(best), f, indent=2)

    return results, best


def predict_accident_risk(features: dict, model_dir: str = None) -> dict:
    """Loads the currently-best accident model and scores a single input."""
    model_dir = model_dir or settings.MODEL_DIR
    meta_path = os.path.join(model_dir, "accident_best_model.json")

    with open(meta_path) as f:
        best_meta = json.load(f)

    model = joblib.load(best_meta["artifact_path"])
    X = pd.DataFrame([features])
    proba = model.predict_proba(X)[:, 1][0]

    if proba < 0.3:
        risk_level = "low"
    elif proba < 0.6:
        risk_level = "medium"
    else:
        risk_level = "high"

    return {
        "accident_probability": float(proba),
        "risk_level": risk_level,
        "model_used": best_meta["model_name"],
    }
