"""
Dashboard Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import os
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset, ModelRun, FairnessReport
from app.modules import dashboard, data_processing, narrative, ml_pipeline, fairness
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{dataset_id}")
async def get_dashboard(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Load dataset (supports both local and cloud storage)
    from app.modules.dataset_loader import load_dataset
    try:
        df = await load_dataset(dataset.file_path) if dataset.file_path else pd.DataFrame()
    except Exception:
        df = pd.DataFrame()
    
    # Get profile
    profile = data_processing.profile_data(df)
    quality_score = dataset.data_quality_score or data_processing.compute_data_quality_score(df)
    
    # Get narrative
    narrative_text = narrative.generate_narrative(df, profile)
    
    # Get latest model run
    model_run = db.query(ModelRun).filter(ModelRun.dataset_id == dataset_id).order_by(ModelRun.created_at.desc()).first()
    model_results = None
    fairness_report_data = None
    
    if model_run:
        # Get model results
        import json
        if model_run.metrics:
            metrics = json.loads(model_run.metrics)
            model_results = {
                "problem_type": model_run.problem_type,
                "best_model": model_run.model_name,
                "best_score": metrics,
                "target_column": model_run.target_column
            }
        
        # Get fairness report
        fairness_report = db.query(FairnessReport).filter(FairnessReport.model_run_id == model_run.id).first()
        if fairness_report:
            fairness_metrics = json.loads(fairness_report.metrics)
            fairness_report_data = fairness_metrics
    
    # Generate dashboard data
    dashboard_data = dashboard.get_dashboard_data(
        str(dataset_id),
        {
            "name": dataset.name,
            "filename": dataset.filename,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None
        },
        profile,
        quality_score,
        model_results,
        fairness_report_data,
        narrative_text
    )
    
    return jsonable_encoder(dashboard_data)

