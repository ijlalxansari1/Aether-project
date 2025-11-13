"""
Tests for data ingestion module
"""
import pytest
import pandas as pd
import os
from app.modules import ingestion


def test_auto_detect_types():
    """Test automatic data type detection"""
    df = pd.DataFrame({
        'numeric': ['1', '2', '3'],
        'text': ['a', 'b', 'c'],
        'date': ['2023-01-01', '2023-01-02', '2023-01-03']
    })
    
    df_processed = ingestion.auto_detect_types(df)
    
    assert df_processed['numeric'].dtype in ['int64', 'float64']
    assert df_processed['text'].dtype == 'object'


def test_profile_data():
    """Test data profiling"""
    df = pd.DataFrame({
        'col1': [1, 2, 3, None, 5],
        'col2': ['a', 'b', 'a', 'b', 'c']
    })
    
    from app.modules.data_processing import profile_data
    profile = profile_data(df)
    
    assert profile['summary']['row_count'] == 5
    assert profile['summary']['column_count'] == 2
    assert 'col1' in profile['columns']
    assert profile['columns']['col1']['missing_count'] == 1


def test_compute_data_quality_score():
    """Test data quality score computation"""
    # High quality dataset
    df_high = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['a', 'b', 'c', 'd', 'e']
    })
    
    from app.modules.data_processing import compute_data_quality_score
    score_high = compute_data_quality_score(df_high)
    
    assert score_high >= 80
    
    # Low quality dataset
    df_low = pd.DataFrame({
        'col1': [1, None, None, None, 5],
        'col2': ['a', '', '', '', 'e']
    })
    
    score_low = compute_data_quality_score(df_low)
    assert score_low < score_high


def test_detect_problem_type():
    """Test problem type detection"""
    from app.modules.ml_pipeline import detect_problem_type
    
    # Classification dataset
    df_class = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'target': ['A', 'B', 'A', 'B', 'A']
    })
    
    problem_type = detect_problem_type(df_class, 'target')
    assert problem_type == 'classification'
    
    # Regression dataset
    df_reg = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'target': [10.5, 20.3, 30.1, 40.2, 50.8]
    })
    
    problem_type = detect_problem_type(df_reg, 'target')
    assert problem_type == 'regression'


def test_recommend_models():
    """Test model recommendations"""
    from app.modules.ml_pipeline import recommend_models
    
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'target': ['A', 'B', 'A', 'B', 'A']
    })
    
    recommendations = recommend_models(df, 'target')
    
    assert len(recommendations) > 0
    assert any(r['type'] == 'baseline' for r in recommendations)
    assert any(r['type'] == 'advanced' for r in recommendations)


if __name__ == '__main__':
    pytest.main([__file__])

