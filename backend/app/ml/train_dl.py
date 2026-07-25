"""
Deep Learning module (Phase 5): traffic congestion / volume forecasting.

Uses LSTM and GRU sequence models to predict future traffic values from a
sliding window of past observations. Both architectures are trained and
compared on RMSE/MAE/MAPE, mirroring the ML module's "train + compare +
pick best" pattern for consistency across the codebase.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from sklearn.metrics import mean_squared_error, mean_absolute_error

from app.core.config import settings


@dataclass
class DLResult:
    model_name: str
    rmse: float
    mae: float
    mape: float
    artifact_path: str
    history: dict  # loss / val_loss per epoch, for plotting


def create_sequences(series: np.ndarray, seq_len: int) -> Tuple[np.ndarray, np.ndarray]:
    """Turns a 1D series into (X, y) sliding-window supervised pairs."""
    X, y = [], []
    for i in range(len(series) - seq_len):
        X.append(series[i : i + seq_len])
        y.append(series[i + seq_len])
    return np.array(X), np.array(y)


def build_lstm(seq_len: int) -> tf.keras.Model:
    model = models.Sequential([
        layers.Input(shape=(seq_len, 1)),
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.2),
        layers.LSTM(32),
        layers.Dropout(0.2),
        layers.Dense(16, activation="relu"),
        layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def build_gru(seq_len: int) -> tf.keras.Model:
    model = models.Sequential([
        layers.Input(shape=(seq_len, 1)),
        layers.GRU(64, return_sequences=True),
        layers.Dropout(0.2),
        layers.GRU(32),
        layers.Dropout(0.2),
        layers.Dense(16, activation="relu"),
        layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


BUILDERS = {"lstm": build_lstm, "gru": build_gru}


def _mape(y_true, y_pred, eps=1e-6) -> float:
    return float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + eps))) * 100)


def train_and_compare_dl(
    series: pd.Series,
    model_names: List[str],
    seq_len: int = None,
    epochs: int = 20,
    batch_size: int = 32,
    model_dir: str = None,
) -> Tuple[List[DLResult], DLResult]:
    """
    Trains each requested DL model on the same train/val/test split of the
    series, evaluates, saves artifacts, and returns (all_results, best_result).
    """
    seq_len = seq_len or settings.LSTM_SEQUENCE_LENGTH
    model_dir = model_dir or settings.MODEL_DIR
    os.makedirs(model_dir, exist_ok=True)

    values = series.values.astype("float32").reshape(-1, 1)
    # simple min-max scale to [0, 1] for stable training
    v_min, v_max = values.min(), values.max()
    scaled = (values - v_min) / (v_max - v_min + 1e-9)

    X, y = create_sequences(scaled.flatten(), seq_len)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    n = len(X)
    train_end, val_end = int(n * 0.7), int(n * 0.85)
    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]

    results: List[DLResult] = []

    for name in model_names:
        if name not in BUILDERS:
            continue
        model = BUILDERS[name](seq_len)
        es = callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

        hist = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[es],
            verbose=0,
        )

        y_pred_scaled = model.predict(X_test, verbose=0).flatten()
        # inverse-scale back to real traffic units before computing metrics
        y_pred = y_pred_scaled * (v_max - v_min) + v_min
        y_true = y_test * (v_max - v_min) + v_min

        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))
        mape = _mape(y_true, y_pred)

        artifact_path = os.path.join(model_dir, f"congestion_{name}.keras")
        model.save(artifact_path)

        results.append(DLResult(
            model_name=name, rmse=rmse, mae=mae, mape=mape, artifact_path=artifact_path,
            history={"loss": hist.history["loss"], "val_loss": hist.history["val_loss"]},
        ))

    best = min(results, key=lambda r: r.rmse)

    best_meta_path = os.path.join(model_dir, "congestion_best_model.json")
    with open(best_meta_path, "w") as f:
        meta = asdict(best)
        meta["scale_min"] = float(v_min)
        meta["scale_max"] = float(v_max)
        meta["seq_len"] = seq_len
        json.dump(meta, f, indent=2)

    return results, best


def predict_congestion(recent_sequence: List[float], model_dir: str = None) -> dict:
    """Loads the current best DL model and forecasts the next value from a recent window."""
    model_dir = model_dir or settings.MODEL_DIR
    meta_path = os.path.join(model_dir, "congestion_best_model.json")

    with open(meta_path) as f:
        meta = json.load(f)

    seq_len = meta["seq_len"]
    if len(recent_sequence) != seq_len:
        raise ValueError(f"Expected a sequence of length {seq_len}, got {len(recent_sequence)}")

    model = tf.keras.models.load_model(meta["artifact_path"])

    v_min, v_max = meta["scale_min"], meta["scale_max"]
    scaled = (np.array(recent_sequence, dtype="float32") - v_min) / (v_max - v_min + 1e-9)
    X = scaled.reshape((1, seq_len, 1))

    pred_scaled = model.predict(X, verbose=0).flatten()[0]
    pred = float(pred_scaled * (v_max - v_min) + v_min)

    # crude congestion banding relative to historical range — tune thresholds per real dataset
    relative = (pred - v_min) / (v_max - v_min + 1e-9)
    level = "low" if relative < 0.33 else "moderate" if relative < 0.66 else "high"

    return {
        "predicted_next_values": [pred],
        "congestion_level": level,
        "model_used": meta["model_name"],
    }
