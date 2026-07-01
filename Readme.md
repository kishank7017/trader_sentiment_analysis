# Trader Sentiment Analysis - Trading Strategy Insights

## Overview
This project analyzes the relationship between Bitcoin market sentiment (Fear/Greed Index) and trader performance on Hyperliquid. The goal is to uncover patterns and derive actionable trading strategies based on sentiment analysis.

## Project Structure
```
TRADER_SENTIMENT_ANALYSIS/
├── data/
│   ├── raw/
│   │   ├── fear_greed_index.csv
│   │   └── historical_data.csv
│   └── processed/
│       ├── fear_greed_index_clean.csv
│       ├── historical_data_clean.csv
│       └── merged_data.csv
│
├── src/
│   ├── feature.py
│   ├── analysis.py
│   └── utils.py
│
├── notebooks/
│   ├── 01_data_cleaning.py
│   └── 02_data_merge_analysis.py
│
├── output/
│   ├── figures/
│   ├── reports/
│   └── insights.json
│
├── web/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Data
- Place `fear_greed_index.csv` in `data/raw/`
- Place `historical_data.csv` in `data/raw/`

### 4. Run Analysis
```bash
python notebooks/01_data_cleaning.py
python notebooks/02_data_merge_analysis.py
```

### 5. View Results
Open `web/index.html` in your browser to see insights and trading strategies.

## Key Features

### Data Cleaning
- Handle missing values
- Remove duplicates
- Normalize timestamps
- Data validation checks

### Feature Engineering
- Calculate trader performance metrics
- Create sentiment-based features
- Time-based aggregations
- Performance indicators

### Analysis
- Correlation between sentiment and returns
- Trader behavior patterns
- Sentiment-based trading opportunities
- Risk-adjusted performance metrics

### Insights Dashboard
- Interactive visualizations
- Key metrics and KPIs
- Trading strategy recommendations
- Performance statistics

## Datasets

### Bitcoin Fear & Greed Index
- **Source**: Fear & Greed Index
- **Columns**: timestamp, value, classification, date
- **Time Range**: 2018 - Present
- **Classifications**: Extreme Fear, Fear, Neutral, Greed, Extreme Greed

### Historical Trader Data (Hyperliquid)
- **Source**: Hyperliquid Exchange
- **Columns**: Account, Coin, Execution Price, Size, Side, Timestamp, PnL, etc.
- **Data**: Trading transactions with performance metrics

## Key Insights to Discover

1. **Sentiment-Performance Correlation**: How does market sentiment affect trader returns?
2. **Trader Behavior**: Do traders perform better in fear or greed markets?
3. **Timing Opportunity**: Best entry/exit opportunities based on sentiment
4. **Risk Patterns**: Risk exposure during different sentiment phases
5. **Strategy Recommendations**: Data-driven trading strategies

## Output Files

- `merged_data.csv`: Combined sentiment and trader data
- `insights.json`: Key metrics and statistics
- `figures/`: Charts and visualizations
- `index.html`: Interactive dashboard

## Technologies Used
- **Python**: Data processing and analysis
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Matplotlib/Seaborn**: Visualization
- **HTML/CSS/JavaScript**: Interactive dashboard

## Author Notes
This project is designed to be clean, minimal, and easy to understand. All code uses basic concepts and clear comments for easy modification and learning.