import numpy as np
from sklearn.ensemble import IsolationForest

# ==========================================
# 🔥 GLOBAL MODEL (TRAIN ONCE)
# ==========================================
_model = None


def _train_model():
    global _model

    if _model is not None:
        return

    print("🧠 Training anomaly model...")

    X = []

    # generate synthetic "healthy" data
    for _ in range(1000):
        X.append([
            np.random.uniform(290, 300),   # temperature
            np.random.uniform(35, 50),     # torque
            np.random.uniform(0.05, 0.2),  # tool wear
            np.random.uniform(0.1, 0.3)    # vibration
        ])

    X = np.array(X)

    _model = IsolationForest(
        n_estimators=100,
        contamination=0.08,
        random_state=42
    )

    _model.fit(X)

    print("✅ Anomaly model ready")


# ==========================================
# 🚀 MAIN FUNCTION
# ==========================================
def detect_anomaly(machine):

    global _model

    try:
        if _model is None:
            _train_model()

        X = [[
            machine.get("temperature", 0),
            machine.get("torque", 0),
            machine.get("tool_wear", 0),
            machine.get("vibration_index", 0)
        ]]

        score = _model.decision_function(X)[0]

        # normalize to 0–1
        normalized = max(0, min(1, -score))

        return round(normalized, 3)

    except Exception as e:
        print("❌ ANOMALY SAFE FALLBACK:", e)
        return 0.0