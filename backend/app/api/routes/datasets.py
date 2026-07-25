"""Dataset upload & listing endpoints (Module 1: Data Collection)."""
import os
import shutil
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.models.models import User, Dataset
from app.schemas.schemas import DatasetOut

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetOut)
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith((".csv", ".parquet")):
        raise HTTPException(status_code=400, detail="Only .csv or .parquet files are supported")

    os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
    save_path = os.path.join(settings.RAW_DATA_DIR, file.filename)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Quick shape check so the frontend can show row/column counts immediately
    try:
        df = pd.read_csv(save_path) if file.filename.endswith(".csv") else pd.read_parquet(save_path)
        rows, cols = df.shape
    except Exception:
        rows, cols = None, None

    dataset = Dataset(
        filename=file.filename, filepath=save_path, rows=rows, columns=cols, owner_id=current_user.id
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("/", response_model=List[DatasetOut])
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Dataset).filter(Dataset.owner_id == current_user.id).all()


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
