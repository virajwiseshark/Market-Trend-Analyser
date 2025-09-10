import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class TransformerPredictor(nn.Module):
    def __init__(self, feature_size=1, num_layers=2, nhead=2, hidden_dim=64):
        super().__init__()
        self.input_layer = nn.Linear(feature_size, hidden_dim)
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=nhead)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(hidden_dim, 1)

    def forward(self, src):
        x = self.input_layer(src)
        x = self.transformer(x)
        return self.fc_out(x)

def train_transformer(data, feature="Close", lookback=60, epochs=5, lr=0.001):
    values = data[feature].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i, 0])
        y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)

    X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

    model = TransformerPredictor()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        preds = model(X_tensor).numpy()

    preds = scaler.inverse_transform(preds)
    return model, preds.flatten(), scaler
