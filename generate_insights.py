# generate_insights.py
# Main script to generate all insights and prepare data for web dashboard

import sys
sys.path.insert(0, 'src')

import pandas as pd
import json
from project_utils import load_data, save_insights, print_section
from analysis import SentimentAnalysis
from feature import FeatureEngineer

print("\n" + "="*60)
print("  GENERATING INSIGHTS FOR DASHBOARD")
print("="*60)

# ============================================================
# LOAD DATA
# ============================================================
print_section("Step 1: Load Data")

# Try to load merged data first
try:
    df = pd.read_csv('data/processed/merged_data.csv')
    print("✓ Loaded merged data")
except:
    # If not available, load raw and process
    print("⚠ Merged data not found, processing raw data...")
    
    try:
        df_sentiment = pd.read_csv('data/processed/fear_greed_index_clean.csv')
        df_trades = pd.read_csv('data/processed/historical_data_clean.csv')
        
        engineer = FeatureEngineer()
        df_sentiment = engineer.create_sentiment_features(df_sentiment)
        df_trades = engineer.create_trader_features(df_trades)
        df_daily = engineer.aggregate_trader_metrics(df_trades)
        
        df_sentiment['Date'] = pd.to_datetime(df_sentiment['date']).dt.date
        df_daily['Date'] = pd.to_datetime(df_daily['Date']).dt.date
        
        df = pd.merge(df_sentiment, df_daily, on='Date', how='inner')
        print("✓ Processed and merged data")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please run 01_data_cleaning.py and 02_data_merge_analysis.py first")
        exit()

# ============================================================
# GENERATE INSIGHTS
# ============================================================
print_section("Step 2: Generate Insights")

analyzer = SentimentAnalysis(df)

print("\n► Running comprehensive analysis...")
all_insights = analyzer.get_summary_stats()
print("✓ Analysis complete")

# ============================================================
# GENERATE SAMPLE DATA FOR CHARTS
# ============================================================
print_section("Step 3: Prepare Chart Data")

# Sentiment trend over time
print("\n► Preparing sentiment trend data...")
sentiment_trend = df.groupby('Date').agg({
    'value': 'first',
    'PnL Pct': 'mean',
    'Win_Rate': 'mean',
    'Trade_Count': 'sum'
}).reset_index()

sentiment_trend['Date'] = sentiment_trend['Date'].astype(str)
sentiment_trend = sentiment_trend.round(2)

all_insights['sentiment_trend'] = sentiment_trend.to_dict('records')

# Performance distribution
print("► Preparing performance distribution...")
pnl_pct_data = df['PnL Pct'].dropna()
all_insights['performance_distribution'] = {
    'min': round(float(pnl_pct_data.min()), 2),
    'max': round(float(pnl_pct_data.max()), 2),
    'mean': round(float(pnl_pct_data.mean()), 2),
    'median': round(float(pnl_pct_data.median()), 2),
    'std_dev': round(float(pnl_pct_data.std()), 2)
}

# Monthly performance
print("► Preparing monthly performance...")
df['Date_obj'] = pd.to_datetime(df['Date'])
df['Year_Month'] = df['Date_obj'].dt.to_period('M').astype(str)

monthly_perf = df.groupby('Year_Month').agg({
    'Net PnL': 'sum',
    'Win_Rate': 'mean',
    'Trade_Count': 'sum'
}).reset_index()

monthly_perf.columns = ['Period', 'Total_PnL', 'Avg_Win_Rate', 'Trade_Count']
monthly_perf = monthly_perf.round(2)

all_insights['monthly_performance'] = monthly_perf.to_dict('records')

print("✓ Chart data prepared")

# ============================================================
# CREATE DASHBOARD DATA
# ============================================================
print_section("Step 4: Create Dashboard Data")

dashboard_data = {
    'metadata': {
        'generated_at': pd.Timestamp.now().isoformat(),
        'total_records': len(df),
        'total_days': len(df['Date'].unique()) if 'Date' in df.columns else 0
    },
    'insights': all_insights
}

print("✓ Dashboard data compiled")

# ============================================================
# SAVE INSIGHTS
# ============================================================
print_section("Step 5: Save Insights")

# Save to JSON for web dashboard
try:
    with open('output/insights.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    print("✓ Saved to output/insights.json")
except Exception as e:
    print(f"✗ Error saving insights: {e}")

# Also save as CSV for reference
try:
    df.to_csv('output/merged_data_with_insights.csv', index=False)
    print("✓ Saved to output/merged_data_with_insights.csv")
except Exception as e:
    print(f"✗ Error saving CSV: {e}")

# ============================================================
# SUMMARY
# ============================================================
print_section("Insights Generation Complete")

print(f"\n✓ Insights Summary:")
print(f"  - Total days analyzed: {dashboard_data['metadata']['total_days']}")
print(f"  - Total records processed: {dashboard_data['metadata']['total_records']}")
print(f"  - Insights generated: {len(all_insights)} categories")

print(f"\n✓ Files Created:")
print(f"  - output/insights.json")
print(f"  - output/merged_data_with_insights.csv")

print(f"\n✓ Next Step: Open web/index.html in your browser")
print("="*60 + "\n")