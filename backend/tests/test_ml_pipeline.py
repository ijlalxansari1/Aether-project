"""
Tests for ML pipeline module
"""
import pytest
import pandas as pd
import numpy as np
from app.modules import ml_pipeline


def test_prepare_data():
    """Test data preparation for ML"""
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': ['a', 'b', 'a', 'b', 'a'],
        'target': [10, 20, 30, 40, 50]
    })
    
    data_prep = ml_pipeline.prepare_data(df, 'target')
    
    assert 'X_train' in data_prep
    assert 'X_test' in data_prep
    assert 'y_train' in data_prep
    assert 'y_test' in data_prep
    assert len(data_prep['X_train']) > 0
    assert len(data_prep['X_test']) > 0


def test_train_selected_models():
    """Test model training"""
    df = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)  # Binary classification
    })
    
    results = ml_pipeline.train_selected_models(
        df, 'target', ['Logistic Regression', 'Random Forest']
    )
    
    assert 'models' in results
    assert 'best_model' in results
    assert len(results['models']) > 0
    
    # Check that at least one model was trained successfully
    successful_models = [
        name for name, data in results['models'].items()
        if 'metrics' in data
    ]
    assert len(successful_models) > 0

