# notebooks/01_data_cleaning.py
# Data Cleaning and Preparation

import sys



from pathlib import Path

# Add the project root to Python's search path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.project_utils import *

import pandas as pd
import numpy as np

print("\n" + "="*60)
print("  DATA CLEANING AND PREPARATION")
print("="*60)



# Create directories
create_directories()

# ============================================================
# LOAD RAW DATA
# ============================================================
print_section("Step 1: Load Raw Data")

df_fear_greed = load_data('data/raw/fear_greed_index.csv')
df_trades = load_data('data/raw/historical_data.csv')

# Check if data loaded successfully
if df_fear_greed is None or df_trades is None:
    print("✗ Error loading data. Please check file paths.")
    exit()

# ============================================================
# EXPLORE DATA
# ============================================================
print_section("Step 2: Explore Data")

print("\nFear & Greed Index:")
print(f"  Shape: {df_fear_greed.shape}")
print(f"  Columns: {df_fear_greed.columns.tolist()}")
print(f"  Data types:\n{df_fear_greed.dtypes}")

print("\nTrader Data:")
print(f"  Shape: {df_trades.shape}")
print(f"  Columns: {df_trades.columns.tolist()}")

# ============================================================
# CLEAN FEAR & GREED DATA
# ============================================================
print_section("Step 3: Clean Fear & Greed Data")

# Check missing values
check_missing_values(df_fear_greed, "Fear & Greed Index")

# Remove duplicates
df_fear_greed = remove_duplicates(df_fear_greed, subset=['date'])

# Ensure proper data types
df_fear_greed['timestamp'] = pd.to_numeric(df_fear_greed['timestamp'], errors='coerce')
df_fear_greed['value'] = pd.to_numeric(df_fear_greed['value'], errors='coerce')
df_fear_greed['date'] = pd.to_datetime(df_fear_greed['date'], errors='coerce')

# Remove rows with invalid data
df_fear_greed = df_fear_greed.dropna(subset=['value', 'date'])

# Sort by date
df_fear_greed = df_fear_greed.sort_values('date').reset_index(drop=True)

print(f"✓ Clean shape: {df_fear_greed.shape}")
print(f"✓ Date range: {df_fear_greed['date'].min()} to {df_fear_greed['date'].max()}")

# ============================================================
# CLEAN TRADER DATA
# ============================================================
print_section("Step 4: Clean Trader Data")

# Check missing values
check_missing_values(df_trades, "Trader Data")

# Remove duplicates
df_trades = remove_duplicates(df_trades, subset=['Trade ID'])

# Convert important columns to numeric
numeric_cols = ['Execution Price', 'Size Tokens', 'Size USD', 'Closed PnL', 'Fee']
for col in numeric_cols:
    df_trades[col] = pd.to_numeric(df_trades[col], errors='coerce')

# Remove rows with critical missing values
df_trades = df_trades.dropna(subset=['Execution Price', 'Size USD'])

# Parse timestamp
df_trades['Timestamp IST'] = pd.to_datetime(df_trades['Timestamp IST'], 
                                            format='%d-%m-%Y %H:%M', 
                                            errors='coerce')

# Remove rows with invalid timestamps
df_trades = df_trades.dropna(subset=['Timestamp IST'])

# Sort by timestamp
df_trades = df_trades.sort_values('Timestamp IST').reset_index(drop=True)

print(f"✓ Clean shape: {df_trades.shape}")
print(f"✓ Date range: {df_trades['Timestamp IST'].min()} to {df_trades['Timestamp IST'].max()}")
print(f"✓ Unique accounts: {df_trades['Account'].nunique()}")

# ============================================================
# DATA QUALITY CHECKS
# ============================================================
print_section("Step 5: Data Quality Checks")

# Check value ranges
print("\nFear & Greed Index Value Range:")
print(f"  Min: {df_fear_greed['value'].min()}")
print(f"  Max: {df_fear_greed['value'].max()}")
print(f"  Mean: {df_fear_greed['value'].mean():.2f}")

print("\nTrade Size Range (USD):")
print(f"  Min: ${df_trades['Size USD'].min():.2f}")
print(f"  Max: ${df_trades['Size USD'].max():.2f}")
print(f"  Mean: ${df_trades['Size USD'].mean():.2f}")

# ============================================================
# SAVE CLEANED DATA
# ============================================================
print_section("Step 6: Save Cleaned Data")

save_data(df_fear_greed, 'data/processed/fear_greed_index_clean.csv')
save_data(df_trades, 'data/processed/historical_data_clean.csv')

# ============================================================
# SUMMARY
# ============================================================
print_section("Cleaning Summary")

print("\n✓ Fear & Greed Data:")
print(f"  - {df_fear_greed.shape[0]} records cleaned")
print(f"  - Date range: {(df_fear_greed['date'].max() - df_fear_greed['date'].min()).days} days")

print("\n✓ Trader Data:")
print(f"  - {df_trades.shape[0]} trades cleaned")
print(f"  - Total value traded: ${df_trades['Size USD'].sum():.2f}")
print(f"  - Average trade size: ${df_trades['Size USD'].mean():.2f}")

print("\n✓ All cleaned data saved to data/processed/")
print("\nNext: Run 02_data_merge_analysis.py")
print("="*60 + "\n")