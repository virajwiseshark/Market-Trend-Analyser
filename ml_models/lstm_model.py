import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def train_lstm(data, feature="Close", lookback=60, epochs=5, batch_size=32):
    values = data[feature].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i, 0])
        y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    preds = model.predict(X, verbose=0)
    preds = scaler.inverse_transform(preds)

    return model, preds.flatten(), scaler


def predict_future_lstm(model, data, scaler, lookback=60, days=7):
    """
    Predict future stock prices for 'days' ahead using trained LSTM.
    """
    last_data = data[-lookback:].values.reshape(-1, 1)
    scaled_last = scaler.transform(last_data)

    seq = scaled_last.reshape(1, lookback, 1)
    predictions = []

    for _ in range(days):
        pred = model.predict(seq, verbose=0)[0][0]
        predictions.append(pred)
        seq = np.append(seq[:, 1:, :], [[[pred]]], axis=1)

    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    return predictions.flatten()
