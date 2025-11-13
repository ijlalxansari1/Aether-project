"""
FAQ / Glossary data provider (lightweight).
"""
from typing import List, Dict

FAQ: List[Dict[str, str]] = [
    {
        "q": "What is Data Quality Score?",
        "a": "A 0–100 score combining completeness, consistency, and readability to indicate how usable the dataset is without cleaning.",
        "ethical": "Poor quality can mask bias; review missingness by subgroup."
    },
    {
        "q": "What does AUC mean?",
        "a": "Area Under the ROC Curve; probability the classifier ranks a random positive higher than a random negative.",
        "ethical": "High AUC does not imply fairness across subgroups."
    },
    {
        "q": "What is class imbalance?",
        "a": "When one class dominates the dataset; can lead to biased models and misleading metrics.",
        "ethical": "Consider reweighting or stratified sampling to mitigate harm."
    },
]

GLOSSARY: List[Dict[str, str]] = [
    {"term": "Precision", "definition": "TP / (TP + FP)", "why": "Measures exactness of positive predictions."},
    {"term": "Recall", "definition": "TP / (TP + FN)", "why": "Measures completeness of positive predictions."},
    {"term": "Skew", "definition": "Asymmetry of a distribution", "why": "High skew may distort model training."},
]


def get_faq() -> List[Dict[str, str]]:
    return FAQ


def get_glossary() -> List[Dict[str, str]]:
    return GLOSSARY
