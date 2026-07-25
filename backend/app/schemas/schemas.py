"""
Pydantic schemas. These define the API's public contract, separate from the
ORM models so internal DB structure never leaks directly into responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Datasets ----------
class DatasetOut(BaseModel):
    id: int
    filename: str
    rows: Optional[int]
    columns: Optional[int]
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---------- ML (accident prediction) ----------
class MLTrainRequest(BaseModel):
    dataset_id: int
    target_column: str = "accident"
    models: List[str] = ["random_forest", "xgboost", "lightgbm", "decision_tree"]


class MLTrainResult(BaseModel):
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float


class AccidentPredictRequest(BaseModel):
    features: Dict[str, Any]


class AccidentPredictResponse(BaseModel):
    accident_probability: float
    risk_level: str
    model_used: str


# ---------- DL (congestion forecasting) ----------
class DLTrainRequest(BaseModel):
    dataset_id: int
    target_column: str = "traffic_volume"
    sequence_length: int = 24
    epochs: int = 20
    models: List[str] = ["lstm", "gru"]


class DLTrainResult(BaseModel):
    model_name: str
    rmse: float
    mae: float
    mape: float


class CongestionPredictRequest(BaseModel):
    recent_sequence: List[float]  # last N observations (length == sequence_length)


class CongestionPredictResponse(BaseModel):
    predicted_next_values: List[float]
    congestion_level: str
    model_used: str


# ---------- Route recommendation ----------
class RouteRequest(BaseModel):
    origin_node: str
    destination_node: str
    algorithm: str = "dijkstra"  # or "astar"


class RouteResponse(BaseModel):
    path: List[str]
    total_distance_km: float
    estimated_time_minutes: float
    congestion_adjusted: bool


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_datasets: int
    total_predictions: int
    best_ml_model: Optional[str]
    best_dl_model: Optional[str]
    avg_accident_risk: Optional[float]
