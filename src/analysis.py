# src/analysis.py
# Analysis functions for trader sentiment data

import pandas as pd
import numpy as np


class SentimentAnalysis:
    """Analyze relationship between sentiment and trading performance"""
    
    def __init__(self, merged_data):
        """
        Initialize with merged data
        
        Parameters:
        merged_data (DataFrame): Merged sentiment and trade data
        """
        self.df = merged_data.copy()
    
    def get_sentiment_distribution(self):
        """Get distribution of sentiment classifications"""
        return self.df['classification'].value_counts().to_dict()
    
    def get_performance_by_sentiment(self):
        """
        Calculate trading performance for each sentiment level
        
        Returns:
        dict: Performance metrics by sentiment
        """
        result = {}
        
        for sentiment in self.df['classification'].unique():
            data = self.df[self.df['classification'] == sentiment]
            
            result[sentiment] = {
                'avg_pnl_pct': round(data['PnL Pct'].mean(), 2),
                'total_pnl': round(data['Net PnL'].sum(), 2),
                'win_rate': round(data['Win_Rate'].mean(), 2),
                'trade_count': int(data['Trade_Count'].sum()),
                'volume': round(data['Size USD'].sum(), 2)
            }
        
        return result
    
    def get_correlation_analysis(self):
        """
        Analyze correlation between sentiment and performance
        
        Returns:
        dict: Key correlations
        """
        correlations = {}
        
        # Sentiment value vs PnL %
        if 'value' in self.df.columns and 'PnL Pct' in self.df.columns:
            corr = self.df['value'].corr(self.df['PnL Pct'])
            correlations['sentiment_value_vs_pnl'] = round(float(corr), 3)
        
        # Momentum vs Returns
        if 'momentum' in self.df.columns and 'PnL Pct' in self.df.columns:
            corr = self.df['momentum'].corr(self.df['PnL Pct'])
            correlations['momentum_vs_returns'] = round(float(corr), 3)
        
        # Volatility vs Returns
        if 'volatility_7d' in self.df.columns and 'PnL Pct' in self.df.columns:
            corr = self.df['volatility_7d'].corr(self.df['PnL Pct'])
            correlations['volatility_vs_returns'] = round(float(corr), 3)
        
        return correlations
    
    def get_risk_metrics(self):
        """
        Calculate overall risk and performance metrics
        
        Returns:
        dict: Risk metrics
        """
        total_pnl = self.df['Net PnL'].sum()
        total_trades = self.df['Trade_Count'].sum()
        total_volume = self.df['Size USD'].sum()
        
        # Calculate win rate
        if 'Is_Profitable' in self.df.columns:
            win_rate = (self.df['Is_Profitable'].sum() / total_trades * 100) if total_trades > 0 else 0
        else:
            win_rate = (self.df['PnL Pct'] > 0).sum() / len(self.df) * 100
        
        return {
            'total_pnl': round(float(total_pnl), 2),
            'total_trades': int(total_trades),
            'win_rate': round(float(win_rate), 2),
            'total_volume': round(float(total_volume), 2),
            'avg_trade_size': round(float(self.df['Avg_Trade_Size'].mean()), 2),
            'sharpe_ratio': round(float(self._calculate_sharpe()), 3)
        }
    
    def _calculate_sharpe(self, risk_free_rate=0.02):
        """
        Calculate Sharpe Ratio
        
        Parameters:
        risk_free_rate (float): Annual risk-free rate
        
        Returns:
        float: Sharpe Ratio
        """
        returns = self.df['PnL Pct'].values
        excess_return = returns.mean() - (risk_free_rate / 252)  # Daily rate
        volatility = returns.std()
        
        if volatility == 0:
            return 0
        
        return (excess_return / volatility) * np.sqrt(252)
    
    def get_best_trading_conditions(self, top_n=5):
        """
        Identify best trading conditions
        
        Parameters:
        top_n (int): Number of top days to return
        
        Returns:
        list: Top trading days with conditions
        """
        if len(self.df) == 0:
            return []
        
        top_days = self.df.nlargest(top_n, 'PnL Pct')[
            ['Date', 'classification', 'value', 'PnL Pct', 'Win_Rate']
        ]
        
        return top_days.to_dict('records')
    
    def get_strategy_recommendations(self):
        """
        Generate trading strategy recommendations based on analysis
        
        Returns:
        list: Recommended strategies
        """
        recommendations = []
        
        # Analyze sentiment performance
        perf_by_sentiment = self.get_performance_by_sentiment()
        best_sentiment = max(perf_by_sentiment, key=lambda x: perf_by_sentiment[x]['avg_pnl_pct'])
        worst_sentiment = min(perf_by_sentiment, key=lambda x: perf_by_sentiment[x]['avg_pnl_pct'])
        
        recommendations.append({
            'title': 'Best Sentiment Environment',
            'description': f'Trading performance is highest during {best_sentiment} sentiment',
            'action': f'Increase position sizing and take more trades during {best_sentiment} phases'
        })
        
        recommendations.append({
            'title': 'Worst Sentiment Environment',
            'description': f'Trading performance is lowest during {worst_sentiment} sentiment',
            'action': f'Reduce risk or avoid trading during {worst_sentiment} phases'
        })
        
        # Win rate analysis
        win_rate = self.get_risk_metrics()['win_rate']
        if win_rate < 45:
            recommendations.append({
                'title': 'Low Win Rate',
                'description': f'Current win rate is {win_rate:.1f}%, below 50% threshold',
                'action': 'Focus on trade quality over quantity; improve entry/exit criteria'
            })
        else:
            recommendations.append({
                'title': 'Solid Win Rate',
                'description': f'Current win rate is {win_rate:.1f}%, above 50% threshold',
                'action': 'Maintain discipline; consider slightly increasing position size'
            })
        
        # Volatility strategy
        if 'volatility_7d' in self.df.columns:
            high_vol_perf = self.df[self.df['volatility_7d'] > self.df['volatility_7d'].median()]['PnL Pct'].mean()
            low_vol_perf = self.df[self.df['volatility_7d'] <= self.df['volatility_7d'].median()]['PnL Pct'].mean()
            
            if high_vol_perf > low_vol_perf:
                recommendations.append({
                    'title': 'High Volatility Strategy',
                    'description': 'Trading performance is better during high volatility periods',
                    'action': 'Increase activity and position size during volatile market conditions'
                })
            else:
                recommendations.append({
                    'title': 'Low Volatility Strategy',
                    'description': 'Trading performance is better during calm market conditions',
                    'action': 'Focus on trading during periods of lower market volatility'
                })
        
        return recommendations
    
    def get_summary_stats(self):
        """
        Get comprehensive summary statistics
        
        Returns:
        dict: Complete summary
        """
        return {
            'total_days_analyzed': len(self.df),
            'date_range': {
                'start': str(self.df['Date'].min()) if 'Date' in self.df.columns else 'N/A',
                'end': str(self.df['Date'].max()) if 'Date' in self.df.columns else 'N/A'
            },
            'sentiment_distribution': self.get_sentiment_distribution(),
            'performance_by_sentiment': self.get_performance_by_sentiment(),
            'correlations': self.get_correlation_analysis(),
            'risk_metrics': self.get_risk_metrics(),
            'best_conditions': self.get_best_trading_conditions(),
            'recommendations': self.get_strategy_recommendations()
        }


if __name__ == "__main__":
    print("Analysis module loaded successfully")