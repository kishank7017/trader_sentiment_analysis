# src/utils.py
# Utility functions for data processing and analysis

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os


def create_directories():
    """Create necessary project directories if they don't exist"""
    directories = [
        'data/raw',
        'data/processed',
        'output/figures',
        'output/reports',
        'notebooks'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Directories created successfully")


def load_data(filepath):
    """
    Load CSV file with error handling
    
    Parameters:
    filepath (str): Path to CSV file
    
    Returns:
    DataFrame: Loaded data
    """
    try:
        data = pd.read_csv(filepath)
        print(f"✓ Loaded {filepath} - Shape: {data.shape}")
        return data
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return None
    except Exception as e:
        print(f"✗ Error loading {filepath}: {str(e)}")
        return None


def save_data(dataframe, filepath):
    """
    Save dataframe to CSV
    
    Parameters:
    dataframe (DataFrame): Data to save
    filepath (str): Path where to save
    """
    try:
        dataframe.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath}")
    except Exception as e:
        print(f"✗ Error saving {filepath}: {str(e)}")


def check_missing_values(dataframe, name="Dataset"):
    """
    Check and report missing values in dataframe
    
    Parameters:
    dataframe (DataFrame): Data to check
    name (str): Dataset name for reporting
    """
    missing = dataframe.isnull().sum()
    if missing.sum() == 0:
        print(f"✓ {name}: No missing values")
    else:
        print(f"⚠ {name} Missing Values:")
        print(missing[missing > 0])
    
    return missing


def remove_duplicates(dataframe, subset=None):
    """
    Remove duplicate rows
    
    Parameters:
    dataframe (DataFrame): Data to clean
    subset (list): Columns to consider for duplicates
    
    Returns:
    DataFrame: Data without duplicates
    """
    initial_shape = dataframe.shape[0]
    dataframe = dataframe.drop_duplicates(subset=subset)
    removed = initial_shape - dataframe.shape[0]
    
    if removed > 0:
        print(f"✓ Removed {removed} duplicate rows")
    
    return dataframe


def get_summary_stats(dataframe):
    """
    Get summary statistics of dataframe
    
    Parameters:
    dataframe (DataFrame): Data to analyze
    
    Returns:
    dict: Summary statistics
    """
    summary = {
        'total_rows': len(dataframe),
        'total_columns': len(dataframe.columns),
        'memory_usage': dataframe.memory_usage(deep=True).sum() / 1024**2,  # MB
        'columns': dataframe.columns.tolist(),
        'dtypes': dataframe.dtypes.to_dict()
    }
    
    return summary


def save_insights(insights_dict, filepath):
    """
    Save insights dictionary as JSON
    
    Parameters:
    insights_dict (dict): Insights to save
    filepath (str): Path where to save
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(insights_dict, f, indent=2, default=str)
        print(f"✓ Insights saved to {filepath}")
    except Exception as e:
        print(f"✗ Error saving insights: {str(e)}")


def load_insights(filepath):
    """
    Load insights from JSON file
    
    Parameters:
    filepath (str): Path to JSON file
    
    Returns:
    dict: Loaded insights
    """
    try:
        with open(filepath, 'r') as f:
            insights = json.load(f)
        print(f"✓ Loaded insights from {filepath}")
        return insights
    except FileNotFoundError:
        print(f"✗ Insights file not found: {filepath}")
        return {}
    except Exception as e:
        print(f"✗ Error loading insights: {str(e)}")
        return {}


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)


# Example usage
if __name__ == "__main__":
    print("Utility module loaded successfully")