import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

MODEL_PATH = "ml_models/lstm_model.h5"

# ==========================================
# 🚀 TRAIN LSTM MODEL
# ==========================================
def train_lstm():

    # dummy synthetic sequence data
    X = []
    y = []

    for _ in range(1000):
        seq = np.random.rand(10, 4)  # 10 timesteps, 4 features
        target = np.mean(seq[-1])  # future proxy
        X.append(seq)
        y.append(target)

    X = np.array(X)
    y = np.array(y)

    model = Sequential([
        LSTM(64, input_shape=(10, 4), return_sequences=False),
        Dense(32, activation="relu"),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=5, batch_size=32)

    os.makedirs("ml_models", exist_ok=True)
    model.save(MODEL_PATH)

    print("✅ LSTM model trained & saved")


# ==========================================
# 🔮 PREDICT FUTURE RISK
# ==========================================
def predict_future(machine, history=None):

    from tensorflow.keras.models import load_model

    if not os.path.exists(MODEL_PATH):
        raise Exception("LSTM model not trained")

    model = load_model(MODEL_PATH)

    # build fake sequence if no history
    if history is None:
        seq = np.array([
            [
                machine.get("temperature", 295) / 330,
                machine.get("torque", 40) / 100,
                machine.get("tool_wear", 0.1),
                machine.get("vibration_index", 0.2)
            ]
        ] * 10)
    else:
        seq = np.array(history)

    seq = np.expand_dims(seq, axis=0)

    pred = model.predict(seq)[0][0]

    pred = max(0, min(float(pred), 1))

    return round(pred, 3)