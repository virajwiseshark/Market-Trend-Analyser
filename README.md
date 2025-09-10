# Market Trend Analyzer

This is a Streamlit app that fetches market data from multiple sources, computes common technical indicators (SMA, EMA, RSI, MACD), runs a simple MA crossover backtest, and displays interactive charts.


# 📈 Market Trend Analyzer

An interactive financial analysis and backtesting tool built with **Python, Streamlit, and Plotly**.  
It supports **multi-stock analysis** (US & Indian markets), technical indicators, backtesting, and now **AI-powered predictions**.

---

## 🚀 Features
- Multi-stock support (e.g., `AAPL`, `RELIANCE.NS`, `TATAPOWER.NS`)
- Data sources:
  - Yahoo Finance (default, no API key required)
  - Alpha Vantage (requires API key)
  - Polygon.io (requires API key)
  - Finnhub (requires API key)
- Technical Indicators:
  - Simple Moving Average (SMA)
  - Exponential Moving Average (EMA)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
- Backtesting:
  - Moving Average Crossover strategy
  - Metrics: CAGR, Max Drawdown, Win Rate, Sharpe Ratio
- **AI Predictions (New!)**
  - LSTM (Long Short-Term Memory)
  - Transformer (self-attention model)
  - Linear Regression (baseline ML)
  - Random Forest (baseline ML)
- Dark mode with neon-style charts

---

## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/virajwiseshark/Market-Trend-Analyser.git
cd Market-Trend-Analyser


## Setup

1. Create a virtual environment (recommended)
   ```
   python -m venv .venv
   source .venv/bin/activate  # mac/linux
   .venv\Scripts\activate   # windows
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. (Optional) Add API keys to `.streamlit/secrets.toml`:
   ```
   [api_keys]
   alpha = "YOUR_ALPHA_VANTAGE_KEY"
   polygon = "YOUR_POLYGON_KEY"
   finnhub = "YOUR_FINNHUB_KEY"
   ```

4. Run the app
   ```
   streamlit run app.py
   ```

## Project structure
See the repository tree for modularized code: `data_sources`, `indicators`, `backtest`, `utils`, `config`.
