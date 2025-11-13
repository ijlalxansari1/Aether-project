"""
Data Ingestion Router
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal, Dataset, User, AuditLog
from app.modules import ingestion
from app.routers.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class APIConnectionRequest(BaseModel):
    api_url: str
    auth_token: Optional[str] = None
    headers: Optional[dict] = None


class SchemaItem(BaseModel):
    column: str
    dtype: str


class ApplySchemaRequest(BaseModel):
    dataset_id: int
    # avoid shadowing BaseModel.schema by using an internal name and aliasing
    schema_items: List[SchemaItem] = Field(..., alias="schema")

    class Config:
        # allow accessing the field by attribute name (schema_items) if needed
        allow_population_by_field_name = True


@router.post("/upload")
async def upload_dataset_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV or Excel file"""
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.xls', '.json', '.parquet')):
            raise HTTPException(status_code=400, detail="Supported: CSV, Excel, JSON, Parquet")
        
        upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        result = await ingestion.upload_dataset(file, upload_dir)
        
        db_dataset = Dataset(
            name=file.filename,
            filename=file.filename,
            file_path=result["file_path"],
            source_type="upload",
            row_count=int(result["row_count"]),
            column_count=int(result["column_count"]),
            owner_id=current_user.id
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        audit = AuditLog(
            user_id=current_user.id,
            action="upload",
            resource_type="dataset",
            resource_id=db_dataset.id,
            details=f"Uploaded {file.filename}"
        )
        db.add(audit)
        db.commit()
        
        return jsonable_encoder({
            "dataset_id": db_dataset.id,
            "filename": result["filename"],
            "row_count": result["row_count"],
            "column_count": result["column_count"],
            "columns": [str(c) for c in result["columns"]],
            "data_types": {str(k): str(v) for k, v in result["data_types"].items()},
            "preview": result.get("preview")
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api-connection")
async def connect_api_endpoint(
    request: APIConnectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect to a REST API and fetch data"""
    try:
        result = await ingestion.fetch_api_data(
            request.api_url,
            request.auth_token,
            request.headers
        )
        
        db_dataset = Dataset(
            name=result["filename"],
            filename=result["filename"],
            file_path=None,
            source_type="api",
            api_url=request.api_url,
            row_count=int(result["row_count"]),
            column_count=int(result["column_count"]),
            owner_id=current_user.id
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        audit = AuditLog(
            user_id=current_user.id,
            action="api_connection",
            resource_type="dataset",
            resource_id=db_dataset.id,
            details=f"Connected to API: {request.api_url}"
        )
        db.add(audit)
        db.commit()
        
        return jsonable_encoder({
            "dataset_id": db_dataset.id,
            "filename": result["filename"],
            "row_count": result["row_count"],
            "column_count": result["column_count"],
            "columns": [str(c) for c in result["columns"]],
            "data_types": {str(k): str(v) for k, v in result["data_types"].items()},
            "preview": result.get("preview")
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-schema")
async def apply_schema_endpoint(
    request: ApplySchemaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not dataset.file_path or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")

    import pandas as pd
    if dataset.file_path.endswith('.csv'):
        df = pd.read_csv(dataset.file_path)
    elif dataset.file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(dataset.file_path)
    elif dataset.file_path.endswith('.json'):
        df = pd.read_json(dataset.file_path)
    elif dataset.file_path.endswith('.parquet'):
        df = pd.read_parquet(dataset.file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    schema_list: List[Dict[str, str]] = [{"column": s.column, "dtype": s.dtype} for s in request.schema_items]
    df2 = ingestion.apply_schema(df, schema_list)

    # Save over original path
    if dataset.file_path.endswith('.csv'):
        df2.to_csv(dataset.file_path, index=False)
    elif dataset.file_path.endswith(('.xlsx', '.xls')):
        df2.to_excel(dataset.file_path, index=False)
    elif dataset.file_path.endswith('.json'):
        df2.to_json(dataset.file_path, orient='records')
    elif dataset.file_path.endswith('.parquet'):
        df2.to_parquet(dataset.file_path, index=False)

    dataset.row_count = int(len(df2))
    dataset.column_count = int(len(df2.columns))
    db.commit()

    preview = ingestion.get_preview(df2)
    return jsonable_encoder({
        "dataset_id": dataset.id,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns": list(df2.columns),
        "data_types": {c: str(df2[c].dtype) for c in df2.columns},
        "preview": preview
    })

