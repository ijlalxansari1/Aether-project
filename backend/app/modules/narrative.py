"""
EDA & Narrative Generation Module
Generates visualizations and natural language insights
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def _detect_data_type(df: pd.DataFrame) -> str:
    """
    Detect the primary data type/domain of the dataset
    Returns: 'time_series', 'transactional', 'survey', 'demographic', 'financial', 'mixed'
    """
    col_names = [c.lower() for c in df.columns]
    
    # Time series indicators
    time_keywords = ['date', 'time', 'timestamp', 'year', 'month', 'day', 'hour', 'quarter']
    if any(any(kw in col for kw in time_keywords) for col in col_names):
        # Check if there's a clear time column
        time_cols = [c for c in df.columns if any(kw in c.lower() for kw in time_keywords)]
        if time_cols:
            try:
                pd.to_datetime(df[time_cols[0]].dropna().head(100))
                return 'time_series'
            except:
                pass
    
    # Transactional indicators
    trans_keywords = ['transaction', 'order', 'purchase', 'sale', 'item', 'product', 'customer_id']
    if sum(1 for col in col_names if any(kw in col for kw in trans_keywords)) >= 3:
        return 'transactional'
    
    # Survey indicators
    survey_keywords = ['rating', 'score', 'response', 'question', 'survey', 'answer', 'agree']
    if sum(1 for col in col_names if any(kw in col for kw in survey_keywords)) >= 2:
        return 'survey'
    
    # Demographic indicators
    demo_keywords = ['age', 'gender', 'race', 'ethnic', 'location', 'city', 'country', 'region']
    if sum(1 for col in col_names if any(kw in col for kw in demo_keywords)) >= 3:
        return 'demographic'
    
    # Financial indicators
    financial_keywords = ['price', 'cost', 'revenue', 'profit', 'income', 'salary', 'amount', 'balance']
    if sum(1 for col in col_names if any(kw in col for kw in financial_keywords)) >= 2:
        return 'financial'
    
    return 'mixed'


def generate_eda_visuals(df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
    """
    Generate data-type aware EDA visualizations
    Performs different analysis based on detected data type
    
    Args:
        df: Input DataFrame
        target_column: Optional target column for supervised analysis
        
    Returns:
        Dictionary with visualization data and metadata
    """
    data_type = _detect_data_type(df)
    visuals = {
        "histograms": [],
        "correlations": None,
        "scatter_plots": [],
        "box_plots": [],
        "missing_heatmap": None,
        "data_type": data_type,
        "type_specific_visuals": []
    }
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Color schemes for different data types
    color_schemes = {
        'time_series': ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd'],
        'transactional': ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0'],
        'survey': ['#f59e0b', '#fbbf24', '#fcd34d', '#fde68a'],
        'demographic': ['#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe'],
        'financial': ['#ef4444', '#f87171', '#fca5a5', '#fecaca'],
        'mixed': ['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe']
    }
    colors = color_schemes.get(data_type, color_schemes['mixed'])
    
    # Generate histograms for numeric columns with improved binning
    for col in numeric_cols[:10]:  # Limit to 10 columns
        col_data = df[col].dropna()
        if len(col_data) > 0:
            # Smart binning: use Sturges' rule or Freedman-Diaconis rule
            n_bins = min(50, max(10, int(np.log2(len(col_data)) + 1)))
            # Ensure bins don't exceed data range
            if col_data.nunique() < n_bins:
                n_bins = col_data.nunique()
            
            fig = px.histogram(
                df, 
                x=col, 
                nbins=n_bins,
                title=f"Distribution of {col}",
                labels={col: col.replace('_', ' ').title()},
                color_discrete_sequence=[colors[0]]  # Use data-type specific color
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(t=50, b=50, l=50, r=20)
            )
            fig.update_traces(marker_line_width=1, marker_line_color='white')
            visuals["histograms"].append({
                "column": col,
                "figure": fig.to_json(),
                "type": "histogram"
            })
    
    # Correlation heatmap for numeric columns with improved display
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        # Round correlation values for better display
        corr_matrix_rounded = corr_matrix.round(3)
        
        # Create heatmap with proper color scale (blue for positive, red for negative)
        # Prepare text annotations
        text_annotations = []
        for i in range(len(corr_matrix_rounded.columns)):
            row = []
            for j in range(len(corr_matrix_rounded.columns)):
                val = corr_matrix_rounded.iloc[i, j]
                row.append(f'{val:.2f}' if not pd.isna(val) else '')
            text_annotations.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix_rounded.values,
            x=corr_matrix_rounded.columns,
            y=corr_matrix_rounded.columns,
            colorscale=[[0, '#ef4444'], [0.5, '#f3f4f6'], [1, '#3b82f6']],  # Red to Gray to Blue
            zmid=0,
            text=text_annotations,
            texttemplate='%{text}',
            textfont={"size": 10, "color": "white"},
            colorbar=dict(title="Correlation", titleside="right"),
            hoverongaps=False,
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Correlation Heatmap",
            height=500,
            width=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11),
            margin=dict(t=60, b=50, l=100, r=50),
            xaxis=dict(side="bottom"),
            yaxis=dict(autorange="reversed")
        )
        
        visuals["correlations"] = {
            "figure": fig.to_json(),
            "matrix": corr_matrix.to_dict()
        }
    
    # Scatter plots (if target column provided)
    if target_column and target_column in numeric_cols:
        for col in numeric_cols[:5]:  # Limit to 5 features
            if col != target_column:
                fig = px.scatter(
                    df, 
                    x=col, 
                    y=target_column,
                    title=f"{col.replace('_', ' ').title()} vs {target_column.replace('_', ' ').title()}",
                    trendline="ols",
                    labels={
                        col: col.replace('_', ' ').title(),
                        target_column: target_column.replace('_', ' ').title()
                    },
                    color_discrete_sequence=[colors[0]]  # Use data-type specific color
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(t=50, b=50, l=50, r=20)
                )
                fig.update_traces(marker=dict(size=4, opacity=0.6))
                visuals["scatter_plots"].append({
                    "x": col,
                    "y": target_column,
                    "figure": fig.to_json()
                })
    
    # Box plots for numeric columns with improved display
    for col in numeric_cols[:5]:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            fig = px.box(
                df, 
                y=col, 
                title=f"Box Plot: {col}",
                labels={col: col.replace('_', ' ').title()},
                color_discrete_sequence=[colors[1]]  # Use data-type specific color
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(t=50, b=50, l=50, r=20),
                yaxis=dict(title=col.replace('_', ' ').title())
            )
            fig.update_traces(
                boxmean='sd',  # Show mean and standard deviation
                marker=dict(size=3, opacity=0.6),
                line=dict(width=2)
            )
            visuals["box_plots"].append({
                "column": col,
                "figure": fig.to_json()
            })
    
    # Missing values heatmap
    if df.isnull().sum().sum() > 0:
        missing_data = df.isnull()
        fig = px.imshow(
            missing_data,
            labels=dict(x="Column", y="Row", color="Missing"),
            title="Missing Values Heatmap",
            color_continuous_scale="Reds"
        )
        visuals["missing_heatmap"] = {
            "figure": fig.to_json(),
            "missing_counts": df.isnull().sum().to_dict()
        }
    
    # Type-specific visualizations
    if data_type == 'time_series':
        # Time series: line plots over time
        time_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['date', 'time', 'timestamp', 'year', 'month'])]
        if time_cols and len(numeric_cols) > 0:
            try:
                time_col = time_cols[0]
                df_time = df.copy()
                df_time[time_col] = pd.to_datetime(df_time[time_col], errors='coerce')
                df_time = df_time.dropna(subset=[time_col]).sort_values(time_col)
                for num_col in numeric_cols[:3]:
                    fig = px.line(
                        df_time, 
                        x=time_col, 
                        y=num_col,
                        title=f"{num_col.replace('_', ' ').title()} Over Time",
                        color_discrete_sequence=[colors[0]]
                    )
                    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    visuals["type_specific_visuals"].append({
                        "type": "time_series",
                        "column": num_col,
                        "figure": fig.to_json()
                    })
            except:
                pass
    
    elif data_type == 'transactional':
        # Transactional: frequency analysis
        if categorical_cols:
            for cat_col in categorical_cols[:3]:
                value_counts = df[cat_col].value_counts().head(10)
                fig = px.bar(
                    x=value_counts.index, 
                    y=value_counts.values,
                    title=f"Top 10 {cat_col.replace('_', ' ').title()}",
                    color_discrete_sequence=[colors[0]]
                )
                fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                visuals["type_specific_visuals"].append({
                    "type": "frequency",
                    "column": cat_col,
                    "figure": fig.to_json()
                })
    
    elif data_type == 'survey':
        # Survey: distribution of ratings/scores
        rating_cols = [c for c in numeric_cols if any(kw in c.lower() for kw in ['rating', 'score', 'response'])]
        if rating_cols:
            for col in rating_cols[:3]:
                fig = px.histogram(
                    df, 
                    x=col, 
                    nbins=min(20, df[col].nunique()),
                    title=f"Distribution of {col.replace('_', ' ').title()}",
                    color_discrete_sequence=[colors[0]]
                )
                fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                visuals["type_specific_visuals"].append({
                    "type": "rating_distribution",
                    "column": col,
                    "figure": fig.to_json()
                })
    
    elif data_type == 'demographic':
        # Demographic: pie charts for categorical distributions
        demo_cols = [c for c in categorical_cols if any(kw in c.lower() for kw in ['gender', 'race', 'ethnic', 'location', 'city', 'country'])]
        if demo_cols:
            for col in demo_cols[:3]:
                value_counts = df[col].value_counts().head(8)
                fig = px.pie(
                    values=value_counts.values, 
                    names=value_counts.index,
                    title=f"Distribution of {col.replace('_', ' ').title()}",
                    color_discrete_sequence=colors
                )
                fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                visuals["type_specific_visuals"].append({
                    "type": "demographic_distribution",
                    "column": col,
                    "figure": fig.to_json()
                })
    
    elif data_type == 'financial':
        # Financial: cumulative or stacked charts
        financial_cols = [c for c in numeric_cols if any(kw in c.lower() for kw in ['price', 'cost', 'revenue', 'profit', 'amount'])]
        if financial_cols:
            for col in financial_cols[:3]:
                fig = px.histogram(
                    df, 
                    x=col, 
                    nbins=30,
                    title=f"Distribution of {col.replace('_', ' ').title()}",
                    color_discrete_sequence=[colors[0]]
                )
                fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                visuals["type_specific_visuals"].append({
                    "type": "financial_distribution",
                    "column": col,
                    "figure": fig.to_json()
                })
    
    return visuals


def generate_narrative(df: pd.DataFrame, profile: Dict[str, Any], 
                      target_column: str = None) -> str:
    """
    Generate natural language narrative from data analysis
    
    Args:
        df: Input DataFrame
        profile: Data profile dictionary
        target_column: Optional target column
        
    Returns:
        Natural language narrative string
    """
    narrative_parts = []
    
    # Introduction
    narrative_parts.append(f"This dataset contains {profile['summary']['row_count']:,} rows and "
                          f"{profile['summary']['column_count']} columns, occupying approximately "
                          f"{profile['summary']['memory_usage_mb']:.2f} MB of memory.")
    
    # Data quality assessment
    from app.modules.data_processing import compute_data_quality_score
    quality_score = compute_data_quality_score(df)
    
    if quality_score >= 80:
        narrative_parts.append(f"The dataset demonstrates high data quality (score: {quality_score}/100), "
                              "with minimal missing values and good consistency.")
    elif quality_score >= 50:
        narrative_parts.append(f"The dataset shows moderate data quality (score: {quality_score}/100). "
                              "Some data cleaning may be beneficial to improve analysis results.")
    else:
        narrative_parts.append(f"The dataset has low data quality (score: {quality_score}/100). "
                              "Significant data cleaning is recommended before proceeding with analysis.")
    
    # Missing values summary
    total_missing = sum(profile["missing_values"].values())
    if total_missing > 0:
        missing_pct = (total_missing / (len(df) * len(df.columns))) * 100
        narrative_parts.append(f"Missing values are present in the dataset ({missing_pct:.1f}% of all cells). "
                              f"The columns with the most missing values should be reviewed carefully.")
    else:
        narrative_parts.append("No missing values were detected in the dataset.")
    
    # Duplicates
    if profile["duplicates"]["duplicate_rows"] > 0:
        narrative_parts.append(f"Found {profile['duplicates']['duplicate_rows']} duplicate rows "
                              f"({profile['duplicates']['duplicate_percentage']:.1f}% of the dataset).")
    
    # Column insights
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if numeric_cols:
        narrative_parts.append(f"The dataset contains {len(numeric_cols)} numeric columns, "
                              "which are suitable for statistical analysis and modeling.")
    
    if categorical_cols:
        narrative_parts.append(f"There are {len(categorical_cols)} categorical/text columns, "
                              "which may require encoding for machine learning models.")
    
    # Key statistics for numeric columns
    if numeric_cols and len(numeric_cols) > 0:
        key_col = numeric_cols[0]
        col_info = profile["columns"][key_col]
        if "mean" in col_info and col_info["mean"] is not None:
            narrative_parts.append(f"For the '{key_col}' column, values range from {col_info['min']:.2f} "
                                  f"to {col_info['max']:.2f}, with a mean of {col_info['mean']:.2f} "
                                  f"and standard deviation of {col_info['std']:.2f}.")
    
    # Anomalies and outliers
    if numeric_cols:
        outlier_count = 0
        for col in numeric_cols[:5]:
            if col in profile["columns"]:
                col_info = profile["columns"][col]
                if "mean" in col_info and "std" in col_info and col_info["std"] is not None and col_info["std"] > 0:
                    mean = col_info["mean"]
                    std = col_info["std"]
                    outliers = ((df[col] - mean).abs() > 3 * std).sum()
                    outlier_count += outliers
        
        if outlier_count > 0:
            narrative_parts.append(f"Potential outliers detected: {outlier_count} values exceed 3 standard deviations "
                                  "from the mean. These should be investigated for data quality issues or "
                                  "legitimate extreme cases.")
    
    # Target column insights
    if target_column and target_column in df.columns:
        if target_column in numeric_cols:
            col_info = profile["columns"][target_column]
            narrative_parts.append(f"The target variable '{target_column}' is numeric, suggesting a regression problem. "
                                  f"Its distribution shows a mean of {col_info.get('mean', 'N/A'):.2f} "
                                  f"with {col_info.get('unique_count', 0)} unique values.")
        else:
            col_info = profile["columns"][target_column]
            narrative_parts.append(f"The target variable '{target_column}' is categorical, suggesting a classification problem. "
                                  f"It has {col_info.get('unique_count', 0)} unique classes.")
    
    # Recommendations
    narrative_parts.append("\n### Recommendations:")
    
    if quality_score < 50:
        narrative_parts.append("- Prioritize data cleaning to address missing values and inconsistencies.")
    elif quality_score < 80:
        narrative_parts.append("- Consider minor data cleaning to optimize model performance.")
    
    if profile["duplicates"]["duplicate_rows"] > 0:
        narrative_parts.append("- Remove duplicate rows to ensure data integrity.")
    
    if numeric_cols and categorical_cols:
        narrative_parts.append("- Apply appropriate encoding techniques (one-hot, label encoding) for categorical variables.")
    
    if target_column:
        narrative_parts.append(f"- Proceed with model training using '{target_column}' as the target variable.")
    else:
        narrative_parts.append("- Consider identifying a target variable for supervised learning tasks.")
    
    return "\n\n".join(narrative_parts)


def detect_anomalies(df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect anomalies in the dataset
    
    Args:
        df: Input DataFrame
        profile: Data profile dictionary
        
    Returns:
        List of detected anomalies
    """
    anomalies = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_cols:
        if col in profile["columns"]:
            col_info = profile["columns"][col]
            if "mean" in col_info and "std" in col_info and col_info["std"] is not None and col_info["std"] > 0:
                mean = col_info["mean"]
                std = col_info["std"]
                outliers = df[(df[col] - mean).abs() > 3 * std]
                
                if len(outliers) > 0:
                    anomalies.append({
                        "column": col,
                        "type": "outlier",
                        "count": len(outliers),
                        "severity": "high" if len(outliers) > len(df) * 0.05 else "medium",
                        "description": f"{len(outliers)} values exceed 3 standard deviations from the mean"
                    })
    
    # Check for potential bias indicators
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_cols:
        if col in profile["columns"]:
            col_info = profile["columns"][col]
            if "top_values" in col_info:
                top_values = list(col_info["top_values"].values())
                if len(top_values) > 0:
                    max_count = max(top_values)
                    total = sum(top_values)
                    if max_count / total > 0.9:  # >90% in one category
                        anomalies.append({
                            "column": col,
                            "type": "imbalance",
                            "severity": "medium",
                            "description": f"Severe class imbalance detected: {max_count/total*100:.1f}% of values in one category"
                        })
    
    return anomalies

