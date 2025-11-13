"""
Tests for data processing module
"""
import pytest
import pandas as pd
import numpy as np
from app.modules import data_processing


def test_clean_data():
    """Test data cleaning"""
    df = pd.DataFrame({
        'col1': [1, 2, 2, 3, None],
        'col2': ['a', 'b', 'b', 'c', 'd']
    })
    
    df_cleaned = data_processing.clean_data(df, user_approved=True, operations=['remove_duplicates'])
    
    assert len(df_cleaned) <= len(df)
    assert df_cleaned.duplicated().sum() == 0


def test_compute_data_integrity_score():
    """Test data integrity score"""
    # Good integrity
    df_good = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': [10, 20, 30, 40, 50]
    })
    
    score_good = data_processing.compute_data_integrity_score(df_good)
    assert score_good >= 80
    
    # Poor integrity (with outliers)
    df_poor = pd.DataFrame({
        'col1': [1, 2, 3, 4, 1000],  # Outlier
        'col2': [10, 20, 30, 40, 50]
    })
    
    score_poor = data_processing.compute_data_integrity_score(df_poor)
    assert score_poor < score_good


def test_suggest_cleaning_operations():
    """Test cleaning operation suggestions"""
    df = pd.DataFrame({
        'col1': [1, 2, 2, 3, None, None],
        'col2': ['a', 'b', 'b', 'c', 'd', 'd'],
        'sparse': [None] * 5 + [1]  # 90%+ missing
    })
    
    profile = data_processing.profile_data(df)
    suggestions = data_processing.suggest_cleaning_operations(df, profile)
    
    assert len(suggestions) > 0
    assert any(s['operation'] == 'remove_duplicates' for s in suggestions)
    assert any(s['operation'] == 'handle_missing' for s in suggestions)

