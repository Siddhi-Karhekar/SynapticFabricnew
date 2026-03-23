def train_lstm(data_path):

    if not TF_AVAILABLE:
        raise Exception("TensorFlow not installed")

    df = pd.read_csv(data_path)

    features = ["temperature", "torque", "tool_wear", "vibration_index"]

    data = df[features].values

    X, y = [], []
    seq_len = 5

    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len][0])

    X = np.array(X)
    y = np.array(y)

    model = Sequential([
        LSTM(64, input_shape=(seq_len, 4)),
        Dense(32, activation="relu"),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=16)

    model.save(MODEL_PATH)

    print("✅ LSTM trained")