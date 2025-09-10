import plotly.graph_objs as go

def plot_price(data, sma_window=None, ema_window=None):
    fig = go.Figure()
    if set(['Open','High','Low','Close']).issubset(data.columns):
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price'))
    else:
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close'))

    if 'SMA' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], name=f'SMA {sma_window}' if sma_window else 'SMA'))
    if 'EMA' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA'], name=f'EMA {ema_window}' if ema_window else 'EMA'))

    fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=500, xaxis_rangeslider_visible=False)
    return fig

def plot_rsi(data, rsi_window=14):
    fig = go.Figure()
    if 'RSI' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name=f'RSI {rsi_window}'))
        fig.add_hline(y=70, line_dash='dot')
        fig.add_hline(y=30, line_dash='dot')
    fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=250, xaxis_rangeslider_visible=False)
    return fig

def plot_macd(data):
    fig = go.Figure()
    if {'MACD','MACD_signal','MACD_hist'}.issubset(data.columns):
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD'))
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], name='Signal'))
        fig.add_trace(go.Bar(x=data.index, y=data['MACD_hist'], name='Hist'))
    fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, xaxis_rangeslider_visible=False, barmode='relative')
    return fig

def plot_equity(bt):
    fig = go.Figure()
    if 'equity' in bt.columns:
        fig.add_trace(go.Scatter(x=bt.index, y=bt['equity'], name='Equity Curve'))
    fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=350, xaxis_rangeslider_visible=False)
    return fig
