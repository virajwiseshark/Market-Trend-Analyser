# Market Trend Analyzer

This is a Streamlit app that fetches market data from multiple sources, computes common technical indicators (SMA, EMA, RSI, MACD), runs a simple MA crossover backtest, and displays interactive charts.

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
