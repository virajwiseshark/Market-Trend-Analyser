import streamlit as st
import pandas as pd
from datetime import date, timedelta
from config.settings import DEFAULT_INTERVAL, DEFAULT_START_DAYS
from indicators.technicals import compute_indicators
from backtest.strategies import run_crossover, compute_metrics
from data_sources import yahoo, alpha_vantage, polygon, finnhub
from utils.plotting import plot_price, plot_rsi, plot_macd, plot_equity

# Import AI models
from ml_models.lstm_model import train_lstm, predict_future_lstm
from ml_models.transformer_model import train_transformer
from ml_models.baseline_models import train_linear_regression, train_random_forest

st.set_page_config(page_title="Market Trend Analyzer", layout="wide")
st.sidebar.title("Market Trend Analyzer")

# --- Sidebar: data source & basic inputs ---
source = st.sidebar.selectbox("Data Source", ["Yahoo Finance", "Alpha Vantage", "Polygon (placeholder)", "Finnhub (placeholder)"])
tickers_input = st.sidebar.text_input("Tickers (comma-separated)", "AAPL, RELIANCE.NS")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

col1, col2 = st.sidebar.columns(2)
start = col1.date_input("Start", value=date.today() - timedelta(days=DEFAULT_START_DAYS))
end = col2.date_input("End", value=date.today())
interval = st.sidebar.selectbox("Interval", DEFAULT_INTERVAL, index=0)

# --- AI Predictions block moved above Indicators ---
st.sidebar.subheader("AI Predictions")
ai_model_choice = st.sidebar.selectbox("Choose AI Model", ["None", "LSTM", "Transformer", "Linear Regression", "Random Forest"])

st.sidebar.markdown('---')
st.sidebar.subheader("Indicators")
sma_window = st.sidebar.number_input("SMA window", min_value=2, max_value=400, value=20, step=1)
ema_window = st.sidebar.number_input("EMA window", min_value=2, max_value=400, value=50, step=1)
rsi_window = st.sidebar.number_input("RSI window", min_value=2, max_value=100, value=14, step=1)
macd_fast = st.sidebar.number_input("MACD fast", min_value=2, max_value=100, value=12, step=1)
macd_slow = st.sidebar.number_input("MACD slow", min_value=2, max_value=200, value=26, step=1)
macd_signal = st.sidebar.number_input("MACD signal", min_value=2, max_value=50, value=9, step=1)

st.sidebar.markdown('---')
st.sidebar.subheader("Backtest (MA Crossover)")
fast_ma = st.sidebar.number_input("Fast MA", min_value=2, max_value=200, value=10, step=1)
slow_ma = st.sidebar.number_input("Slow MA", min_value=2, max_value=400, value=30, step=1)
initial_capital = st.sidebar.number_input("Initial Capital", min_value=1000, value=10000, step=500)

if st.sidebar.button("Load / Refresh Data", use_container_width=True):
    st.session_state["data_loaded"] = True

if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = True

st.title("📈 Market Trend Analyzer")
st.caption("Educational demo. Not investment advice.")

# --- Loop through tickers ---
for ticker in tickers:
    if st.session_state["data_loaded"]:
        if source == "Yahoo Finance":
            df = yahoo.load_data(ticker, start, end, interval)
        elif source == "Alpha Vantage":
            df = alpha_vantage.load_data(ticker, start, end, interval, api_key=st.secrets.get("api_keys", {}).get("alpha",""))
        elif source.startswith("Polygon"):
            df = polygon.load_data(ticker, start, end, interval, api_key=st.secrets.get("api_keys",{}).get("polygon",""))
        elif source.startswith("Finnhub"):
            df = finnhub.load_data(ticker, start, end, interval, api_key=st.secrets.get("api_keys",{}).get("finnhub",""))
        else:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if df.empty:
        st.warning(f"No data for {ticker}. Check ticker, date range, API key, or chosen data source.")
        continue

    data = compute_indicators(df, sma=sma_window, ema=ema_window, rsi=rsi_window,
                              macd_fast=macd_fast, macd_slow=macd_slow, macd_signal=macd_signal)

    st.header(f"📊 {ticker} Analysis")

    st.subheader(f"{ticker} Price with Simple & Exponential Moving Averages")
    st.plotly_chart(plot_price(data, sma_window, ema_window), use_container_width=True)

    st.subheader("Relative Strength Index (RSI)")
    st.plotly_chart(plot_rsi(data, rsi_window), use_container_width=True)

    st.subheader("Moving Average Convergence Divergence (MACD)")
    st.plotly_chart(plot_macd(data), use_container_width=True)

    bt = run_crossover(data, fast_ma=fast_ma, slow_ma=slow_ma, initial_capital=initial_capital)
    st.subheader("Backtest Equity Curve")
    st.plotly_chart(plot_equity(bt), use_container_width=True)

    metrics = compute_metrics(bt)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Equity", f"${bt['equity'].iloc[-1]:,.2f}")
    c2.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}" if not pd.isna(metrics['max_drawdown']) else "n/a")
    c3.metric("CAGR (approx.)", f"{metrics['cagr']:.2%}" if not pd.isna(metrics['cagr']) else "n/a")
    c4.metric("Win Rate", f"{metrics['win_rate']:.1%}" if not pd.isna(metrics['win_rate']) else "n/a")

    # --- Safe handling of latest signal ---
    latest = bt.iloc[-1].to_dict()
    fast_val = latest.get("fast", float("nan"))
    slow_val = latest.get("slow", float("nan"))
    signal = "LONG" if latest.get("position", 0) > 0 else ("SHORT" if latest.get("position", 0) < 0 else "FLAT")
    st.info(f"Latest signal: {signal} | fast={fast_val if pd.notna(fast_val) else 'n/a'}, slow={slow_val if pd.notna(slow_val) else 'n/a'}")

    # --- AI Predictions ---
    if ai_model_choice != "None":
        st.subheader(f"AI Prediction using {ai_model_choice}")
        if ai_model_choice == "LSTM":
            model, preds, scaler = train_lstm(data)
            st.line_chart({"Actual": data["Close"].iloc[-len(preds):], "Predicted": preds})
            # Future forecast (7 days)
            future_preds = predict_future_lstm(model, data["Close"], scaler, lookback=60, days=7)
            st.subheader("📈 LSTM Future Forecast (Next 7 Days)")
            st.line_chart({"Future": future_preds})
        elif ai_model_choice == "Transformer":
            _, preds, _ = train_transformer(data)
            st.line_chart({"Actual": data["Close"].iloc[-len(preds):], "Predicted": preds})
        elif ai_model_choice == "Linear Regression":
            _, preds = train_linear_regression(data)
            st.line_chart({"Actual": data["Close"], "Predicted": preds})
        elif ai_model_choice == "Random Forest":
            _, preds = train_random_forest(data)
            st.line_chart({"Actual": data["Close"], "Predicted": preds})

    st.download_button(f"Download {ticker} indicators CSV", data=data.to_csv().encode('utf-8'), file_name=f"{ticker}_indicators.csv", mime='text/csv')
    export_cols = ['Close','fast','slow','signal','position','returns','strategy','equity']
    export_existing = [c for c in export_cols if c in bt.columns]
    st.download_button(f"Download {ticker} backtest CSV", data=bt[export_existing].to_csv().encode('utf-8'), file_name=f"{ticker}_backtest.csv", mime='text/csv')

    st.markdown("---")
