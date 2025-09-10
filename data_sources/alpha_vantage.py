import pandas as pd
from streamlit import cache_data

try:
    from alpha_vantage.timeseries import TimeSeries
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False

@cache_data
def load_data(ticker, start, end, interval, api_key=""):
    if not _AVAILABLE:
        return pd.DataFrame()
    if not api_key:
        return pd.DataFrame()
    ts = TimeSeries(key=api_key, output_format='pandas', indexing_type='date')
    try:
        if interval == "1d":
            df, _ = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
        elif interval == "1wk":
            df, _ = ts.get_weekly_adjusted(symbol=ticker)
        elif interval == "1mo":
            df, _ = ts.get_monthly_adjusted(symbol=ticker)
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

    # rename columns to match yfinance style
    rename_map = {}
    for col in df.columns:
        if col.startswith('1. '):
            rename_map[col] = 'Open'
        elif col.startswith('2. '):
            rename_map[col] = 'High'
        elif col.startswith('3. '):
            rename_map[col] = 'Low'
        elif col.startswith('4. '):
            rename_map[col] = 'Close'
        elif 'adjusted close' in col.lower() or col.startswith('5. '):
            rename_map[col] = 'Adj Close'
        elif 'volume' in col.lower() or col.startswith('6. '):
            rename_map[col] = 'Volume'
    df = df.rename(columns=rename_map)
    if 'Adj Close' in df.columns and 'Close' not in df.columns:
        df['Close'] = df['Adj Close']
    keep = [c for c in ['Open','High','Low','Close','Volume'] if c in df.columns]
    df = df[keep].copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.loc[(df.index.date >= pd.to_datetime(start).date()) & (df.index.date <= pd.to_datetime(end).date())]
    df.dropna(inplace=True)
    return df
