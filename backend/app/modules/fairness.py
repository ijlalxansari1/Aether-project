"""
Explainability & Fairness Module
Handles SHAP/LIME explanations, bias evaluation, and counterfactuals
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import shap
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


def compute_feature_importance(model, df: pd.DataFrame, 
                               feature_names: List[str],
                               X_test: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute feature importance using SHAP values
    
    Args:
        model: Trained model
        df: Original DataFrame
        feature_names: List of feature names
        X_test: Test features
        
    Returns:
        Dictionary with feature importance scores
    """
    try:
        # Use TreeExplainer for tree-based models
        if hasattr(model, 'feature_importances_'):
            # Tree-based model
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_test)
            
            # Handle multi-class case
            if isinstance(shap_values, list):
                shap_values = np.mean(np.abs(shap_values), axis=0)
            else:
                shap_values = np.abs(shap_values)
            
            # Calculate mean absolute SHAP values per feature
            feature_importance = {}
            if len(shap_values.shape) > 1:
                mean_shap = np.mean(shap_values, axis=0)
            else:
                mean_shap = shap_values
            
            for i, feature in enumerate(feature_names):
                if i < len(mean_shap):
                    feature_importance[feature] = float(mean_shap[i])
        else:
            # Linear model or other
            try:
                explainer = shap.LinearExplainer(model, X_test)
                shap_values = explainer.shap_values(X_test)
                
                if isinstance(shap_values, list):
                    shap_values = np.mean(np.abs(shap_values), axis=0)
                else:
                    shap_values = np.abs(shap_values)
                
                mean_shap = np.mean(shap_values, axis=0) if len(shap_values.shape) > 1 else shap_values
                
                feature_importance = {}
                for i, feature in enumerate(feature_names):
                    if i < len(mean_shap):
                        feature_importance[feature] = float(mean_shap[i])
            except:
                # Fallback to model coefficients if available
                if hasattr(model, 'coef_'):
                    coef = np.abs(model.coef_)
                    if len(coef.shape) > 1:
                        coef = np.mean(coef, axis=0)
                    
                    feature_importance = {}
                    for i, feature in enumerate(feature_names):
                        if i < len(coef):
                            feature_importance[feature] = float(coef[i])
                else:
                    # Default: equal importance
                    feature_importance = {feature: 1.0 / len(feature_names) for feature in feature_names}
        
        # Normalize to sum to 1
        total = sum(feature_importance.values())
        if total > 0:
            feature_importance = {k: v / total for k, v in feature_importance.items()}
        
        # Sort by importance
        sorted_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "feature_importance": sorted_importance,
            "top_features": list(sorted_importance.keys())[:10]
        }
    
    except Exception as e:
        # Fallback: use model's built-in feature importance if available
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_importance = {feature_names[i]: float(importance[i]) 
                                 for i in range(min(len(feature_names), len(importance)))}
            sorted_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            return {
                "feature_importance": sorted_importance,
                "top_features": list(sorted_importance.keys())[:10],
                "method": "built-in"
            }
        else:
            return {
                "feature_importance": {},
                "top_features": [],
                "error": str(e)
            }


