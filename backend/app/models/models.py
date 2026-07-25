"""
ORM models. Kept in one file for a project this size; split per-domain
(users.py, datasets.py, ...) if the schema grows significantly.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    datasets = relationship("Dataset", back_populates="owner")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    rows = Column(Integer, nullable=True)
    columns = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="datasets")


class ModelResult(Base):
    """Stores metrics for each trained model run so results are comparable over time."""
    __tablename__ = "model_results"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(50))       # "ML" or "DL"
    model_name = Column(String(100))      # e.g. "XGBoost", "LSTM"
    task = Column(String(100))            # e.g. "accident_prediction", "congestion_forecast"
    metrics_json = Column(Text)           # JSON-serialized metrics dict
    artifact_path = Column(String(500))   # where the trained model file is saved
    trained_at = Column(DateTime, default=datetime.utcnow)
    is_best = Column(Boolean, default=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_result_id = Column(Integer, ForeignKey("model_results.id"))
    input_json = Column(Text)
    output_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20))            # INFO / WARNING / ERROR
    source = Column(String(100))          # e.g. "ml.train", "api.predict"
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
