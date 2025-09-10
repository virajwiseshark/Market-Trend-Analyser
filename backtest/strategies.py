import pandas as pd
import numpy as np

def run_crossover(data, fast_ma=10, slow_ma=30, initial_capital=10000):
    bt = data.copy()
    if 'Close' not in bt.columns:
        return bt
    bt['fast'] = bt['Close'].ewm(span=int(fast_ma), adjust=False).mean()
    bt['slow'] = bt['Close'].ewm(span=int(slow_ma), adjust=False).mean()
    bt['signal'] = 0
    bt.loc[bt['fast'] > bt['slow'], 'signal'] = 1
    bt.loc[bt['fast'] < bt['slow'], 'signal'] = -1
    bt['position'] = bt['signal'].shift(1).fillna(0)
    bt['returns'] = bt['Close'].pct_change().fillna(0)
    bt['strategy'] = bt['position'] * bt['returns']
    bt['equity'] = (1 + bt['strategy']).cumprod() * initial_capital
    return bt

def compute_metrics(bt, interval='1d'):
    metrics = {}
    # max drawdown
    if 'equity' in bt.columns:
        cummax = bt['equity'].cummax()
        drawdown = bt['equity'] / cummax - 1
        metrics['max_drawdown'] = drawdown.min()
    else:
        metrics['max_drawdown'] = np.nan

    # cagr approximation
    periods_per_year = {'1d':252,'1wk':52,'1mo':12}.get(interval,252)
    if 'equity' in bt.columns and len(bt) > 1:
        total_return = bt['equity'].iloc[-1] / bt['equity'].iloc[0] - 1
        years = len(bt) / periods_per_year
        metrics['cagr'] = (1 + total_return)**(1/years) - 1 if years>0 else np.nan
    else:
        metrics['cagr'] = np.nan

    # win rate
    if 'strategy' in bt.columns:
        trades = bt[bt['position'] != 0]
        metrics['win_rate'] = (trades['strategy'] > 0).sum() / max(1, (trades['strategy'] != 0).sum())
    else:
        metrics['win_rate'] = np.nan

    return metrics
