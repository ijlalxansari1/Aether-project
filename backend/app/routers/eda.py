"""
EDA Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset
from app.modules import narrative, data_processing
from app.modules import eda_utils
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EDARequest(BaseModel):
    dataset_id: int
    target_column: Optional[str] = None
    auto_clean: bool = False  # Option to auto-apply safe cleaning operations


@router.post("/generate")
async def generate_eda(
    request: EDARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate EDA visualizations and narrative.
    Optionally applies data cleaning before analysis (integrated cleaning step).
    """
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
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
    
    # Step 1: Generate initial profile to identify issues
    profile = data_processing.profile_data(df)
    initial_row_count = len(df)
    initial_col_count = len(df.columns)
    
    # Step 2: Apply data cleaning if requested (integrated into EDA step per workflow spec)
    cleaning_applied = False
    cleaning_summary = {}
    if request.auto_clean:
        # Get cleaning suggestions
        suggestions = data_processing.suggest_cleaning_operations(df, profile)
        if suggestions:
            # Auto-apply high-impact, safe operations (duplicates, empty rows)
            safe_operations = []
            for suggestion in suggestions:
                op = suggestion.get("operation")
                impact = suggestion.get("impact", "low")
                # Auto-apply safe operations: remove duplicates, remove empty rows
                if impact in ["high", "medium"] and op in ["remove_duplicates", "remove_empty_rows"]:
                    safe_operations.append(op)
            
            if safe_operations:
                df = data_processing.clean_data(df, user_approved=True, operations=safe_operations)
                cleaning_applied = True
                cleaning_summary = {
                    "operations_applied": safe_operations,
                    "rows_before": initial_row_count,
                    "rows_after": len(df),
                    "columns_before": initial_col_count,
                    "columns_after": len(df.columns)
                }
                # Re-profile after cleaning
                profile = data_processing.profile_data(df)
    
    # Step 3: Extended EDA on (potentially cleaned) data
    summary = eda_utils.compute_summary_stats(df)
    missing = eda_utils.compute_missing_report(df)
    correlations = eda_utils.compute_correlations(df)
    dist_metrics = eda_utils.distribution_metrics(df)
    value_counts = eda_utils.value_counts_small(df)
    insights = eda_utils.quick_insights(df)
    
    # Step 4: Generate visualizations
    visuals = narrative.generate_eda_visuals(df, request.target_column)
    
    # Step 5: Generate narrative
    narrative_text = narrative.generate_narrative(df, profile, request.target_column)
    
    # Step 6: Detect anomalies
    anomalies = narrative.detect_anomalies(df, profile)
    
    return jsonable_encoder({
        "dataset_id": request.dataset_id,
        "summary_stats": summary,
        "missing_report": missing,
        "correlations": correlations,
        "distribution_metrics": dist_metrics,
        "value_counts": value_counts,
        "visualizations": visuals,
        "narrative": narrative_text,
        "insights": insights,
        "anomalies": anomalies,
        "profile": profile,
        "cleaning_applied": cleaning_applied,
        "cleaning_summary": cleaning_summary
    })

