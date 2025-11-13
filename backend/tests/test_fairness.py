"""
Tests for fairness module
"""
import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.modules import fairness, ml_pipeline


def test_evaluate_fairness():
    """Test fairness evaluation"""
    # Create dataset with potential bias
    np.random.seed(42)
    df = pd.DataFrame({
        'feature1': np.random.randn(200),
        'group': ['A'] * 100 + ['B'] * 100,
        'target': np.random.randint(0, 2, 200)
    })
    
    # Train a simple model
    data_prep = ml_pipeline.prepare_data(df, 'target')
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(data_prep['X_train'], data_prep['y_train'])
    predictions = model.predict(data_prep['X_test'])
    
    # Evaluate fairness
    fairness_result = fairness.evaluate_fairness(
        df.iloc[data_prep['X_test'].index] if hasattr(data_prep['X_test'], 'index') else df,
        'target',
        'group',
        predictions,
        'classification'
    )
    
    assert 'groups' in fairness_result
    assert 'bias_detected' in fairness_result
    assert len(fairness_result['groups']) > 0


def test_compute_feature_importance():
    """Test feature importance computation"""
    df = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)
    })
    
    data_prep = ml_pipeline.prepare_data(df, 'target')
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(data_prep['X_train'], data_prep['y_train'])
    
    importance = fairness.compute_feature_importance(
        model, df, data_prep['feature_names'], data_prep['X_test']
    )
    
    assert 'feature_importance' in importance
    assert len(importance['feature_importance']) > 0

