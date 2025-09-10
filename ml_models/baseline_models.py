import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

def train_linear_regression(data, feature="Close"):
    X = np.arange(len(data)).reshape(-1, 1)
    y = data[feature].values
    model = LinearRegression().fit(X, y)
    preds = model.predict(X)
    return model, preds

def train_random_forest(data, feature="Close"):
    X = np.arange(len(data)).reshape(-1, 1)
    y = data[feature].values
    model = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
    preds = model.predict(X)
    return model, preds
