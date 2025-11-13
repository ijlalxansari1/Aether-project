"""
Story Mode: generate structured narrative paragraphs based on user intent, audience, and direction.
"""
from typing import Dict, Any, List


def generate_story(intent: str, audience: str, direction: str, eda: Dict[str, Any], ethics: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Generate a focused story with 3-5 key insights from EDA.
    Structure: Problem → Discovery → Implication → Recommendation
    """
    sections: List[Dict[str, str]] = []

    # Introduction - tailored to intent and audience
    intent_map = {
        "explain": "explain what happened in the data",
        "explore": "explore patterns and relationships",
        "predict": "build predictive models"
    }
    audience_map = {
        "exec": "executive",
        "tech": "technical",
        "general": "general"
    }
    intro = f"This analysis aims to {intent_map.get(intent, 'analyze')} the dataset for a {audience_map.get(audience, 'general')} audience."
    sections.append({"title": "Introduction", "body": intro})

    # Problem Statement (based on data quality and issues found)
    problems = []
    miss = eda.get("missing_report", {})
    if miss and miss.get("total_missing", 0) > 0:
        problems.append(f"Data completeness issues: {miss.get('total_missing', 0)} missing values detected.")
    
    insights = eda.get("insights", [])
    warning_insights = [i for i in insights if "⚠️" in i]
    if warning_insights:
        problems.append(f"Data quality concerns identified: {len(warning_insights)} issue(s) requiring attention.")
    
    if ethics and ethics.get("sensitive_attributes"):
        problems.append(f"Ethical considerations: {len(ethics.get('sensitive_attributes', []))} sensitive attribute(s) detected.")
    
    if problems:
        sections.append({
            "title": "Problem Statement",
            "body": " ".join(problems) if problems else "No significant data quality issues detected."
        })
    else:
        sections.append({
            "title": "Problem Statement",
            "body": "The dataset appears to be in good condition with minimal quality issues."
        })

    # Key Discoveries (3-5 most important insights from EDA)
    key_insights = []
    
    # Select top insights - prioritize warnings and important findings
    if insights:
        # Get positive insights (✓) and important findings
        positive_insights = [i for i in insights if "✓" in i and "numeric" in i.lower() or "categorical" in i.lower()]
        important_findings = [i for i in insights if "correlation" in i.lower() or "outlier" in i.lower()]
        
        # Combine and limit to 3-5
        selected = (warning_insights[:2] + positive_insights[:2] + important_findings[:1])[:5]
        key_insights = selected if selected else insights[:5]
    
    if key_insights:
        discoveries_text = "Key findings from exploratory data analysis:\n\n" + "\n".join(f"• {i.replace('⚠️', '').replace('✓', '').strip()}" for i in key_insights)
        sections.append({"title": "Key Discoveries", "body": discoveries_text})
    else:
        summary = eda.get("summary_stats", {})
        num_cols = len(summary.get("columns", []))
        sections.append({
            "title": "Key Discoveries",
            "body": f"Analysis of {num_cols} numeric feature(s) revealed patterns and relationships in the data."
        })

    # Implications (What do the findings mean?)
    direction_map = {
        "trends": "The identified patterns suggest notable trends that could inform strategic decisions.",
        "risks": "The detected issues highlight potential risks that should be addressed before deployment.",
        "opportunities": "The analysis reveals opportunities for optimization and improvement."
    }
    implication = direction_map.get(direction.lower(), "The findings provide valuable insights for decision-making.")
    
    # Add context based on insights
    if any("correlation" in i.lower() for i in key_insights):
        implication += " Strong correlations between variables indicate important relationships worth exploring further."
    if any("outlier" in i.lower() for i in key_insights):
        implication += " Outliers detected may represent edge cases or data quality issues requiring investigation."
    
    sections.append({"title": "Implications", "body": implication})

    # Recommendations (What should be done?)
    recommendations = []
    
    if warning_insights:
        recommendations.append("Address data quality issues identified in the analysis before proceeding.")
    
    if direction.lower() == "predict":
        recommendations.append("Proceed to machine learning model training to build predictive capabilities.")
    elif direction.lower() == "trends":
        recommendations.append("Generate a comprehensive report to share findings with stakeholders.")
    else:
        recommendations.append("Consider generating a detailed report or proceeding to advanced modeling based on objectives.")
    
    if ethics and ethics.get("sensitive_attributes"):
        recommendations.append("Ensure ethical guidelines are followed when using sensitive attributes in analysis.")
    
    sections.append({
        "title": "Recommendations",
        "body": "\n".join(f"• {r}" for r in recommendations) if recommendations else "No specific recommendations at this time."
    })

    # Conclusion
    conclusion = "This analysis provides a foundation for data-driven decision making. "
    if intent == "predict":
        conclusion += "Proceed to model training to unlock predictive capabilities."
    else:
        conclusion += "Generate a shareable report to communicate findings to stakeholders."
    
    sections.append({"title": "Conclusion", "body": conclusion})

    return {"sections": sections}
