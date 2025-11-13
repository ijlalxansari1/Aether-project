"""
Dashboard Module
Generates dashboard data and reports
"""
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime


def get_dashboard_data(dataset_id: str, dataset_info: Dict[str, Any],
                      profile: Dict[str, Any],
                      quality_score: float,
                      model_results: Optional[Dict[str, Any]] = None,
                      fairness_report: Optional[Dict[str, Any]] = None,
                      narrative: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate comprehensive dashboard data
    
    Args:
        dataset_id: Dataset identifier
        dataset_info: Dataset metadata
        profile: Data profile
        quality_score: Data quality score
        model_results: Optional model training results
        fairness_report: Optional fairness evaluation results
        narrative: Optional generated narrative
        
    Returns:
        Dictionary with all dashboard data
    """
    dashboard = {
        "dataset_id": dataset_id,
        "dataset_info": dataset_info,
        "data_quality": {
            "score": quality_score,
            "status": get_quality_status(quality_score),
            "color": get_quality_color(quality_score)
        },
        "summary": {
            "row_count": profile.get("summary", {}).get("row_count", 0),
            "column_count": profile.get("summary", {}).get("column_count", 0),
            "memory_usage_mb": profile.get("summary", {}).get("memory_usage_mb", 0)
        },
        "profile": profile,
        "narrative": narrative or "No narrative available",
        "model_results": model_results,
        "fairness_report": fairness_report,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # Add model performance indicators if available
    if model_results:
        dashboard["model_performance"] = get_model_performance_indicators(model_results)
    
    # Add fairness indicators if available
    if fairness_report:
        dashboard["fairness_indicators"] = get_fairness_indicators(fairness_report)
    
    return dashboard


def get_quality_status(score: float) -> str:
    """Get quality status text"""
    if score >= 80:
        return "Excellent"
    elif score >= 50:
        return "Good"
    else:
        return "Needs Improvement"


def get_quality_color(score: float) -> str:
    """Get color code for quality score"""
    if score >= 80:
        return "green"
    elif score >= 50:
        return "yellow"
    else:
        return "red"


def get_model_performance_indicators(model_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract model performance indicators"""
    indicators = {
        "best_model": model_results.get("best_model"),
        "problem_type": model_results.get("problem_type"),
        "models": {}
    }
    
    for model_name, model_data in model_results.get("models", {}).items():
        if "metrics" in model_data:
            metrics = model_data["metrics"]
            if model_results.get("problem_type") == "classification":
                indicators["models"][model_name] = {
                    "accuracy": metrics.get("accuracy", 0),
                    "f1_score": metrics.get("f1_score", 0),
                    "status": get_performance_status(metrics.get("accuracy", 0), "classification")
                }
            else:
                indicators["models"][model_name] = {
                    "rmse": metrics.get("rmse", 0),
                    "r2_score": metrics.get("r2_score", 0),
                    "status": get_performance_status(metrics.get("r2_score", 0), "regression")
                }
    
    return indicators


def get_performance_status(metric_value: float, problem_type: str) -> str:
    """Get performance status based on metric"""
    if problem_type == "classification":
        if metric_value >= 0.9:
            return "Excellent"
        elif metric_value >= 0.7:
            return "Good"
        elif metric_value >= 0.5:
            return "Fair"
        else:
            return "Poor"
    else:  # regression
        if metric_value >= 0.8:
            return "Excellent"
        elif metric_value >= 0.6:
            return "Good"
        elif metric_value >= 0.4:
            return "Fair"
        else:
            return "Poor"


def get_fairness_indicators(fairness_report: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fairness indicators"""
    return {
        "bias_detected": fairness_report.get("bias_detected", False),
        "bias_severity": fairness_report.get("bias_severity", "none"),
        "bias_description": fairness_report.get("bias_description", ""),
        "group_count": len(fairness_report.get("groups", {})),
        "status": "Fair" if not fairness_report.get("bias_detected", False) else "Bias Detected",
        "color": "green" if not fairness_report.get("bias_detected", False) else "red"
    }