def evaluate_fairness(df: pd.DataFrame, target_column: str, 
                     group_column: str, predictions: np.ndarray,
                     problem_type: str = "classification") -> Dict[str, Any]:
    """
    Evaluate fairness metrics across subgroups
    
    Args:
        df: Input DataFrame
        target_column: Target column name
        group_column: Column to group by for fairness evaluation
        predictions: Model predictions
        problem_type: "classification" or "regression"
        
    Returns:
        Dictionary with fairness metrics
    """
    if group_column not in df.columns:
        return {"error": f"Group column '{group_column}' not found"}
    
    if target_column not in df.columns:
        return {"error": f"Target column '{target_column}' not found"}
    
    # Align predictions with dataframe (assuming same order)
    df_eval = df.copy()
    if len(predictions) <= len(df_eval):
        df_eval = df_eval.iloc[:len(predictions)]
        df_eval['predictions'] = predictions
    else:
        return {"error": "Predictions length mismatch with dataframe"}
    
    fairness_metrics = {
        "group_column": group_column,
        "groups": {},
        "overall_metrics": {},
        "bias_detected": False
    }
    
    # Get unique groups
    groups = df_eval[group_column].unique()
    
    if problem_type == "classification":
        from sklearn.metrics import accuracy_score, f1_score
        
        # Overall metrics
        overall_accuracy = accuracy_score(df_eval[target_column], df_eval['predictions'])
        overall_f1 = f1_score(df_eval[target_column], df_eval['predictions'], average='weighted')
        
        fairness_metrics["overall_metrics"] = {
            "accuracy": float(overall_accuracy),
            "f1_score": float(overall_f1)
        }
        
        # Per-group metrics
        group_accuracies = []
        group_f1_scores = []
        
        for group in groups:
            group_data = df_eval[df_eval[group_column] == group]
            if len(group_data) > 0:
                group_accuracy = accuracy_score(group_data[target_column], group_data['predictions'])
                group_f1 = f1_score(group_data[target_column], group_data['predictions'], average='weighted')
                
                fairness_metrics["groups"][str(group)] = {
                    "count": int(len(group_data)),
                    "accuracy": float(group_accuracy),
                    "f1_score": float(group_f1),
                    "accuracy_difference": float(group_accuracy - overall_accuracy)
                }
                
                group_accuracies.append(group_accuracy)
                group_f1_scores.append(group_f1)
        
        # Detect bias: if accuracy difference > 10% for any group
        max_diff = max([abs(metrics["accuracy_difference"]) 
                       for metrics in fairness_metrics["groups"].values()])
        
        if max_diff > 0.10:  # 10% threshold
            fairness_metrics["bias_detected"] = True
            fairness_metrics["bias_severity"] = "high" if max_diff > 0.20 else "medium"
            fairness_metrics["bias_description"] = f"Significant performance disparity detected: " \
                                                  f"maximum accuracy difference of {max_diff*100:.1f}% across groups"
    
    else:  # regression
        from sklearn.metrics import mean_squared_error, r2_score
        
        overall_rmse = np.sqrt(mean_squared_error(df_eval[target_column], df_eval['predictions']))
        overall_r2 = r2_score(df_eval[target_column], df_eval['predictions'])
        
        fairness_metrics["overall_metrics"] = {
            "rmse": float(overall_rmse),
            "r2_score": float(overall_r2)
        }
        
        group_rmses = []
        
        for group in groups:
            group_data = df_eval[df_eval[group_column] == group]
            if len(group_data) > 0:
                group_rmse = np.sqrt(mean_squared_error(group_data[target_column], group_data['predictions']))
                group_r2 = r2_score(group_data[target_column], group_data['predictions'])
                
                fairness_metrics["groups"][str(group)] = {
                    "count": int(len(group_data)),
                    "rmse": float(group_rmse),
                    "r2_score": float(group_r2),
                    "rmse_difference": float(group_rmse - overall_rmse)
                }
                
                group_rmses.append(group_rmse)
        
        # Detect bias: if RMSE difference > 20% for any group
        if group_rmses:
            max_diff = max([abs(metrics["rmse_difference"]) 
                           for metrics in fairness_metrics["groups"].values()])
            relative_diff = max_diff / overall_rmse if overall_rmse > 0 else 0
            
            if relative_diff > 0.20:  # 20% threshold
                fairness_metrics["bias_detected"] = True
                fairness_metrics["bias_severity"] = "high" if relative_diff > 0.40 else "medium"
                fairness_metrics["bias_description"] = f"Significant performance disparity detected: " \
                                                      f"maximum RMSE difference of {relative_diff*100:.1f}% across groups"
    
    return fairness_metrics


def generate_counterfactual(model, input_row: Dict[str, Any], 
                           feature_names: List[str],
                           target_value: Optional[Any] = None,
                           max_changes: int = 3) -> Dict[str, Any]:
    """
    Generate counterfactual explanation for a prediction
    
    Args:
        model: Trained model
        input_row: Input features as dictionary
        feature_names: List of feature names
        target_value: Desired target value (optional)
        max_changes: Maximum number of features to change
        
    Returns:
        Dictionary with counterfactual explanation
    """
    try:
        # Convert input to array
        input_array = np.array([input_row.get(f, 0) for f in feature_names]).reshape(1, -1)
        
        # Get original prediction
        original_prediction = model.predict(input_array)[0]
        
        # Simple counterfactual: try small perturbations
        counterfactual = input_row.copy()
        changes = []
        
        # Get feature importance if available
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_importance = {feature_names[i]: importance[i] 
                                 for i in range(len(feature_names))}
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        else:
            sorted_features = [(f, 1.0) for f in feature_names]
        
        # Try changing features to flip prediction
        for feature, _ in sorted_features[:max_changes]:
            if feature in input_row:
                original_value = input_row[feature]
                
                # Try different values
                if isinstance(original_value, (int, float)):
                    # Try increasing and decreasing
                    for multiplier in [1.1, 1.2, 0.9, 0.8]:
                        new_value = original_value * multiplier
                        test_input = input_row.copy()
                        test_input[feature] = new_value
                        test_array = np.array([test_input.get(f, 0) for f in feature_names]).reshape(1, -1)
                        new_prediction = model.predict(test_array)[0]
                        
                        if target_value is not None:
                            if new_prediction == target_value:
                                counterfactual[feature] = new_value
                                changes.append({
                                    "feature": feature,
                                    "original_value": original_value,
                                    "new_value": new_value,
                                    "change": f"{((new_value - original_value) / original_value * 100):.1f}%"
                                })
                                break
                        else:
                            if new_prediction != original_prediction:
                                counterfactual[feature] = new_value
                                changes.append({
                                    "feature": feature,
                                    "original_value": original_value,
                                    "new_value": new_value,
                                    "change": f"{((new_value - original_value) / original_value * 100):.1f}%"
                                })
                                break
        
        # Get new prediction
        counterfactual_array = np.array([counterfactual.get(f, 0) for f in feature_names]).reshape(1, -1)
        new_prediction = model.predict(counterfactual_array)[0]
        
        return {
            "original_input": input_row,
            "original_prediction": float(original_prediction) if isinstance(original_prediction, (int, float)) else str(original_prediction),
            "counterfactual": counterfactual,
            "new_prediction": float(new_prediction) if isinstance(new_prediction, (int, float)) else str(new_prediction),
            "changes": changes,
            "explanation": f"To change the prediction from {original_prediction} to {new_prediction}, "
                          f"modify {len(changes)} feature(s): {', '.join([c['feature'] for c in changes])}"
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "original_input": input_row,
            "original_prediction": None
        }

