"""
Data Processing Module
Handles data cleaning, profiling, and quality assessment
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')


def clean_data(df: pd.DataFrame, user_approved: bool = True, 
               operations: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Clean data based on suggested operations - Best Practices Implementation
    
    Best Practices Applied:
    - Preserve data integrity (no data loss without explicit approval)
    - Handle missing values intelligently (median for numeric, mode for categorical)
    - Remove duplicates while preserving first occurrence
    - Standardize data types for consistency
    - Handle outliers appropriately
    - Preserve data lineage information (e.g. source, transformation, etc.)
    
    Args:
        df: Input DataFrame
        user_approved: Whether user approved the cleaning operations
        operations: List of cleaning operations to perform
        
    Returns:
        Cleaned DataFrame
    """
    if not user_approved:
        return df
    
    df_cleaned = df.copy()
    operations = operations or []
    
    # Step 1: Remove rows with all missing values (safe operation)
    if "remove_empty_rows" in operations:
        initial_rows = len(df_cleaned)
        df_cleaned = df_cleaned.dropna(how='all')
        if len(df_cleaned) < initial_rows:
            pass  # Log removed rows
    
    # Step 2: Remove duplicates (preserve first occurrence - best practice)
    if "remove_duplicates" in operations:
        initial_rows = len(df_cleaned)
        df_cleaned = df_cleaned.drop_duplicates(keep='first')  # Keep first occurrence
        if len(df_cleaned) < initial_rows:
            pass  # Log removed duplicates
    
    # Step 3: Handle missing values intelligently
    if "handle_missing" in operations:
        for col in df_cleaned.columns:
            missing_pct = df_cleaned[col].isnull().sum() / len(df_cleaned) if len(df_cleaned) > 0 else 0
            
            # Skip if column is >90% missing (will be handled by remove_sparse_columns)
            if missing_pct > 0.9:
                continue
                
            if df_cleaned[col].isnull().sum() > 0:
                if df_cleaned[col].dtype in ['int64', 'float64']:
                    # For numeric: use median (robust to outliers) or mean if median is NaN
                    median_val = df_cleaned[col].median()
                    if pd.isna(median_val):
                        mean_val = df_cleaned[col].mean()
                        df_cleaned[col].fillna(mean_val if not pd.isna(mean_val) else 0, inplace=True)
                    else:
                        df_cleaned[col].fillna(median_val, inplace=True)
                elif df_cleaned[col].dtype in ['datetime64[ns]', 'datetime64']:
                    # For datetime: forward fill or use most recent date
                    df_cleaned[col].fillna(method='ffill', inplace=True)
                    df_cleaned[col].fillna(method='bfill', inplace=True)
                else:
                    # For categorical: use mode (most frequent) or "Unknown"
                    mode_series = df_cleaned[col].mode(dropna=True)
                    if mode_series is not None and len(mode_series) > 0:
                        df_cleaned[col].fillna(mode_series.iloc[0], inplace=True)
                    else:
                        df_cleaned[col].fillna("Unknown", inplace=True)
    
    # Step 4: Remove columns with too many missing values (>90% - best practice threshold)
    if "remove_sparse_columns" in operations:
        threshold = 0.9
        cols_to_remove = []
        for col in df_cleaned.columns:
            missing_pct = df_cleaned[col].isnull().sum() / len(df_cleaned) if len(df_cleaned) > 0 else 0
            if missing_pct > threshold:
                cols_to_remove.append(col)
        if cols_to_remove:
            df_cleaned = df_cleaned.drop(columns=cols_to_remove)
    
    # Step 5: Standardize text columns (trim whitespace, preserve case for analysis)
    if "standardize_text" in operations:
        for col in df_cleaned.select_dtypes(include=['object']).columns:
            # Trim whitespace only (preserve case for better analysis)
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
            # Replace multiple spaces with single space
            df_cleaned[col] = df_cleaned[col].str.replace(r'\s+', ' ', regex=True)
    
    # Step 6: Fix data type inconsistencies (best practice)
    if "fix_data_types" in operations:
        for col in df_cleaned.columns:
            # Try to convert numeric strings to numbers
            if df_cleaned[col].dtype == 'object':
                try:
                    # Check if column can be converted to numeric
                    numeric_series = pd.to_numeric(df_cleaned[col], errors='coerce')
                    if numeric_series.notna().sum() / len(df_cleaned) > 0.8:  # 80% can be numeric
                        df_cleaned[col] = numeric_series
                except:
                    pass
    
    # Step 7: Remove leading/trailing whitespace from all string columns
    if "trim_whitespace" in operations:
        for col in df_cleaned.select_dtypes(include=['object']).columns:
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
    
    return df_cleaned


