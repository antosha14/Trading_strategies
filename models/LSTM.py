import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

data = pd.read_csv("./btc_timestampdata.csv")
data["timestamp"] = pd.to_datetime(data["timestamp"], format="ISO8601")


scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(
    data[
        [
            "price",
            "volume_5000_bids",
            "volume_5000_asks",
            "weighted_avg_bid_price",
            "weighted_avg_ask_price",
        ]
    ]
)

X = data_scaled[:, :-1]
y = data_scaled[:, 0]
X = np.reshape(X, (X.shape[0], 1, X.shape[1]))


model = keras.Sequential()
model.add(
    keras.layers.LSTM(units=50, return_sequences=True, input_shape=(1, X.shape[2]))
)
model.add(keras.layers.LSTM(units=50))
model.add(keras.layers.Dense(1))
model.compile(loss="mse", optimizer="adam")

model.fit(X, y, epochs=100, batch_size=32)

prediction = model.predict(X)
prediction_unscaled = scaler.inverse_transform(
    np.concatenate((prediction, X[:, :, 1:]), axis=2)
)[:, 0]
print("Predicted stock price:", prediction_unscaled[0])
