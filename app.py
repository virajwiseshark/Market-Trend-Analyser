import streamlit as st
import pandas as pd
from datetime import date, timedelta
from config.settings import DEFAULT_TICKER, DEFAULT_INTERVAL, DEFAULT_START_DAYS
from indicators.technicals import compute_indicators
from backtest.strategies import run_crossover, compute_metrics
from data_sources import yahoo, alpha_vantage, polygon, finnhub
from utils.plotting import plot_price, plot_rsi, plot_macd, plot_equity

st.set_page_config(page_title="Market Trend Analyzer", layout="wide")
st.sidebar.title("Market Trend Analyzer")

# --- Sidebar: data source & basic inputs ---
source = st.sidebar.selectbox("Data Source", ["Yahoo Finance", "Alpha Vantage", "Polygon (placeholder)", "Finnhub (placeholder)"])
ticker = st.sidebar.text_input("Ticker (symbol)", DEFAULT_TICKER)
col1, col2 = st.sidebar.columns(2)
start = col1.date_input("Start", value=date.today() - timedelta(days=DEFAULT_START_DAYS))
end = col2.date_input("End", value=date.today())
interval = st.sidebar.selectbox("Interval", DEFAULT_INTERVAL, index=0)

# API key input for Alpha Vantage (optional; also support st.secrets)
alpha_api_key = ""
if source == "Alpha Vantage":
    alpha_api_key = st.sidebar.text_input("Alpha Vantage API Key", value=st.secrets.get('api_keys', {}).get('alpha','') if st.secrets.get('api_keys',{}) else "", type="password")
    if not alpha_api_key:
        st.sidebar.info("Alpha Vantage API key required for this source. Put it in the field or in .streamlit/secrets.toml")

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

# --- Load data based on selected source ---
if st.session_state["data_loaded"]:
    if source == "Yahoo Finance":
        df = yahoo.load_data(ticker, start, end, interval)
    elif source == "Alpha Vantage":
        df = alpha_vantage.load_data(ticker, start, end, interval, api_key=alpha_api_key)
    elif source.startswith("Polygon"):
        df = polygon.load_data(ticker, start, end, interval, api_key=st.secrets.get('api_keys',{}).get('polygon',''))
    elif source.startswith("Finnhub"):
        df = finnhub.load_data(ticker, start, end, interval, api_key=st.secrets.get('api_keys',{}).get('finnhub',''))
    else:
        df = pd.DataFrame()
else:
    df = pd.DataFrame()

st.title("📈 Market Trend Analyzer")
st.caption("Educational demo. Not investment advice.")

if df.empty:
    st.warning("No data. Check ticker, date range, API key, or chosen data source.")
    st.stop()

# --- Compute indicators ---
data = compute_indicators(df, sma=sma_window, ema=ema_window, rsi=rsi_window,
                          macd_fast=macd_fast, macd_slow=macd_slow, macd_signal=macd_signal)

# --- Plot price and indicators ---
st.subheader(f"{ticker} Price with SMA/EMA  —  Source: {source}")
st.plotly_chart(plot_price(data, sma_window, ema_window), use_container_width=True)

st.subheader("RSI")
st.plotly_chart(plot_rsi(data, rsi_window), use_container_width=True)

st.subheader("MACD")
st.plotly_chart(plot_macd(data), use_container_width=True)

# --- Backtest ---
bt = run_crossover(data, fast_ma=fast_ma, slow_ma=slow_ma, initial_capital=initial_capital)

st.subheader("Backtest Equity Curve")
st.plotly_chart(plot_equity(bt), use_container_width=True)

metrics = compute_metrics(bt)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Final Equity", f"${bt['equity'].iloc[-1]:,.2f}")
c2.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}" if not pd.isna(metrics['max_drawdown']) else "n/a")
c3.metric("CAGR (approx.)", f"{metrics['cagr']:.2%}" if not pd.isna(metrics['cagr']) else "n/a")
c4.metric("Win Rate", f"{metrics['win_rate']:.1%}" if not pd.isna(metrics['win_rate']) else "n/a")

latest = bt.iloc[-1][['fast','slow','position']]
st.info(f"Latest signal: {'LONG' if latest['position']>0 else ('SHORT' if latest['position']<0 else 'FLAT')}  |  fast={latest['fast']:.2f}, slow={latest['slow']:.2f}")

# --- Downloads ---
st.download_button("Download price & indicators CSV", data=data.to_csv().encode('utf-8'), file_name=f"{ticker}_indicators.csv", mime='text/csv')
export_cols = ['Close','fast','slow','signal','position','returns','strategy','equity']
export_existing = [c for c in export_cols if c in bt.columns]
st.download_button("Download backtest CSV", data=bt[export_existing].to_csv().encode('utf-8'), file_name=f"{ticker}_backtest.csv", mime='text/csv')

st.caption(f"Built with Streamlit, yfinance, plotly. Data source: {source}. Educational use only.")