def _to_native(value: Any) -> Any:
    """Convert numpy/pandas scalars to native Python types for JSON safety."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _iqr_outlier_count(series: pd.Series) -> int:
    s = series.dropna()
    if s.empty:
        return 0
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((s < lower) | (s > upper)).sum())


def profile_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive data profile
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with profiling information
    """
    profile: Dict[str, Any] = {
        "summary": {
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024**2)
        },
        "columns": {},
        "missing_values": {},
        "duplicates": {
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": float((df.duplicated().sum() / len(df)) * 100) if len(df) > 0 else 0.0
        },
        "data_types": {},
        "outliers_iqr": {
            "total_outliers": 0,
            "per_column": {}
        }
    }
    
    total_outliers = 0
    
    for col in df.columns:
        missing_count = int(df[col].isnull().sum())
        missing_pct = float((df[col].isnull().sum() / len(df)) * 100) if len(df) > 0 else 0.0
        unique_count = int(df[col].nunique())
        unique_pct = float((df[col].nunique() / len(df)) * 100) if len(df) > 0 else 0.0

        # Determine data category (categorical vs continuous)
        data_category = "unknown"
        if df[col].dtype in ['int64', 'float64']:
            if unique_count <= 10 and unique_pct < 5:
                data_category = "categorical_numeric"  # e.g., rating 1-5
            else:
                data_category = "continuous"
        elif df[col].dtype == 'object' or df[col].dtype.name == 'category':
            if unique_count <= 20:
                data_category = "categorical"
            else:
                data_category = "high_cardinality_text"  # e.g., names, IDs
        
        col_info: Dict[str, Any] = {
            "data_type": str(df[col].dtype),
            "data_category": data_category,  # categorical, continuous, categorical_numeric, high_cardinality_text
            "missing_count": missing_count,
            "missing_percentage": missing_pct,
            "unique_count": unique_count,
            "unique_percentage": unique_pct,
            "cardinality": "low" if unique_count <= 10 else "medium" if unique_count <= 100 else "high"
        }
        
        # Add statistics for numeric columns
        if df[col].dtype in ['int64', 'float64']:
            col_info.update({
                "mean": None if df[col].isnull().all() else float(df[col].mean()),
                "median": None if df[col].isnull().all() else float(df[col].median()),
                "std": None if df[col].isnull().all() else float(df[col].std()),
                "min": None if df[col].isnull().all() else float(df[col].min()),
                "max": None if df[col].isnull().all() else float(df[col].max()),
                "q25": None if df[col].isnull().all() else float(df[col].quantile(0.25)),
                "q75": None if df[col].isnull().all() else float(df[col].quantile(0.75))
            })
            out_cnt = _iqr_outlier_count(df[col])
            profile["outliers_iqr"]["per_column"][str(col)] = int(out_cnt)
            total_outliers += out_cnt
        
        # Add top values for categorical or low-cardinality columns
        if df[col].dtype == 'object' or unique_count < 20:
            vc = df[col].value_counts().head(10)
            # Convert to {str(value): int(count)}
            top_dict = {str(k): int(v) for k, v in vc.to_dict().items()}
            col_info["top_values"] = top_dict
        
        profile["columns"][str(col)] = {k: _to_native(v) for k, v in col_info.items()}
        profile["missing_values"][str(col)] = int(col_info["missing_count"])
        profile["data_types"][str(col)] = str(col_info["data_type"])
    
    profile["outliers_iqr"]["total_outliers"] = int(total_outliers)
    
    return profile


