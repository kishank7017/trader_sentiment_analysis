# notebooks/02_data_merge_analysis.py
# Data Merging and Analysis

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.project_utils import *
from src.feature import FeatureEngineer

import pandas as pd
import numpy as np
import json

print("\n" + "="*60)
print("  DATA MERGE AND ANALYSIS")
print("="*60)

# ============================================================
# LOAD CLEANED DATA
# ============================================================
print_section("Step 1: Load Cleaned Data")

df_sentiment = load_data('data/processed/fear_greed_index_clean.csv')
df_trades = load_data('data/processed/historical_data_clean.csv')

if df_sentiment is None or df_trades is None:
    print("✗ Please run 01_data_cleaning.py first")
    exit()

# ============================================================
# CREATE FEATURES
# ============================================================
print_section("Step 2: Create Features")

engineer = FeatureEngineer()

# Sentiment features
print("\n► Creating sentiment features...")
df_sentiment = engineer.create_sentiment_features(df_sentiment)
print(f"✓ Sentiment features created: {df_sentiment.shape[1]} columns")

# Trade features
print("\n► Creating trade features...")
df_trades = engineer.create_trader_features(df_trades)
print(f"✓ Trade features created: {df_trades.shape[1]} columns")

# Aggregated metrics
print("\n► Aggregating trader metrics by date...")
df_daily_trades = engineer.aggregate_trader_metrics(df_trades, groupby='Date')
print(f"✓ Aggregated data: {df_daily_trades.shape[0]} days")

# ============================================================
# MERGE DATA
# ============================================================
print_section("Step 3: Merge Sentiment and Trade Data")

# Create date columns for merging
df_sentiment['Date'] = df_sentiment['date'].dt.date
df_daily_trades['Date'] = pd.to_datetime(df_daily_trades['Date']).dt.date

# Merge on date
df_merged = pd.merge(df_sentiment, df_daily_trades, on='Date', how='inner')

print(f"✓ Merged data shape: {df_merged.shape}")
print(f"✓ Overlapping dates: {len(df_merged)} days")

# ============================================================
# ANALYSIS
# ============================================================
print_section("Step 4: Calculate Insights")

insights = {}

# 1. Sentiment Statistics
print("\n► 1. Sentiment Analysis")
sentiment_dist = df_sentiment['classification'].value_counts().to_dict()
insights['sentiment_distribution'] = sentiment_dist
print(f"  Sentiment Distribution: {sentiment_dist}")

# 2. Trading Performance by Sentiment
print("\n► 2. Trading Performance by Sentiment")
perf_by_sentiment = df_merged.groupby('classification').agg({
    'Net PnL': ['sum', 'mean'],
    'PnL Pct': 'mean',
    'Win_Rate': 'mean',
    'Trade_Count': 'sum',
    'Size USD': 'sum'
}).round(2)

insights['performance_by_sentiment'] = perf_by_sentiment.to_dict()
print("\n" + str(perf_by_sentiment))

# 3. Sentiment Level Impact (1-5 scale)
print("\n► 3. Sentiment Level Impact")
sentiment_level_perf = df_merged.groupby('sentiment_level').agg({
    'PnL Pct': 'mean',
    'Win_Rate': 'mean'
}).round(2)

insights['sentiment_level_impact'] = sentiment_level_perf.to_dict()
print("\n" + str(sentiment_level_perf))

# 4. Correlation Analysis
print("\n► 4. Correlation Analysis")
correlation_cols = ['value', 'Net PnL', 'PnL Pct', 'Win_Rate', 'momentum', 'volatility_7d']
available_cols = [col for col in correlation_cols if col in df_merged.columns]

if len(available_cols) > 1:
    correlation = df_merged[available_cols].corr()
    
    # Extract key correlations
    key_correlations = {
        'sentiment_vs_pnl': round(correlation.loc['value', 'PnL Pct'], 3) if 'value' in correlation.index else None,
        'momentum_vs_returns': round(correlation.loc['momentum', 'PnL Pct'], 3) if 'momentum' in correlation.index else None,
        'volatility_vs_returns': round(correlation.loc['volatility_7d', 'PnL Pct'], 3) if 'volatility_7d' in correlation.index else None,
    }
    
    insights['correlations'] = key_correlations
    print("\nKey Correlations:")
    for key, value in key_correlations.items():
        if value is not None:
            print(f"  {key}: {value}")

