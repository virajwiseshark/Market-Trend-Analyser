import yfinance as yf
import pandas as pd
from streamlit import cache_data

@cache_data
def load_data(ticker, start, end, interval):
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
    if not df.empty:
        df.dropna(inplace=True)
    return df
