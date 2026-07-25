"""ML endpoints: train + compare accident-risk models, then predict (Module 4)."""
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import User, Dataset, ModelResult
from app.ml.preprocessing import preprocess_pipeline, train_val_test_split
from app.ml.train_ml import train_and_compare, predict_accident_risk
from app.schemas.schemas import MLTrainRequest, MLTrainResult, AccidentPredictRequest, AccidentPredictResponse

router = APIRouter(prefix="/api/ml", tags=["machine-learning"])


@router.post("/train", response_model=List[MLTrainResult])
def train_ml_models(
    payload: MLTrainRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == payload.dataset_id, Dataset.owner_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df, _report = preprocess_pipeline(dataset.filepath, target_col=payload.target_column)
    train_df, _val_df, test_df = train_val_test_split(df, payload.target_column)

    results, best = train_and_compare(
        train_df, test_df, target_col=payload.target_column, model_names=payload.models
    )

    # Persist results for the dashboard / history view
    for r in results:
        db.add(ModelResult(
            model_type="ML",
            model_name=r.model_name,
            task="accident_prediction",
            metrics_json=json.dumps({
                "accuracy": r.accuracy, "precision": r.precision, "recall": r.recall,
                "f1_score": r.f1_score, "roc_auc": r.roc_auc,
            }),
            artifact_path=r.artifact_path,
            is_best=(r.model_name == best.model_name),
        ))
    db.commit()

    return [
        MLTrainResult(
            model_name=r.model_name, accuracy=r.accuracy, precision=r.precision,
            recall=r.recall, f1_score=r.f1_score, roc_auc=r.roc_auc,
        )
        for r in results
    ]


@router.post("/predict", response_model=AccidentPredictResponse)
def predict_accident(payload: AccidentPredictRequest, current_user: User = Depends(get_current_user)):
    try:
        result = predict_accident_risk(payload.features)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="No trained accident model found. Train a model first.")
    return result