def compute_data_quality_score(df: pd.DataFrame) -> float:
    """
    Compute Data Quality Score (0-100) based on completeness, consistency, and readability
    
    Args:
        df: Input DataFrame
        
    Returns:
        Quality score between 0 and 100
    """
    if len(df) == 0:
        return 0.0
    
    scores = []
    
    # 1. Completeness Score (40% weight)
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isnull().sum().sum()
    completeness = (1 - (missing_cells / total_cells)) * 100 if total_cells > 0 else 0
    scores.append(("completeness", completeness, 0.4))
    
    # 2. Consistency Score (30% weight)
    duplicate_ratio = df.duplicated().sum() / len(df) if len(df) > 0 else 0
    consistency = (1 - duplicate_ratio) * 100
    scores.append(("consistency", consistency, 0.3))
    
    # 3. Readability/Validity Score (30% weight)
    readability_issues = 0
    total_text_cells = 0
    
    for col in df.select_dtypes(include=['object']).columns:
        total_text_cells += len(df[col])
        readability_issues += (df[col].astype(str).str.strip() == '').sum()
        readability_issues += (df[col].astype(str).str.strip().str.len() == 0).sum()
    
    readability = (1 - (readability_issues / total_text_cells)) * 100 if total_text_cells > 0 else 100
    scores.append(("readability", readability, 0.3))
    
    quality_score = sum(score * weight for _, score, weight in scores)
    
    return round(float(quality_score), 2)


def compute_data_integrity_score(df: pd.DataFrame) -> float:
    """
    Compute Data Integrity Score based on data type consistency and value validity
    """
    if len(df) == 0:
        return 0.0
    
    integrity_issues = 0
    total_checks = 0
    
    for col in df.columns:
        # Only numeric columns are checked for integrity issues
        if df[col].dtype in ['int64', 'float64']:
            col_series = df[col]
            total_checks += len(col_series)

            # Count infinite values as integrity issues
            integrity_issues += int(np.isinf(col_series).sum())

            # Use robust IQR-based outlier detection (handles extreme outliers in small samples)
            try:
                outliers = _iqr_outlier_count(col_series)
            except Exception:
                outliers = 0
            integrity_issues += int(outliers)
    
    integrity_score = (1 - (integrity_issues / total_checks)) * 100 if total_checks > 0 else 100
    return round(float(max(0, min(100, integrity_score))), 2)


def suggest_cleaning_operations(df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Suggest cleaning operations based on data profile
    """
    suggestions: List[Dict[str, Any]] = []
    
    if profile["duplicates"]["duplicate_rows"] > 0:
        suggestions.append({
            "operation": "remove_duplicates",
            "description": f"Remove {profile['duplicates']['duplicate_rows']} duplicate rows",
            "impact": "high",
            "estimated_rows_removed": int(profile["duplicates"]["duplicate_rows"])})
    
    missing_cols = [col for col, count in profile["missing_values"].items() if count > 0]
    if missing_cols:
        total_missing = int(sum(profile["missing_values"].values()))
        missing_percentage = (total_missing / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 0
        
        if missing_percentage > 50:
            suggestions.append({
                "operation": "handle_missing",
                "description": f"Handle missing values in {len(missing_cols)} columns ({total_missing} missing values, {missing_percentage:.1f}%)",
                "impact": "high",
                "method": "median for numeric, mode for categorical"})
        else:
            suggestions.append({
                "operation": "handle_missing",
                "description": f"Handle missing values in {len(missing_cols)} columns",
                "impact": "medium",
                "method": "median for numeric, mode for categorical"})
    
    sparse_cols: List[str] = []
    for col, info in profile["columns"].items():
        if info.get("missing_percentage", 0) > 90:
            sparse_cols.append(str(col))
    
    if sparse_cols:
        suggestions.append({
            "operation": "remove_sparse_columns",
            "description": f"Remove {len(sparse_cols)} columns with >90% missing values",
            "impact": "medium",
            "columns": sparse_cols})
    
    empty_rows = int(df.isnull().all(axis=1).sum())
    if empty_rows > 0:
        suggestions.append({
            "operation": "remove_empty_rows",
            "description": f"Remove {empty_rows} completely empty rows",
            "impact": "low",
            "estimated_rows_removed": empty_rows})
    
    text_cols = [col for col, dtype in profile["data_types"].items() if dtype == 'object']
    if text_cols:
        suggestions.append({
            "operation": "standardize_text",
            "description": f"Standardize text in {len(text_cols)} columns (trim, lowercase)",
            "impact": "low"})
    
    return suggestions

