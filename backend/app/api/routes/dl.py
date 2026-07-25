"""DL endpoints: train + compare LSTM/GRU congestion models, then forecast (Module 5)."""
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.ml.preprocessing import load_dataset
from app.ml.train_dl import train_and_compare_dl, predict_congestion
from app.models.models import User, Dataset, ModelResult
from app.schemas.schemas import DLTrainRequest, DLTrainResult, CongestionPredictRequest, CongestionPredictResponse

router = APIRouter(prefix="/api/dl", tags=["deep-learning"])


@router.post("/train", response_model=List[DLTrainResult])
def train_dl_models(
    payload: DLTrainRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == payload.dataset_id, Dataset.owner_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset(dataset.filepath)
    if payload.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{payload.target_column}' not found in dataset")

    series = df[payload.target_column].dropna()

    results, best = train_and_compare_dl(
        series, model_names=payload.models, seq_len=payload.sequence_length, epochs=payload.epochs
    )

    for r in results:
        db.add(ModelResult(
            model_type="DL",
            model_name=r.model_name,
            task="congestion_forecast",
            metrics_json=json.dumps({"rmse": r.rmse, "mae": r.mae, "mape": r.mape}),
            artifact_path=r.artifact_path,
            is_best=(r.model_name == best.model_name),
        ))
    db.commit()

    return [DLTrainResult(model_name=r.model_name, rmse=r.rmse, mae=r.mae, mape=r.mape) for r in results]


@router.post("/predict", response_model=CongestionPredictResponse)
def predict_traffic_congestion(payload: CongestionPredictRequest, current_user: User = Depends(get_current_user)):
    try:
        result = predict_congestion(payload.recent_sequence)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="No trained congestion model found. Train a model first.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
