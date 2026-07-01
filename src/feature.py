# src/feature.py
# Feature engineering for trader sentiment analysis

import pandas as pd
import numpy as np
from datetime import datetime


class FeatureEngineer:
    """Class to create features from raw data"""
    
    def __init__(self):
        """Initialize feature engineer"""
        pass
    
    def create_sentiment_features(self, df_sentiment):
        """
        Create additional features from sentiment data
        
        Parameters:
        df_sentiment (DataFrame): Fear & Greed index data
        
        Returns:
        DataFrame: Data with new features
        """
        df = df_sentiment.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Create sentiment level (numerical)
        sentiment_mapping = {
            'Extreme Fear': 1,
            'Fear': 2,
            'Neutral': 3,
            'Greed': 4,
            'Extreme Greed': 5
        }
        df['sentiment_level'] = df['classification'].map(sentiment_mapping)
        
        # Create sentiment change (day-to-day)
        df['value_change'] = df['value'].diff()
        df['sentiment_change_pct'] = df['value'].pct_change() * 100
        
        # Create rolling averages
        df['value_ma7'] = df['value'].rolling(window=7, min_periods=1).mean()
        df['value_ma30'] = df['value'].rolling(window=30, min_periods=1).mean()
        
        # Create volatility (7-day rolling std)
        df['volatility_7d'] = df['value'].rolling(window=7, min_periods=1).std()
        
        # Create momentum indicator
        df['momentum'] = df['value'] - df['value_ma7']
        
        # Extract time features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        
        return df
    
    def create_trader_features(self, df_trades):
        """
        Create features from trader data
        
        Parameters:
        df_trades (DataFrame): Historical trade data
        
        Returns:
        DataFrame: Data with new features
        """
        df = df_trades.copy()
        
        # Ensure numeric columns
        df['Execution Price'] = pd.to_numeric(df['Execution Price'], errors='coerce')
        df['Size USD'] = pd.to_numeric(df['Size USD'], errors='coerce')
        df['Closed PnL'] = pd.to_numeric(df['Closed PnL'], errors='coerce')
        df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce')
        
        # Create PnL after fee
        df['Net PnL'] = df['Closed PnL'] - df['Fee']
        
        # Create PnL percentage
        df['PnL Pct'] = (df['Net PnL'] / df['Size USD']) * 100
        
        # Create trade type (BUY/SELL indicator)
        df['Is_Long'] = (df['Side'] == 'BUY').astype(int)
        
        # Create profit indicator
        df['Is_Profitable'] = (df['Net PnL'] > 0).astype(int)
        


        # Parse timestamp
        # Show original values
        print("\n===== BEFORE CONVERSION =====")
        print(df["Timestamp IST"].head(10))

        # Convert timestamps
        df["Timestamp IST"] = pd.to_datetime(
            df["Timestamp IST"],
            errors="coerce"
        )

        # Show converted values
        print("\n===== AFTER CONVERSION =====")
        print(df["Timestamp IST"].head(10))
        print("NaT count:", df["Timestamp IST"].isna().sum())




        df['Date'] = df['Timestamp IST'].dt.date
        
        # Extract time features
        df['Hour'] = df['Timestamp IST'].dt.hour
        df['Day_of_Week'] = df['Timestamp IST'].dt.dayofweek
        
        return df
    
    def aggregate_trader_metrics(self, df_trades, groupby='Date'):
        """
        Aggregate trader metrics by date or account
        
        Parameters:
        df_trades (DataFrame): Trade data with engineered features
        groupby (str): Column to group by
        
        Returns:
        DataFrame: Aggregated metrics
        """
        agg_dict = {
            'Size USD': 'sum',
            'Net PnL': 'sum',
            'PnL Pct': 'mean',
            'Is_Profitable': 'sum',
            'Account': 'count'
        }
        
        aggregated = df_trades.groupby(groupby).agg(agg_dict).reset_index()
        
        # Rename columns for clarity
        aggregated.rename(columns={'Account': 'Trade_Count'}, inplace=True)
        
        # Create win rate
        aggregated['Win_Rate'] = (aggregated['Is_Profitable'] / aggregated['Trade_Count']) * 100
        
        # Create average trade size
        aggregated['Avg_Trade_Size'] = aggregated['Size USD'] / aggregated['Trade_Count']
        
        # Create total PnL percentage
        aggregated['Total_PnL_Pct'] = (aggregated['Net PnL'] / aggregated['Size USD']) * 100
        
        return aggregated
    
    def create_merged_features(self, df_merged):
        """
        Create features from merged sentiment and trade data
        
        Parameters:
        df_merged (DataFrame): Merged sentiment and trade data
        
        Returns:
        DataFrame: Data with interaction features
        """
        df = df_merged.copy()
        
        # Create sentiment-performance interaction
        df['Greed_Trade'] = (df['classification'] == 'Greed').astype(int) * df['PnL Pct']
        df['Fear_Trade'] = (df['classification'] == 'Fear').astype(int) * df['PnL Pct']
        
        # Create sentiment momentum
        df['Sentiment_Momentum'] = df['momentum'].fillna(0) * df['PnL Pct']
        
        # Create volatility adjusted return
        df['Vol_Adj_PnL'] = df['PnL Pct'] / (df['volatility_7d'] + 1)
        
        return df


# Example usage function
def create_all_features(df_sentiment, df_trades):
    """
    Create all features from raw data
    
    Parameters:
    df_sentiment (DataFrame): Sentiment data
    df_trades (DataFrame): Trade data
    
    Returns:
    tuple: (sentiment_features, trade_features, aggregated_trades)
    """
    engineer = FeatureEngineer()
    
    # Create features
    df_sentiment_features = engineer.create_sentiment_features(df_sentiment)
    df_trades_features = engineer.create_trader_features(df_trades)
    df_aggregated = engineer.aggregate_trader_metrics(df_trades_features)
    
    return df_sentiment_features, df_trades_features, df_aggregated


if __name__ == "__main__":
    print("Feature engineering module loaded")