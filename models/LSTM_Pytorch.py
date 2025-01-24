import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler

# Load and preprocess the data
data = pd.read_csv("btc_timestampdata.csv")
data["timestamp"] = pd.to_datetime(data["timestamp"], format="mixed")
data.set_index("timestamp", inplace=True)

# Scale the features
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)


# Prepare the dataset
def create_dataset(data, time_step=60):
    X, y, finalActual = [], [], []
    for i in range(len(data) - time_step - 20):
        X.append(data[i : (i + time_step), :])
        y.append(data[(i + time_step + 20), 0])
        finalActual.append(data[(i + time_step), 0])
    return np.array(X), np.array(y), np.array(finalActual)


# Split the data into training and testing sets
train_size = int(len(scaled_data) * 0.98)
train_data = scaled_data[:train_size]
test_data = scaled_data[train_size:]

# Create datasets
X_train, y_train, z_train = create_dataset(train_data, time_step=60)
X_test, y_test, z_test = create_dataset(test_data, time_step=60)


# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        h0 = torch.zeros(num_layers, x.size(0), hidden_size).requires_grad_()
        c0 = torch.zeros(num_layers, x.size(0), hidden_size).requires_grad_()
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


# Hyperparameters
input_size = X_train.shape[2]  # Number of features
hidden_size = 50
num_layers = 2

# Initialize the model
model = LSTMModel(input_size, hidden_size, num_layers)

X_train_tensor = torch.Tensor(X_train)
y_train_tensor = torch.Tensor(y_train).view(-1, 1)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.002)

# Train the model
num_epochs = 4
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}")

torch.save(model.state_dict(), "LSTM_1.pth")


# Test the model
model.eval()
with torch.no_grad():
    predicted = model(torch.FloatTensor(X_test)).numpy()
    # Create an array with the same number of features as the original data
    predicted_full = np.zeros(
        (predicted.shape[0] * predicted.shape[1], scaled_data.shape[1])
    )
    predicted_full[:, 0] = predicted.flatten()  # Only fill the price column
    predicted = scaler.inverse_transform(predicted_full)[:, 0].reshape(
        predicted.shape[0], predicted.shape[1]
    )  # Inverse scaling only for price

    actual_full = np.zeros((y_test.shape[0] * y_test.shape[1], scaled_data.shape[1]))
    actual_full[:, 0] = y_test.flatten()  # Only fill the price column
    actual = scaler.inverse_transform(actual_full)[:, 0].reshape(
        y_test.shape[0], y_test.shape[1]
    )

    initial_full = np.zeros((z_test.shape[0] * z_test.shape[1], scaled_data.shape[1]))
    initial_full[:, 0] = z_test.flatten()  # Only fill the price column
    initial = scaler.inverse_transform(initial_full)[:, 0].reshape(
        z_test.shape[0], z_test.shape[1]
    )


# Log predicted, actual prices, and error
Error = 0
for i in range(predicted.shape[0]):
    for j in range(predicted.shape[1]):
        print(
            f"Predicted: {predicted[i, j]}, Actual: {actual[i, j]}, Error: {actual[i, j] - predicted[i, j]}"
        )
        Error = Error + actual[i, j] - predicted[i, j]

print(Error)
# Plot predicted vs actual prices
plt.figure(figsize=(14, 7))
plt.plot(actual[:, 0], label="Actual Prices", color="blue")
plt.plot(predicted[:, 0], label="Predicted Prices", color="orange")
plt.title("Stock Price Prediction")
plt.xlabel("Time Steps")
plt.ylabel("Price")
plt.legend()
plt.show()
