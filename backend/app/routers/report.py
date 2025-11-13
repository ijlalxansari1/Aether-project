"""
Report Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import pandas as pd
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from app.database import SessionLocal, Dataset, ModelRun, FairnessReport
from app.modules import data_processing, eda_utils, narrative, ethical, report as report_mod, ml_report
from app.routers.auth import get_current_user, User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _build_payload(dataset, df: pd.DataFrame, db: Session) -> dict:
    profile = data_processing.profile_data(df)
    eda_payload = {
        "summary_stats": eda_utils.compute_summary_stats(df),
        "missing_report": eda_utils.compute_missing_report(df),
        "insights": eda_utils.quick_insights(df)
    }
    try:
        visuals = narrative.generate_eda_visuals(df)
        eda_payload.update(visuals or {})
    except Exception:
        pass
    ethics = ethical.run_ethical_scan(df)
    story = narrative.generate_narrative(df, profile)
    story_struct = {"sections": [{"title": "Narrative", "body": story}]}
    model_run = db.query(ModelRun).filter(ModelRun.dataset_id == dataset.id).order_by(ModelRun.created_at.desc()).first()
    ml = None
    if model_run and model_run.metrics:
        import json
        ml = {"best_model": model_run.model_name, "best_score": json.loads(model_run.metrics)}
    return {
        "dataset": {"name": dataset.name, "row_count": dataset.row_count, "column_count": dataset.column_count, "preview": df.head(10).to_dict(orient='records')},
        "ethics": ethics,
        "eda": eda_payload,
        "story": story_struct,
        "ml": ml
    }


@router.get("/{dataset_id}")
async def generate_report(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not dataset.file_path or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    df = pd.read_csv(dataset.file_path) if dataset.file_path.endswith('.csv') else pd.read_excel(dataset.file_path)
    payload = _build_payload(dataset, df, db)
    html = report_mod.generate_html(payload)
    md = report_mod.generate_markdown(payload)
    return jsonable_encoder({"markdown": md, "html": html})


@router.get("/{dataset_id}/docx")
async def generate_report_docx(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not dataset.file_path or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    df = pd.read_csv(dataset.file_path) if dataset.file_path.endswith('.csv') else pd.read_excel(dataset.file_path)
    payload = _build_payload(dataset, df, db)
    content = report_mod.generate_docx(payload)
    return Response(content, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename=aether_report_{dataset_id}.docx"})


@router.get("/{dataset_id}/pdf")
async def generate_report_pdf(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not dataset.file_path or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    df = pd.read_csv(dataset.file_path) if dataset.file_path.endswith('.csv') else pd.read_excel(dataset.file_path)
    payload = _build_payload(dataset, df, db)
    content = report_mod.generate_pdf(payload)
    return Response(content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=aether_report_{dataset_id}.pdf"})


@router.get("/{dataset_id}/ml-report")
async def generate_ml_business_report(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate business-focused ML analysis report"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest model run
    model_run = db.query(ModelRun).filter(ModelRun.dataset_id == dataset_id).order_by(ModelRun.created_at.desc()).first()
    if not model_run:
        raise HTTPException(status_code=404, detail="No model run found for this dataset")
    
    import json
    model_results = {
        "problem_type": model_run.problem_type,
        "best_model": model_run.model_name,
        "best_score": json.loads(model_run.metrics) if model_run.metrics else {},
        "models": {}  # Could be expanded to include all models
    }
    
    feature_importance = None
    if model_run.feature_importance:
        feature_importance = {"feature_importance": json.loads(model_run.feature_importance)}
    
    dataset_info = {
        "name": dataset.name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count
    }
    
    content = ml_report.generate_ml_business_report(model_results, dataset_info, feature_importance)
    return Response(content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=ml_business_report_{dataset_id}.pdf"})
