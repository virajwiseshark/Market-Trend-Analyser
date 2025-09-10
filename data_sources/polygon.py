import pandas as pd
from streamlit import cache_data

@cache_data
def load_data(ticker, start, end, interval, api_key=""):
    # Placeholder: implement Polygon.io fetching if you have an API key.
    # Return empty DataFrame for now.
    return pd.DataFrame()
