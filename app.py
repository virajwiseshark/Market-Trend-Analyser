
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objs as go
from datetime import date, timedelta
import math

st.set_page_config(page_title="Market Trend Analyzer", layout="wide")

# ---------- Sidebar controls ----------
st.sidebar.title("Market Trend Analyzer")
default_ticker = "AAPL"
ticker = st.sidebar.text_input("Ticker (Yahoo Finance symbol)", default_ticker)
col1, col2 = st.sidebar.columns(2)
start = col1.date_input("Start", value=date.today() - timedelta(days=365*2))
end = col2.date_input("End", value=date.today())
interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("Indicators")
sma_window = st.sidebar.number_input("SMA window", min_value=2, max_value=400, value=20, step=1)
ema_window = st.sidebar.number_input("EMA window", min_value=2, max_value=400, value=50, step=1)
rsi_window = st.sidebar.number_input("RSI window", min_value=2, max_value=100, value=14, step=1)
macd_fast = st.sidebar.number_input("MACD fast", min_value=2, max_value=100, value=12, step=1)
macd_slow = st.sidebar.number_input("MACD slow", min_value=2, max_value=200, value=26, step=1)
macd_signal = st.sidebar.number_input("MACD signal", min_value=2, max_value=50, value=9, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Backtest (MA Crossover)")
fast_ma = st.sidebar.number_input("Fast MA", min_value=2, max_value=200, value=10, step=1)
slow_ma = st.sidebar.number_input("Slow MA", min_value=2, max_value=400, value=30, step=1)
initial_capital = st.sidebar.number_input("Initial Capital", min_value=1000, value=10000, step=500)

# ---------- Data fetch ----------
@st.cache_data(show_spinner=False)
def load_data(ticker, start, end, interval):
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
    if not df.empty:
        df.dropna(inplace=True)
    return df

if st.sidebar.button("Load / Refresh Data", use_container_width=True):
    st.session_state["data_loaded"] = True

if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = True

if st.session_state["data_loaded"]:
    df = load_data(ticker, start, end, interval)
else:
    df = pd.DataFrame()

st.title("📈 Market Trend Analyzer")
st.caption("Educational demo. Not investment advice.")

if df.empty:
    st.warning("No data. Check the ticker or date range.")
    st.stop()

# ---------- Indicators ----------
def compute_indicators(df):
    data = df.copy()
    data["SMA"] = data["Close"].rolling(window=int(sma_window)).mean()
    data["EMA"] = data["Close"].ewm(span=int(ema_window), adjust=False).mean()

    # RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(rsi_window).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(rsi_window).mean()
    rs = gain / loss.replace(0, np.nan)
    data["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema_fast = data["Close"].ewm(span=int(macd_fast), adjust=False).mean()
    ema_slow = data["Close"].ewm(span=int(macd_slow), adjust=False).mean()
    data["MACD"] = ema_fast - ema_slow
    data["MACD_signal"] = data["MACD"].ewm(span=int(macd_signal), adjust=False).mean()
    data["MACD_hist"] = data["MACD"] - data["MACD_signal"]
    return data

data = compute_indicators(df)

# ---------- Price Chart ----------
price_fig = go.Figure()
price_fig.add_trace(go.Candlestick(
    x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name="Price"
))
price_fig.add_trace(go.Scatter(x=data.index, y=data["SMA"], line=dict(), name=f"SMA {sma_window}"))
price_fig.add_trace(go.Scatter(x=data.index, y=data["EMA"], line=dict(), name=f"EMA {ema_window}"))
price_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=500, xaxis_rangeslider_visible=False)

st.subheader(f"{ticker} Price with SMA/EMA")
st.plotly_chart(price_fig, use_container_width=True)

# ---------- RSI Chart ----------
rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(x=data.index, y=data["RSI"], name=f"RSI {rsi_window}"))
rsi_fig.add_hline(y=70, line_dash="dot")
rsi_fig.add_hline(y=30, line_dash="dot")
rsi_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=250, xaxis_rangeslider_visible=False)
st.subheader("RSI")
st.plotly_chart(rsi_fig, use_container_width=True)

