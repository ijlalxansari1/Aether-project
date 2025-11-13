"""
Ethical Analysis Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import pandas as pd
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset
from app.modules import ethical
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/scan/{dataset_id}")
async def ethical_scan(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Load dataset (supports both local and cloud storage)
    from app.modules.dataset_loader import load_dataset
    try:
        df = await load_dataset(dataset.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading dataset: {str(e)}")

    result = ethical.run_ethical_scan(df)
    return jsonable_encoder(result)
