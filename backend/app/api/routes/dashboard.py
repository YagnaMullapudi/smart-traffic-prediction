"""Dashboard statistics endpoint (Module 7 data source)."""
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import User, Dataset, ModelResult, Prediction
from app.schemas.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).count()
    total_predictions = db.query(Prediction).count()

    best_ml = db.query(ModelResult).filter(ModelResult.model_type == "ML", ModelResult.is_best.is_(True)) \
        .order_by(ModelResult.trained_at.desc()).first()
    best_dl = db.query(ModelResult).filter(ModelResult.model_type == "DL", ModelResult.is_best.is_(True)) \
        .order_by(ModelResult.trained_at.desc()).first()

    avg_risk = None
    if best_ml:
        metrics = json.loads(best_ml.metrics_json)
        avg_risk = metrics.get("accuracy")

    return DashboardStats(
        total_datasets=total_datasets,
        total_predictions=total_predictions,
        best_ml_model=best_ml.model_name if best_ml else None,
        best_dl_model=best_dl.model_name if best_dl else None,
        avg_accident_risk=avg_risk,
    )
