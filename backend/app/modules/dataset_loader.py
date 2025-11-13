"""
Dataset Loading Utility
Handles loading datasets from both local filesystem and cloud storage
"""
import pandas as pd
import os
from typing import Optional
from .storage import get_storage_adapter


async def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load dataset from file path (supports both local and cloud storage)
    
    Args:
        file_path: File path (local) or URL (cloud storage)
    
    Returns:
        pandas DataFrame
    """
    # Check if it's a URL (cloud storage)
    if file_path.startswith(('http://', 'https://')):
        storage = get_storage_adapter()
        content = await storage.download_file(file_path)
        return _read_from_bytes(content, file_path)
    
    # Local file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    return _read_from_path(file_path)


def _read_from_path(file_path: str) -> pd.DataFrame:
    """Read DataFrame from local file path"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    elif file_path.endswith('.parquet'):
        return pd.read_parquet(file_path)
    else:
        # Try CSV as default
        return pd.read_csv(file_path)


def _read_from_bytes(content: bytes, file_path: str) -> pd.DataFrame:
    """Read DataFrame from bytes content"""
    import io
    
    if file_path.endswith('.csv') or '.csv' in file_path:
        return pd.read_csv(io.BytesIO(content))
    elif file_path.endswith(('.xlsx', '.xls')) or any(ext in file_path for ext in ['.xlsx', '.xls']):
        return pd.read_excel(io.BytesIO(content))
    elif file_path.endswith('.json') or '.json' in file_path:
        return pd.read_json(io.BytesIO(content))
    elif file_path.endswith('.parquet') or '.parquet' in file_path:
        return pd.read_parquet(io.BytesIO(content))
    else:
        # Try CSV as default
        return pd.read_csv(io.BytesIO(content))


def is_cloud_storage(file_path: str) -> bool:
    """Check if file_path is a cloud storage URL"""
    return file_path.startswith(('http://', 'https://'))


def file_exists(file_path: str) -> bool:
    """Check if file exists (local or cloud)"""
    if is_cloud_storage(file_path):
        # For cloud storage, assume it exists if URL is provided
        # In production, you might want to do a HEAD request
        return True
    return os.path.exists(file_path)

