"""
ML Pipeline Module
Handles problem detection, model recommendation, and training
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, 
    mean_squared_error, r2_score, classification_report, confusion_matrix,
    precision_score, recall_score, roc_curve
)
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')


def detect_problem_type(df: pd.DataFrame, target_column: str) -> str:
    """
    Auto-detect if the problem is classification or regression
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")
    
    target = df[target_column]
    
    if target.dtype == 'object' or target.dtype.name == 'category':
        return "classification"
    
    unique_ratio = target.nunique() / len(target)
    if target.nunique() <= 10 or unique_ratio < 0.05:
        return "classification"
    return "regression"


def recommend_models(df: pd.DataFrame, target_column: str, 
                    problem_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recommend models based on dataset characteristics"""
    if problem_type is None:
        problem_type = detect_problem_type(df, target_column)
    
    recommendations = []
    
    if problem_type == "classification":
        recommendations.append({
            "name": "Logistic Regression",
            "type": "baseline",
            "description": "Fast, interpretable baseline model for classification",
            "pros": ["Fast training", "Interpretable", "Good for linear relationships"],
            "cons": ["Assumes linearity", "May underperform on complex patterns"]
        })
        recommendations.append({
            "name": "Random Forest",
            "type": "advanced",
            "description": "Ensemble method that handles non-linear relationships well",
            "pros": ["Handles non-linearity", "Feature importance", "Robust to overfitting"],
            "cons": ["Less interpretable", "Slower than linear models"]
        })
        recommendations.append({
            "name": "XGBoost",
            "type": "advanced",
            "description": "Gradient boosting model with excellent performance",
            "pros": ["High accuracy", "Handles missing values", "Feature importance"],
            "cons": ["Requires tuning", "Less interpretable", "Slower training"]
        })
        recommendations.append({
            "name": "SVM",
            "type": "advanced",
            "description": "Support Vector Machine for complex decision boundaries",
            "pros": ["Effective for high-dimensional data", "Memory efficient"],
            "cons": ["Slow on large datasets", "Requires feature scaling"]
        })
    else:
        recommendations.append({
            "name": "Linear Regression",
            "type": "baseline",
            "description": "Simple, interpretable baseline model for regression",
            "pros": ["Fast training", "Highly interpretable", "Good for linear relationships"],
            "cons": ["Assumes linearity", "Sensitive to outliers"]
        })
        recommendations.append({
            "name": "Random Forest Regressor",
            "type": "advanced",
            "description": "Ensemble method for non-linear regression",
            "pros": ["Handles non-linearity", "Feature importance", "Robust"],
            "cons": ["Less interpretable", "May overfit"]
        })
        recommendations.append({
            "name": "XGBoost Regressor",
            "type": "advanced",
            "description": "Gradient boosting for regression with high accuracy",
            "pros": ["High accuracy", "Handles missing values", "Feature importance"],
            "cons": ["Requires tuning", "Less interpretable"]
        })
        recommendations.append({
            "name": "SVR",
            "type": "advanced",
            "description": "Support Vector Regression for complex patterns",
            "pros": ["Effective for non-linear patterns", "Memory efficient"],
            "cons": ["Slow on large datasets", "Requires feature scaling"]
        })
    
    return recommendations


def _expand_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    for col in df2.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
        df2[f"{col}_year"] = df2[col].dt.year
        df2[f"{col}_month"] = df2[col].dt.month
        df2[f"{col}_day"] = df2[col].dt.day
        df2[f"{col}_weekday"] = df2[col].dt.weekday
        if hasattr(df2[col].dt, 'hour'):
            df2[f"{col}_hour"] = df2[col].dt.hour
    return df2


def _smart_type_inference(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    # Coerce numeric-like strings
    for col in df2.columns:
        if df2[col].dtype == 'object':
            # try numeric
            coerced = pd.to_numeric(df2[col], errors='ignore')
            if coerced.dtype != 'object':
                df2[col] = coerced
                continue
            # try datetime
            try:
                dt = pd.to_datetime(df2[col], errors='raise', utc=False, infer_datetime_format=True)
                # accept if decent parse rate
                parsed_ratio = dt.notna().mean()
                if parsed_ratio > 0.9:
                    df2[col] = dt
            except Exception:
                pass
    return df2


def _prune_features(X: pd.DataFrame, y: pd.Series, target_column: str) -> pd.DataFrame:
    Xp = X.copy()
    # Remove columns identical to target (leakage)
    if target_column in Xp.columns:
        Xp = Xp.drop(columns=[target_column])
    # Remove zero-variance columns
    nunique = Xp.nunique(dropna=False)
    zero_var_cols = nunique[nunique <= 1].index.tolist()
    if zero_var_cols:
        Xp = Xp.drop(columns=zero_var_cols)
    # Remove highly correlated numeric features (threshold 0.98)
    num_cols = Xp.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 1:
        corr = Xp[num_cols].corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        to_drop = [column for column in upper.columns if any(upper[column] > 0.98)]
        if to_drop:
            Xp = Xp.drop(columns=to_drop)
    return Xp


def prepare_data(df: pd.DataFrame, target_column: str, 
                test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
    """Prepare data for model training with light feature engineering"""
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")

    # Smart inference before cleaning
    df_cast = _smart_type_inference(df)

    df_clean = df_cast.dropna(subset=[target_column]).copy()

    # Expand datetimes to numeric components
    df_clean = _expand_datetime_features(df_clean)

    # Separate features/target
    X = df_clean.drop(columns=[target_column])
    y = df_clean[target_column]

    # Prune leakage, zero-variance and high-correlation
    X = _prune_features(X, y, target_column)

    # Identify column types
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    datetime_cols = X.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns.tolist()
    object_cols = [c for c in X.columns if c not in numeric_cols and c not in datetime_cols]

    # Categorical split by cardinality
    low_card_cats = [c for c in object_cols if X[c].nunique(dropna=False) <= 10]
    # High-card ignored for now (drop) to avoid explosion

    # Preprocessors
    numeric_processor = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])
    lowcat_processor = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_processor, numeric_cols),
            ("cat_low", lowcat_processor, low_card_cats)
        ], remainder="drop"
    )

    # Encode target if needed
    target_encoder = None
    if y.dtype == 'object':
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y.astype(str))

    # Apply transform to features
    X_processed = preprocessor.fit_transform(X)

    # Train/test split (stratify for classification)
    stratify = y if (len(np.unique(y)) < 20 and len(np.unique(y)) > 1) else None
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": list(X.columns),
        "label_encoders": {},
        "target_encoder": target_encoder,
        "scaler": None
    }


def train_selected_models(df: pd.DataFrame, target_column: str, 
                         selected_models: List[str],
                         problem_type: Optional[str] = None) -> Dict[str, Any]:
    """Train selected models and return metrics"""
    if problem_type is None:
        problem_type = detect_problem_type(df, target_column)
    
    data_prep = prepare_data(df, target_column)
    X_train = data_prep["X_train"]
    X_test = data_prep["X_test"]
    y_train = data_prep["y_train"]
    y_test = data_prep["y_test"]
    
    results = {
        "problem_type": problem_type,
        "models": {},
        "best_model": None,
        "best_score": None
    }
    
    best_score = -np.inf if problem_type == "classification" else np.inf
    
    for model_name in selected_models:
        try:
            if problem_type == "classification":
                if model_name == "Logistic Regression":
                    model = LogisticRegression(max_iter=1000, random_state=42)
                elif model_name == "Random Forest":
                    model = RandomForestClassifier(n_estimators=200, random_state=42)
                elif model_name == "XGBoost":
                    model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
                elif model_name == "SVM":
                    model = SVC(probability=True, random_state=42)
                else:
                    continue
            else:
                if model_name == "Linear Regression":
                    model = LinearRegression()
                elif model_name == "Random Forest Regressor":
                    model = RandomForestRegressor(n_estimators=200, random_state=42)
                elif model_name == "XGBoost Regressor":
                    model = xgb.XGBRegressor(random_state=42)
                elif model_name == "SVR":
                    model = SVR()
                else:
                    continue
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
            
            if problem_type == "classification":
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')
                precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                metrics = {"accuracy": float(accuracy), "f1_score": float(f1), "precision": float(precision), "recall": float(recall)}
                if len(np.unique(y_test)) == 2 and y_pred_proba is not None:
                    try:
                        auc = roc_auc_score(y_test, y_pred_proba)
                        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
                        metrics["auc"] = float(auc)
                        metrics["roc_curve"] = {"fpr": [float(v) for v in fpr.tolist()], "tpr": [float(v) for v in tpr.tolist()]}
                    except Exception:
                        pass
                metrics["classification_report"] = classification_report(y_test, y_pred, output_dict=True)
                metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
                score = accuracy
            else:
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                metrics = {"rmse": float(rmse), "r2_score": float(r2)}
                score = -rmse
            
            results["models"][model_name] = {"model": model, "metrics": metrics, "predictions": y_pred.tolist(), "predictions_proba": y_pred_proba.tolist() if y_pred_proba is not None else None}
            if (problem_type == "classification" and score > best_score) or (problem_type == "regression" and score > best_score):
                best_score = score
                results["best_model"] = model_name
                results["best_score"] = metrics
        except Exception as e:
            results["models"][model_name] = {"error": str(e), "status": "failed"}
    
    return results

