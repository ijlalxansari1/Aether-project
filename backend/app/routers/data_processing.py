"""
Data Processing Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset, DataProfile, AuditLog
from app.modules import data_processing
from app.modules import ingestion as ingestion_mod
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CleaningRequest(BaseModel):
    dataset_id: int
    operations: List[str]
    user_approved: bool = True


@router.get("/preview/{dataset_id}")
async def get_preview(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

    preview = ingestion_mod.get_preview(df)
    return jsonable_encoder(preview)


@router.get("/profile/{dataset_id}")
async def profile_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data profile for a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if dataset.file_path and os.path.exists(dataset.file_path):
        if dataset.file_path.endswith('.csv'):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
    else:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    profile = data_processing.profile_data(df)
    
    quality_score = data_processing.compute_data_quality_score(df)
    integrity_score = data_processing.compute_data_integrity_score(df)
    
    dataset.data_quality_score = float(quality_score)
    dataset.data_integrity_score = float(integrity_score)
    db.commit()
    
    for col_name, col_info in profile["columns"].items():
        db_profile = DataProfile(
            dataset_id=dataset_id,
            column_name=str(col_name),
            data_type=str(col_info["data_type"]),
            missing_count=int(col_info["missing_count"]),
            missing_percentage=float(col_info["missing_percentage"]),
            unique_count=int(col_info["unique_count"])
        )
        db.add(db_profile)
    db.commit()
    
    suggestions = data_processing.suggest_cleaning_operations(df, profile)
    
    preview = ingestion_mod.get_preview(df)

    return jsonable_encoder({
        "dataset_id": dataset_id,
        "profile": profile,
        "data_quality_score": quality_score,
        "data_integrity_score": integrity_score,
        "cleaning_suggestions": suggestions,
        "preview": preview
    })


@router.post("/clean")
async def clean_dataset(
    request: CleaningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if dataset.file_path and os.path.exists(dataset.file_path):
        if dataset.file_path.endswith('.csv'):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
    else:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    df_cleaned = data_processing.clean_data(df, request.user_approved, request.operations)
    
    cleaned_filename = f"cleaned_{dataset.filename}"
    cleaned_path = os.path.join(os.path.dirname(dataset.file_path), cleaned_filename)
    
    if cleaned_path.endswith('.csv'):
        df_cleaned.to_csv(cleaned_path, index=False)
    else:
        df_cleaned.to_excel(cleaned_path, index=False)
    
    dataset.file_path = cleaned_path
    dataset.filename = cleaned_filename
    
    quality_score = data_processing.compute_data_quality_score(df_cleaned)
    dataset.data_quality_score = float(quality_score)
    db.commit()
    
    audit = AuditLog(
        user_id=current_user.id,
        action="clean_data",
        resource_type="dataset",
        resource_id=dataset.id,
        details=f"Cleaned dataset with operations: {', '.join(request.operations)}"
    )
    db.add(audit)
    db.commit()
    
    return jsonable_encoder({
        "dataset_id": dataset.id,
        "cleaned": True,
        "new_quality_score": quality_score,
        "row_count": int(len(df_cleaned)),
        "column_count": int(len(df_cleaned.columns))
    })

