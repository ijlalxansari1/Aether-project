"""
Ethical analysis helpers: detect sensitive attributes, imbalance, skewness, and notes.
Includes GDPR and ethical compliance checks.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import re

SENSITIVE_TOKENS = {
    "gender", "sex", "age", "race", "ethnic", "religion", "marital", "disab", "income", "nation", "minority"
}

# GDPR Article 4 - Personal Data Identifiers
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
}


def _tokens(name: str) -> List[str]:
    name = name.lower().replace('-', '_').replace('.', '_')
    return re.split(r"[^a-z0-9]+", name)


def detect_sensitive_attributes(df: pd.DataFrame) -> List[str]:
    found: List[str] = []
    for c in df.columns:
        toks = _tokens(str(c))
        if any(any(tok.startswith(s) for tok in toks) for s in SENSITIVE_TOKENS):
            found.append(str(c))
    return found


def distribution_imbalance(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    for col in columns:
        try:
            vc = df[col].astype(str).value_counts(dropna=False)
            total = int(vc.sum()) if vc.size else 0
            ratios = {str(k): float(v) / total if total else 0.0 for k, v in vc.head(10).to_dict().items()}
            max_ratio = max(ratios.values()) if ratios else 0.0
            report[str(col)] = {
                "top_values": {k: int(vc.to_dict().get(k, 0)) for k in ratios.keys()},
                "max_ratio": float(max_ratio),
                "flag": bool(max_ratio > 0.8)
            }
        except Exception:
            report[str(col)] = {"error": "unable_to_compute"}
    return report


def skew_warnings(df: pd.DataFrame) -> Dict[str, Any]:
    warnings: Dict[str, Any] = {}
    num = df.select_dtypes(include=[np.number])
    for col in num.columns:
        series = num[col].dropna()
        if len(series) == 0:
            continue
        skew = float(series.skew())
        kurt = float(series.kurtosis())
        if abs(skew) > 1 or kurt > 3:
            warnings[str(col)] = {"skew": skew, "kurtosis": kurt, "flag": True}
    return warnings


def ethical_notes(sensitive_cols: List[str], imbalance: Dict[str, Any], skew: Dict[str, Any]) -> List[str]:
    notes: List[str] = []
    if sensitive_cols:
        notes.append("Sensitive attributes detected: " + ", ".join(sensitive_cols))
    for col, info in imbalance.items():
        if isinstance(info, dict) and info.get("flag"):
            notes.append(f"Severe imbalance in '{col}' — consider stratified sampling or reweighting.")
    if skew:
        notes.append("Numeric skew/kurtosis flagged; consider transformations or robust models.")
    if not notes:
        notes.append("No immediate ethical risks detected in a quick scan. Review domain context.")
    return notes


def detect_pii(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Detect Personally Identifiable Information (PII) per GDPR Article 4
    """
    pii_found = {}
    for pattern_name, pattern in PII_PATTERNS.items():
        found_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().astype(str).head(1000)  # Sample for performance
                matches = sample.str.contains(pattern, regex=True, na=False)
                if matches.sum() > 0:
                    found_cols.append(col)
        if found_cols:
            pii_found[pattern_name] = found_cols
    return pii_found


def gdpr_compliance_check(df: pd.DataFrame, sensitive_cols: List[str], pii_data: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    GDPR Compliance Assessment (Articles 5, 6, 9, 25)
    """
    compliance_issues = []
    recommendations = []
    
    # Article 5 - Principles of processing
    if sensitive_cols:
        compliance_issues.append("Special category data detected (Article 9)")
        recommendations.append("Ensure explicit consent or legal basis for processing special category data")
    
    if pii_data:
        compliance_issues.append("PII detected in dataset")
        recommendations.append("Implement data minimization - only collect necessary PII")
        recommendations.append("Ensure data subject rights (access, rectification, erasure) are supported")
    
    # Article 25 - Data protection by design
    if len(df) > 10000:
        recommendations.append("Large dataset detected - ensure appropriate security measures (encryption, access controls)")
    
    # Article 6 - Lawfulness of processing
    if sensitive_cols or pii_data:
        recommendations.append("Document legal basis for processing (consent, contract, legal obligation, etc.)")
        recommendations.append("Implement privacy by design and default settings")
    
    compliance_score = 100
    if compliance_issues:
        compliance_score -= len(compliance_issues) * 15
    if len(recommendations) > 3:
        compliance_score -= 10
    
    return {
        "compliance_score": max(0, compliance_score),
        "issues": compliance_issues,
        "recommendations": recommendations,
        "gdpr_articles_applicable": ["Article 5", "Article 6", "Article 9", "Article 25"] if (sensitive_cols or pii_data) else ["Article 5"]
    }


def ethical_notes(sensitive_cols: List[str], imbalance: Dict[str, Any], skew: Dict[str, Any], 
                  pii_data: Optional[Dict[str, List[str]]] = None, gdpr_compliance: Optional[Dict[str, Any]] = None) -> List[str]:
    notes: List[str] = []
    
    # GDPR and PII warnings
    if pii_data:
        pii_types = ", ".join(pii_data.keys())
        notes.append(f"⚠️ GDPR ALERT: PII detected ({pii_types}). Ensure compliance with GDPR Articles 5, 6, and 25.")
    
    if sensitive_cols:
        notes.append(f"⚠️ Sensitive attributes detected: {', '.join(sensitive_cols)}")
        notes.append("⚠️ Special category data (GDPR Article 9) - requires explicit consent or legal basis")
    
    if gdpr_compliance and gdpr_compliance.get("compliance_score", 100) < 80:
        notes.append(f"⚠️ GDPR Compliance Score: {gdpr_compliance['compliance_score']}/100 - Review recommendations")
    
    # Distribution imbalance
    for col, info in imbalance.items():
        if isinstance(info, dict) and info.get("flag"):
            notes.append(f"⚠️ Severe imbalance in '{col}' — consider stratified sampling or reweighting to avoid bias.")
    
    # Statistical warnings
    if skew:
        notes.append("⚠️ Numeric skew/kurtosis flagged; consider transformations or robust models.")
    
    # Positive notes
    if not sensitive_cols and not pii_data and not imbalance:
        notes.append("✓ No immediate ethical risks detected in quick scan. Review domain context.")
    
    return notes


def run_ethical_scan(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive ethical scan with GDPR compliance
    """
    sens = detect_sensitive_attributes(df)
    pii_data = detect_pii(df)
    imb = distribution_imbalance(df, sens or [])
    skew = skew_warnings(df)
    gdpr_compliance = gdpr_compliance_check(df, sens, pii_data)
    
    return {
        "sensitive_attributes": sens,
        "pii_detected": pii_data,
        "imbalance": imb,
        "skew_warnings": skew,
        "gdpr_compliance": gdpr_compliance,
        "notes": ethical_notes(sens, imb, skew, pii_data, gdpr_compliance)
    }