# ---------- MACD Chart ----------
macd_fig = go.Figure()
macd_fig.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD"))
macd_fig.add_trace(go.Scatter(x=data.index, y=data["MACD_signal"], name="Signal"))
macd_fig.add_trace(go.Bar(x=data.index, y=data["MACD_hist"], name="Hist"))
macd_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=300, xaxis_rangeslider_visible=False, barmode="relative")
st.subheader("MACD")
st.plotly_chart(macd_fig, use_container_width=True)

# ---------- Backtest: MA Crossover ----------
bt = data.copy()
bt["fast"] = bt["Close"].ewm(span=int(fast_ma), adjust=False).mean()
bt["slow"] = bt["Close"].ewm(span=int(slow_ma), adjust=False).mean()
bt["signal"] = 0
bt.loc[bt["fast"] > bt["slow"], "signal"] = 1
bt.loc[bt["fast"] < bt["slow"], "signal"] = -1
bt["position"] = bt["signal"].shift(1).fillna(0)

bt["returns"] = bt["Close"].pct_change().fillna(0)
bt["strategy"] = bt["position"] * bt["returns"]

# equity curve
bt["equity"] = (1 + bt["strategy"]).cumprod() * initial_capital

# Metrics
def max_drawdown(series):
    cummax = series.cummax()
    drawdown = series / cummax - 1
    return drawdown.min()

def cagr(series, periods_per_year):
    if len(series) < 2:
        return np.nan
    total_return = series.iloc[-1] / series.iloc[0] - 1
    years = len(series) / periods_per_year
    if years <= 0:
        return np.nan
    return (1 + total_return) ** (1 / years) - 1

def sharpe(returns, rf=0.0, periods_per_year=252):
    # naive daily Sharpe approximation
    if returns.std() == 0:
        return np.nan
    return (returns.mean() - rf/periods_per_year) / returns.std() * np.sqrt(periods_per_year)

# approximate periods per year by interval
ppy = {"1d": 252, "1wk": 52, "1mo": 12}.get(interval, 252)

dd = max_drawdown(bt["equity"])
approx_cagr = cagr(bt["equity"], periods_per_year=ppy)
win_rate = (bt["strategy"] > 0).sum() / max(1, (bt["strategy"] != 0).sum())
sr = sharpe(bt["strategy"], periods_per_year=ppy)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Final Equity", f"${bt['equity'].iloc[-1]:,.2f}")
m2.metric("Max Drawdown", f"{dd:.2%}" if not math.isnan(dd) else "n/a")
m3.metric("CAGR (approx.)", f"{approx_cagr:.2%}" if not math.isnan(approx_cagr) else "n/a")
m4.metric("Win Rate", f"{win_rate:.1%}" if not math.isnan(win_rate) else "n/a")

# Equity curve chart
eq_fig = go.Figure()
eq_fig.add_trace(go.Scatter(x=bt.index, y=bt["equity"], name="Equity Curve"))
eq_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=350, xaxis_rangeslider_visible=False)
st.subheader("Backtest Equity Curve")
st.plotly_chart(eq_fig, use_container_width=True)

# Show latest signals
latest = bt.iloc[-1][["fast", "slow", "position"]]
st.info(f"Latest signal: {'LONG' if latest['position']>0 else ('SHORT' if latest['position']<0 else 'FLAT')}  |  fast={latest['fast']:.2f}, slow={latest['slow']:.2f}")

# Downloads
st.download_button("Download price & indicators CSV", data=data.to_csv().encode("utf-8"), file_name=f"{ticker}_indicators.csv", mime="text/csv")
export_cols = ["Close","fast","slow","signal","position","returns","strategy","equity"]
st.download_button("Download backtest CSV", data=bt[export_cols].to_csv().encode("utf-8"), file_name=f"{ticker}_backtest.csv", mime="text/csv")

st.caption("Built with Streamlit, yfinance, plotly. Educational use only.")
