"""
Data Ingestion Module
Handles CSV/Excel/JSON/Parquet uploads and API connections
Supports both local and cloud storage
"""
import pandas as pd
import requests
from typing import Optional, Dict, Any, List
from fastapi import UploadFile
import aiofiles
import os
import io
from datetime import datetime
from .storage import get_storage_adapter

SUPPORTED_EXT = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}


async def upload_dataset(file: UploadFile, upload_dir: str = "./uploads") -> Dict[str, Any]:
    """
    Upload and process a dataset file (CSV, Excel, JSON, Parquet)
    Uses storage adapter to support both local and cloud storage
    """
    storage = get_storage_adapter()
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Upload file using storage adapter
    upload_result = await storage.upload_file(file, file.filename)
    file_path = upload_result["file_path"]
    storage_type = upload_result.get("storage_type", "local")
    
    try:
        # Read file content for processing
        if storage_type == "local":
            # Local file - read directly
            df = _read_any(file_path, file_extension)
        else:
            # Cloud storage - download and process in memory
            content = await storage.download_file(file_path)
            df = _read_any_from_bytes(content, file_extension)
        
        df = auto_detect_types(df)
        
        return {
            "filename": file.filename,
            "file_path": file_path,  # This will be URL for cloud storage, path for local
            "storage_type": storage_type,
            "dataframe": df,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "preview": get_preview(df)
        }
    except Exception as e:
        # Clean up uploaded file on error
        try:
            await storage.delete_file(file_path)
        except:
            pass
        raise ValueError(f"Error processing file: {str(e)}")


def _read_any_from_bytes(content: bytes, ext: str) -> pd.DataFrame:
    """Read DataFrame from bytes content"""
    if ext == '.csv':
        return pd.read_csv(io.BytesIO(content))
    if ext in {'.xlsx', '.xls'}:
        return pd.read_excel(io.BytesIO(content))
    if ext == '.json':
        return pd.read_json(io.BytesIO(content), lines=False)
    if ext == '.parquet':
        return pd.read_parquet(io.BytesIO(content))
    raise ValueError(f"Unsupported file type: {ext}")


def _read_any(path: str, ext: str) -> pd.DataFrame:
    if ext == '.csv':
        return pd.read_csv(path)
    if ext in {'.xlsx', '.xls'}:
        return pd.read_excel(path)
    if ext == '.json':
        return pd.read_json(path, lines=False)
    if ext == '.parquet':
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file type: {ext}")


async def fetch_api_data(api_url: str, auth_token: Optional[str] = None, 
                        headers: Optional[Dict[str, str]] = None,
                        params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from a REST API endpoint. Tries JSON first, then CSV text.
    """
    try:
        request_headers = headers or {}
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        response = requests.get(api_url, headers=request_headers, params=params or {}, timeout=30)
        response.raise_for_status()
        
        try:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                for key in ("data", "results", "items"):
                    if key in data and isinstance(data[key], list):
                        df = pd.DataFrame(data[key])
                        break
                else:
                    df = pd.json_normalize(data)
            else:
                raise ValueError("Unsupported API response format")
        except ValueError:
            df = pd.read_csv(pd.io.common.StringIO(response.text))
        
        df = auto_detect_types(df)
        
        return {
            "filename": f"api_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "file_path": None,
            "api_url": api_url,
            "dataframe": df,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "preview": get_preview(df)
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching data from API: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing API response: {str(e)}")


def get_preview(df: pd.DataFrame, rows: int = 50) -> Dict[str, Any]:
    prev = df.head(rows)
    return {
        "rows": min(len(df), rows),
        "columns": list(prev.columns),
        "data": [[_safe_cell(prev.iloc[i, j]) for j in range(len(prev.columns))] for i in range(len(prev))]
    }


def _safe_cell(val: Any) -> Any:
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    if isinstance(val, (pd.Timestamp,)):
        return val.isoformat()
    return val if isinstance(val, (int, float, str, bool)) else str(val)


def suggest_schema(df: pd.DataFrame) -> List[Dict[str, str]]:
    return [{"column": str(c), "dtype": str(df[c].dtype)} for c in df.columns]


def apply_schema(df: pd.DataFrame, schema: List[Dict[str, str]]) -> pd.DataFrame:
    cast_map = {}
    for item in schema:
        col = item.get("column")
        dtype = item.get("dtype")
        if col in df.columns and dtype:
            try:
                if dtype in ("int", "int64"):
                    cast_map[col] = 'Int64'
                elif dtype in ("float", "float64"):
                    cast_map[col] = 'float64'
                elif dtype in ("bool", "boolean"):
                    cast_map[col] = 'boolean'
                elif dtype in ("datetime", "datetime64[ns]"):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                else:
                    df[col] = df[col].astype('string')
            except Exception:
                pass
    if cast_map:
        df = df.astype(cast_map)
    return df


def auto_detect_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                pd.to_numeric(df[col], errors='raise')
                df[col] = pd.to_numeric(df[col], errors='coerce')
                continue
            except (ValueError, TypeError):
                pass
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except (ValueError, TypeError):
                df[col] = df[col].astype('string')
    return df