# 5. Best Trading Periods
print("\n► 5. Best Trading Periods")
best_periods = df_merged.nlargest(5, 'PnL Pct')[['Date', 'classification', 'PnL Pct', 'Win_Rate']]
insights['best_trading_days'] = best_periods.to_dict('records')
print("\nTop 5 Trading Days:")
print(best_periods.to_string(index=False))

# 6. Risk Metrics
print("\n► 6. Risk Metrics")
total_pnl = df_merged['Net PnL'].sum()
total_trades = df_merged['Trade_Count'].sum()
overall_win_rate = df_merged['Is_Profitable'].sum() / total_trades * 100 if total_trades > 0 else 0
total_volume = df_merged['Size USD'].sum()
avg_trade_size = df_merged['Avg_Trade_Size'].mean()

insights['risk_metrics'] = {
    'total_pnl': round(float(total_pnl), 2),
    'total_trades': int(total_trades),
    'overall_win_rate': round(float(overall_win_rate), 2),
    'total_volume': round(float(total_volume), 2),
    'avg_trade_size': round(float(avg_trade_size), 2)
}

print(f"\n  Total PnL: ${total_pnl:.2f}")
print(f"  Total Trades: {int(total_trades)}")
print(f"  Win Rate: {overall_win_rate:.2f}%")
print(f"  Total Volume: ${total_volume:.2f}")
print(f"  Avg Trade Size: ${avg_trade_size:.2f}")

# 7. Strategy Recommendations
print("\n► 7. Strategy Recommendations")
recommendations = []

# Based on correlations
if key_correlations['sentiment_vs_pnl'] > 0.1:
    recommendations.append("Higher sentiment values correlate with better returns - consider bullish strategies in Greed phases")
elif key_correlations['sentiment_vs_pnl'] < -0.1:
    recommendations.append("Lower sentiment values correlate with better returns - consider contrarian strategies in Fear phases")
else:
    recommendations.append("Sentiment alone is not a strong predictor - combine with other indicators")



df_daily_trades = engineer.aggregate_trader_metrics(df_trades, groupby='Date')
print(df_trades.shape)
print(df_trades.head())

print(df_daily_trades.shape)
print(df_daily_trades.head())


# Based on performance by sentiment
best_sentiment = df_merged.groupby('classification')['PnL Pct'].mean().idxmax()
worst_sentiment = df_merged.groupby('classification')['PnL Pct'].mean().idxmin()
recommendations.append(f"Best performing sentiment: {best_sentiment}")
recommendations.append(f"Worst performing sentiment: {worst_sentiment}")

# Based on win rate
avg_wr = df_merged['Win_Rate'].mean()
if avg_wr < 50:
    recommendations.append("Win rate below 50% - focus on larger wins to maintain profitability")
else:
    recommendations.append("Solid win rate above 50% - maintain current strategy discipline")

insights['strategy_recommendations'] = recommendations

print("\nRecommendations:")
for i, rec in enumerate(recommendations, 1):
    print(f"  {i}. {rec}")

# ============================================================
# SAVE OUTPUTS
# ============================================================
print_section("Step 5: Save Analysis Results")

# Save merged data
save_data(df_merged, 'data/processed/merged_data.csv')

# Save insights as JSON
save_insights(insights, 'output/insights.json')

# ============================================================
# SUMMARY
# ============================================================
print_section("Analysis Complete")

print("\n✓ Files Saved:")
print("  - data/processed/merged_data.csv")
print("  - output/insights.json")

print("\n✓ Analysis Summary:")
print(f"  - Analyzed {len(df_merged)} trading days")
print(f"  - Total trades analyzed: {int(total_trades)}")
print(f"  - Generated {len(insights)} insight categories")

print("\n✓ Next Step: Open web/index.html in browser to view dashboard")
print("="*60 + "\n")