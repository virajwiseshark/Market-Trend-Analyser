import numpy as np
import pandas as pd

def compute_indicators(df, sma=20, ema=50, rsi=14, macd_fast=12, macd_slow=26, macd_signal=9):
    data = df.copy()
    if 'Close' not in data.columns:
        return data
    data['SMA'] = data['Close'].rolling(window=int(sma)).mean()
    data['EMA'] = data['Close'].ewm(span=int(ema), adjust=False).mean()

    # RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(int(rsi)).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(int(rsi)).mean()
    rs = gain / loss.replace(0, np.nan)
    data['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema_fast = data['Close'].ewm(span=int(macd_fast), adjust=False).mean()
    ema_slow = data['Close'].ewm(span=int(macd_slow), adjust=False).mean()
    data['MACD'] = ema_fast - ema_slow
    data['MACD_signal'] = data['MACD'].ewm(span=int(macd_signal), adjust=False).mean()
    data['MACD_hist'] = data['MACD'] - data['MACD_signal']
    return data
