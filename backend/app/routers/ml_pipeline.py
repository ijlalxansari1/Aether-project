"""
ML Pipeline Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
import json
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset, ModelRun
from app.modules import ml_pipeline, fairness, data_processing
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ModelRecommendationRequest(BaseModel):
    dataset_id: int
    target_column: str


class ModelTrainingRequest(BaseModel):
    dataset_id: int
    target_column: str
    selected_models: List[str]


@router.post("/recommend")
async def recommend_models_endpoint(
    request: ModelRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get model recommendations"""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Load dataset
    if dataset.file_path and os.path.exists(dataset.file_path):
        if dataset.file_path.endswith('.csv'):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
    else:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    # Detect problem type
    problem_type = ml_pipeline.detect_problem_type(df, request.target_column)
    
    # Get recommendations
    recommendations = ml_pipeline.recommend_models(df, request.target_column, problem_type)
    
    return jsonable_encoder({
        "dataset_id": request.dataset_id,
        "target_column": request.target_column,
        "problem_type": problem_type,
        "recommendations": recommendations
    })


@router.post("/train")
async def train_models_endpoint(
    request: ModelTrainingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train selected models"""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Load dataset
    if dataset.file_path and os.path.exists(dataset.file_path):
        if dataset.file_path.endswith('.csv'):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
    else:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    # Train models
    results = ml_pipeline.train_selected_models(
        df, request.target_column, request.selected_models
    )
    
    # Prepare data for feature importance
    data_prep = ml_pipeline.prepare_data(df, request.target_column)
    feature_names = data_prep["feature_names"]
    X_test = data_prep["X_test"]
    
    # Compute feature importance for best model
    feature_importance_data = {}
    if results["best_model"]:
        best_model_data = results["models"][results["best_model"]]
        if "model" in best_model_data:
            model = best_model_data["model"]
            importance = fairness.compute_feature_importance(
                model, df, feature_names, X_test
            )
            feature_importance_data = importance
    
    # Save model run to database
    model_run = ModelRun(
        dataset_id=request.dataset_id,
        user_id=current_user.id,
        model_name=results["best_model"] or ",".join(request.selected_models),
        problem_type=results["problem_type"],
        target_column=request.target_column,
        metrics=json.dumps(results.get("best_score", {}), default=lambda o: float(o) if hasattr(o, 'item') else o),
        feature_importance=json.dumps(feature_importance_data.get("feature_importance", {}), default=lambda o: float(o) if hasattr(o, 'item') else o),
        status="completed"
    )
    db.add(model_run)
    db.commit()
    db.refresh(model_run)
    
    # Prepare response (remove model objects, keep only metrics)
    response_results = {
        "problem_type": results["problem_type"],
        "models": {},
        "best_model": results["best_model"],
        "best_score": results["best_score"],
        "feature_importance": feature_importance_data
    }
    
    for model_name, model_data in results["models"].items():
        response_results["models"][model_name] = {
            "metrics": model_data.get("metrics", {}),
            "status": "completed" if "metrics" in model_data else "failed"
        }
    
    return jsonable_encoder({
        "model_run_id": model_run.id,
        "results": response_results
    })

