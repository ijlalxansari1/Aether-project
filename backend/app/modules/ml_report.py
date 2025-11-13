"""
Business-Focused ML Model Analysis Report Generator
Focuses on business value, not just technical accuracy metrics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import io
import json


def generate_ml_business_report(model_results: Dict[str, Any], dataset_info: Dict[str, Any], 
                                feature_importance: Optional[Dict[str, Any]] = None) -> bytes:
    """
    Generate business-focused ML analysis report
    Focuses on actionable insights, business impact, and recommendations
    """
    width, height = A4
    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    
    # Color scheme
    primary_color = HexColor('#2563eb')
    success_color = HexColor('#10b981')
    warning_color = HexColor('#f59e0b')
    text_color = HexColor('#0f172a')
    light_gray = HexColor('#f8fafc')
    
    y = height - 40
    
    def draw_header(title: str, subtitle: str = ""):
        nonlocal y
        if y < height - 200:
            c.showPage()
            y = height - 40
        
        c.setFillColor(primary_color)
        c.rect(0, y - 30, width, 50, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, y, title)
        if subtitle:
            c.setFont("Helvetica", 10)
            c.drawString(50, y - 18, subtitle)
        y -= 60
    
    def write_section(title: str, color=primary_color):
        nonlocal y
        if y < 150:
            c.showPage()
            y = height - 40
        c.setFillColor(color)
        c.rect(40, y - 20, width - 80, 25, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y - 15, title)
        y -= 35
    
    def write_text(text: str, size=10, bold=False, indent=0):
        nonlocal y
        if y < 80:
            c.showPage()
            y = height - 40
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        words = text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica-Bold" if bold else "Helvetica", size) > width - 100 - indent:
                if line:
                    c.drawString(50 + indent, y, line)
                    y -= size + 4
                line = word + " "
            else:
                line = test_line
        if line:
            c.drawString(50 + indent, y, line)
            y -= size + 4
    
    # Cover page
    draw_header("ML Model Business Analysis", "Actionable Insights & Recommendations")
    y -= 20
    write_text(f"Dataset: {dataset_info.get('name', 'N/A')}", size=14, bold=True)
    write_text(f"Problem Type: {model_results.get('problem_type', 'N/A').title()}", size=12)
    write_text(f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}", size=10)
    
    # Executive Summary
    c.showPage()
    y = height - 40
    write_section("Executive Summary", primary_color)
    
    best_model = model_results.get("best_model", "N/A")
    problem_type = model_results.get("problem_type", "unknown")
    best_score = model_results.get("best_score", {})
    
    write_text("Model Performance Overview:", bold=True)
    write_text(f"Best Performing Model: {best_model}", indent=20)
    
    if problem_type == "classification":
        accuracy = best_score.get("accuracy", 0)
        f1 = best_score.get("f1_score", 0)
        write_text(f"Accuracy: {accuracy*100:.1f}%", indent=20)
        write_text(f"F1 Score: {f1:.3f}", indent=20)
        
        # Business interpretation
        if accuracy >= 0.9:
            write_text("✓ Excellent model performance - Ready for production deployment", indent=20)
        elif accuracy >= 0.75:
            write_text("✓ Good model performance - Suitable for deployment with monitoring", indent=20)
        else:
            write_text("⚠ Model performance needs improvement - Consider feature engineering or more data", indent=20)
    else:
        r2 = best_score.get("r2_score", 0)
        rmse = best_score.get("rmse", 0)
        write_text(f"R² Score: {r2:.3f}", indent=20)
        write_text(f"RMSE: {rmse:.2f}", indent=20)
        
        if r2 >= 0.8:
            write_text("✓ Strong predictive power - Model explains most variance", indent=20)
        elif r2 >= 0.6:
            write_text("✓ Moderate predictive power - Model captures significant patterns", indent=20)
        else:
            write_text("⚠ Limited predictive power - Consider additional features or data", indent=20)
    
    # Business Value Analysis
    write_section("Business Value & Impact", success_color)
    
    write_text("Key Business Insights:", bold=True)
    
    # Model comparison
    models = model_results.get("models", {})
    if len(models) > 1:
        write_text("Model Comparison:", bold=True)
        for model_name, model_data in models.items():
            metrics = model_data.get("metrics", {})
            if problem_type == "classification":
                acc = metrics.get("accuracy", 0)
                write_text(f"  • {model_name}: {acc*100:.1f}% accuracy", indent=20)
            else:
                r2 = metrics.get("r2_score", 0)
                write_text(f"  • {model_name}: R² = {r2:.3f}", indent=20)
    
    # Feature importance business insights
    if feature_importance and feature_importance.get("feature_importance"):
        write_section("Key Drivers & Feature Importance", warning_color)
        write_text("Top factors influencing predictions:", bold=True)
        
        fi_data = feature_importance.get("feature_importance", {})
        if isinstance(fi_data, dict):
            sorted_features = sorted(fi_data.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            for i, (feature, importance) in enumerate(sorted_features, 1):
                write_text(f"{i}. {feature}: {importance:.3f}", indent=20)
        
        write_text("", size=8)  # Spacing
        write_text("Business Recommendation:", bold=True)
        write_text("Focus on features with highest importance for business strategy and data collection efforts.", indent=20)
    
    # Actionable Recommendations
    write_section("Actionable Recommendations", primary_color)
    
    write_text("1. Model Deployment Strategy:", bold=True)
    if problem_type == "classification" and best_score.get("accuracy", 0) >= 0.8:
        write_text("  • Deploy model to production with confidence monitoring", indent=20)
        write_text("  • Set up A/B testing to compare model predictions with current methods", indent=20)
        write_text("  • Monitor model performance monthly and retrain quarterly", indent=20)
    else:
        write_text("  • Consider additional feature engineering before deployment", indent=20)
        write_text("  • Collect more training data if possible", indent=20)
        write_text("  • Test model on recent data to validate performance", indent=20)
    
    write_text("", size=8)
    write_text("2. Business Process Integration:", bold=True)
    write_text("  • Integrate model predictions into decision-making workflows", indent=20)
    write_text("  • Train staff on interpreting model outputs", indent=20)
    write_text("  • Establish feedback loops to continuously improve model", indent=20)
    
    write_text("", size=8)
    write_text("3. Risk Management:", bold=True)
    write_text("  • Monitor for model drift and data quality issues", indent=20)
    write_text("  • Implement human oversight for high-stakes predictions", indent=20)
    write_text("  • Document model limitations and edge cases", indent=20)
    
    # Model Performance Details
    write_section("Detailed Model Analysis", success_color)
    
    for model_name, model_data in models.items():
        metrics = model_data.get("metrics", {})
        write_text(f"{model_name}:", size=12, bold=True)
        
        if problem_type == "classification":
            if "classification_report" in metrics:
                report = metrics["classification_report"]
                if isinstance(report, dict) and "accuracy" in report:
                    write_text(f"  Overall Accuracy: {report['accuracy']*100:.1f}%", indent=20)
            
            if "confusion_matrix" in metrics:
                write_text("  Confusion Matrix available for detailed error analysis", indent=20)
        else:
            if "rmse" in metrics:
                write_text(f"  RMSE: {metrics['rmse']:.2f}", indent=20)
            if "r2_score" in metrics:
                write_text(f"  R² Score: {metrics['r2_score']:.3f}", indent=20)
        
        y -= 10
    
    # Footer
    c.showPage()
    y = height - 40
    c.setFillColor(light_gray)
    c.rect(0, 0, width, 40, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Helvetica", 8)
    c.drawString(50, 15, f"AETHER Insight Platform - ML Business Analysis - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    
    c.save()
    return bio.getvalue()

