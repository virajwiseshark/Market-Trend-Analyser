# Streamlit Market Trend Analyzer

A simple Streamlit app to analyze stock/crypto market trends with common indicators (SMA, EMA, RSI, MACD), 
a basic moving-average crossover backtest, and interactive charts.

## Quickstart

```bash
# 1) Create & activate a virtualenv (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
streamlit run app.py
```

## Features
- Ticker lookup via Yahoo Finance (yfinance)
- Date range and interval selection
- SMA/EMA overlays
- RSI & MACD indicator panels
- Simple MA crossover backtest (fast vs slow)
- Metrics: CAGR (approx), Max Drawdown, Win Rate, Sharpe (naive)
- Export signals & equity curve as CSV

> Note: This app is for educational purposes only and not financial advice.
