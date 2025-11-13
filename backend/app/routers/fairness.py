"""
Fairness & Explainability Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd
import os
import json
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset, ModelRun, FairnessReport
from app.modules import ml_pipeline, fairness
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FairnessEvaluationRequest(BaseModel):
    model_run_id: int
    group_column: str


class CounterfactualRequest(BaseModel):
    model_run_id: int
    input_row: Dict[str, Any]
    target_value: Optional[Any] = None


@router.post("/evaluate")
async def evaluate_fairness_endpoint(
    request: FairnessEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate fairness for a model run"""
    model_run = db.query(ModelRun).filter(ModelRun.id == request.model_run_id).first()
    if not model_run:
        raise HTTPException(status_code=404, detail="Model run not found")
    
    dataset = model_run.dataset
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
    
    data_prep = ml_pipeline.prepare_data(df, model_run.target_column)
    
    # Train a quick model to get predictions
    if model_run.problem_type == "classification":
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    model.fit(data_prep["X_train"], data_prep["y_train"])
    predictions = model.predict(data_prep["X_test"])
    
    fairness_result = fairness.evaluate_fairness(
        df.iloc[data_prep["X_test"].index] if hasattr(data_prep["X_test"], "index") else df,
        model_run.target_column,
        request.group_column,
        predictions,
        model_run.problem_type
    )
    
    # Save fairness report
    fairness_report = FairnessReport(
        model_run_id=request.model_run_id,
        group_column=request.group_column,
        metrics=json.dumps(fairness_result, default=lambda o: float(o) if hasattr(o, 'item') else o),
        bias_detected=fairness_result.get("bias_detected", False)
    )
    db.add(fairness_report)
    db.commit()
    db.refresh(fairness_report)
    
    return jsonable_encoder({
        "fairness_report_id": fairness_report.id,
        "fairness_metrics": fairness_result
    })


@router.get("/feature-importance/{model_run_id}")
async def get_feature_importance(
    model_run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feature importance for a model run"""
    model_run = db.query(ModelRun).filter(ModelRun.id == model_run_id).first()
    if not model_run:
        raise HTTPException(status_code=404, detail="Model run not found")
    
    if model_run.feature_importance:
        importance = json.loads(model_run.feature_importance)
        return jsonable_encoder({
            "model_run_id": model_run_id,
            "feature_importance": importance
        })
    else:
        raise HTTPException(status_code=404, detail="Feature importance not available")


@router.post("/counterfactual")
async def generate_counterfactual_endpoint(
    request: CounterfactualRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate counterfactual explanation"""
    model_run = db.query(ModelRun).filter(ModelRun.id == request.model_run_id).first()
    if not model_run:
        raise HTTPException(status_code=404, detail="Model run not found")
    
    dataset = model_run.dataset
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Load dataset and retrain model (in production, load saved model)
    if dataset.file_path and os.path.exists(dataset.file_path):
        if dataset.file_path.endswith('.csv'):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
    else:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    data_prep = ml_pipeline.prepare_data(df, model_run.target_column)
    feature_names = data_prep["feature_names"]
    
    # Train model
    if model_run.problem_type == "classification":
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    model.fit(data_prep["X_train"], data_prep["y_train"])
    
    # Generate counterfactual
    counterfactual = fairness.generate_counterfactual(
        model, request.input_row, feature_names, request.target_value
    )
    
    return jsonable_encoder(counterfactual)

