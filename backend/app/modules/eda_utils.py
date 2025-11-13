"""
EDA utilities: summary stats, missing report, correlations, distribution metrics.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def compute_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number])
    desc = numeric.describe(percentiles=[0.25, 0.5, 0.75]).to_dict()
    # Convert numpy to native
    summary = {str(col): {k: (float(v) if pd.notna(v) else None) for k, v in stats.items()} for col, stats in desc.items()}
    return {
        "columns": list(numeric.columns),
        "stats": summary
    }


def compute_missing_report(df: pd.DataFrame) -> Dict[str, Any]:
    counts = df.isna().sum()
    perc = (counts / len(df) * 100) if len(df) else counts
    return {
        "per_column": {str(c): {"count": int(counts[c]), "percent": float(perc[c])} for c in df.columns},
        "total_missing": int(counts.sum()),
        "rows_with_any_missing": int(df.isna().any(axis=1).sum())
    }


def compute_correlations(df: pd.DataFrame) -> Dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return {"matrix": {}, "order": []}
    corr = numeric.corr().fillna(0.0)
    return {
        "matrix": {str(r): {str(c): float(corr.loc[r, c]) for c in corr.columns} for r in corr.index},
        "order": [str(c) for c in corr.columns]
    }


def distribution_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    numeric = df.select_dtypes(include=[np.number])
    for col in numeric.columns:
        series = numeric[col].dropna()
        if len(series) == 0:
            metrics[str(col)] = {"skew": None, "kurtosis": None}
        else:
            metrics[str(col)] = {
                "skew": float(series.skew()),
                "kurtosis": float(series.kurtosis())
            }
    return metrics


def value_counts_small(df: pd.DataFrame, max_unique: int = 20, top_k: int = 10) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for col in df.columns:
        if df[col].nunique(dropna=False) <= max_unique or df[col].dtype == 'object':
            vc = df[col].astype(str).value_counts(dropna=False).head(top_k)
            out[str(col)] = {str(k): int(v) for k, v in vc.to_dict().items()}
    return out


def quick_insights(df: pd.DataFrame) -> List[str]:
    insights: List[str] = []
    if df.empty:
        return ["Dataset is empty."]
    
    # Dataset overview
    insights.append(f"Dataset contains {len(df):,} rows and {len(df.columns)} columns.")
    
    # Missingness
    miss_pct = float(df.isna().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) and len(df.columns) else 0.0
    if miss_pct > 5:
        insights.append(f"⚠️ {miss_pct:.1f}% of cells are missing - data cleaning recommended.")
    elif miss_pct > 0:
        insights.append(f"✓ Minimal missing data ({miss_pct:.1f}%) detected.")
    else:
        insights.append("✓ No missing values detected - excellent data completeness.")
    
    # Duplicates
    dups = int(df.duplicated().sum())
    if dups > 0:
        dup_pct = (dups / len(df)) * 100
        insights.append(f"⚠️ {dups} duplicate rows ({dup_pct:.1f}%) found - consider removing.")
    else:
        insights.append("✓ No duplicate rows detected.")
    
    # Numeric columns analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        insights.append(f"✓ {len(numeric_cols)} numeric column(s) available for statistical analysis.")
        # Check for high correlation
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr().abs()
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if corr_matrix.iloc[i, j] > 0.9:
                        high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
            if high_corr_pairs:
                insights.append(f"⚠️ High correlation (>0.9) detected between {len(high_corr_pairs)} pair(s) - potential multicollinearity.")
    
    # Categorical columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    if len(categorical_cols) > 0:
        insights.append(f"✓ {len(categorical_cols)} categorical column(s) identified.")
        # Check for imbalanced categories
        for col in categorical_cols[:5]:  # Check first 5
            vc = df[col].astype(str).value_counts()
            if not vc.empty and len(vc) > 0:
                max_ratio = vc.iloc[0] / max(1, len(df))
                if max_ratio > 0.9:
                    insights.append(f"⚠️ Column '{col}' is highly imbalanced ({max_ratio:.0%} in one category).")
    
    # Outliers check
    if len(numeric_cols) > 0:
        outlier_count = 0
        for col in numeric_cols[:5]:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()
                outlier_count += outliers
        if outlier_count > len(df) * 0.1:
            insights.append(f"⚠️ Significant outliers detected - review data quality.")
        elif outlier_count > 0:
            insights.append(f"✓ Some outliers present - normal for most datasets.")
    
    if len(insights) <= 2:
        insights.append("✓ No obvious issues detected; proceed to modeling or deeper analysis.")
    
    return insights
