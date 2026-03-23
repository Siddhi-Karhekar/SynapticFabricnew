import numpy as np
import pandas as pd
import os

# ==========================================
# ⚠️ SAFE TENSORFLOW IMPORT (NO CRASH)
# ==========================================
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense

    TF_AVAILABLE = True

except Exception as e:
    print("⚠️ TensorFlow not available:", e)
    TF_AVAILABLE = False


MODEL_PATH = "ml_models/lstm_model.h5"


# ==========================================
# 🧠 TRAIN LSTM
# ==========================================
def train_lstm(data_path):

    if not TF_AVAILABLE:
        raise Exception("❌ TensorFlow not installed. Cannot train LSTM.")

    print("📂 Loading dataset:", data_path)

    df = pd.read_csv(data_path)

    print("✅ Columns:", df.columns.tolist())

    features = [
        "temperature",
        "torque",
        "tool_wear",
        "vibration_index"
    ]

    data = df[features].values

    # ======================================
    # CREATE SEQUENCES
    # ======================================
    X, y = [], []
    seq_len = 5

    for i in range(len(data) - seq_len):
        X.append(data[i:i + seq_len])
        y.append(data[i + seq_len][0])  # predict temperature

    X = np.array(X)
    y = np.array(y)

    print(f"📊 Training data shape: {X.shape}")

    # ======================================
    # MODEL
    # ======================================
    model = Sequential([
        LSTM(64, input_shape=(seq_len, 4)),
        Dense(32, activation="relu"),
        Dense(1)
    ])

    model.compile(
        optimizer="adam",
        loss="mse"
    )

    model.fit(
        X,
        y,
        epochs=10,
        batch_size=16,
        verbose=1
    )

    os.makedirs("ml_models", exist_ok=True)
    model.save(MODEL_PATH)

    print("✅ LSTM model saved at:", MODEL_PATH)


# ==========================================
# 🔮 PREDICT FUTURE (SAFE)
# ==========================================
def predict_future(sequence):

    # --------------------------------------
    # 🛡 SAFE FALLBACK (NO TF)
    # --------------------------------------
    if not TF_AVAILABLE:
        # return last known temperature
        return round(float(sequence[-1][0]), 2)

    # --------------------------------------
    # 🛡 MODEL CHECK
    # --------------------------------------
    if not os.path.exists(MODEL_PATH):
        raise Exception("❌ LSTM model not trained")

    try:
        model = load_model(MODEL_PATH)

        seq = np.array(sequence).reshape(1, len(sequence), 4)

        prediction = model.predict(seq, verbose=0)[0][0]

        return round(float(prediction), 2)

    except Exception as e:
        print("❌ LSTM PREDICTION ERROR:", e)

        # fallback
        return round(float(sequence[-1][0]), 2)