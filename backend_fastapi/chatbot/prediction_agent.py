# ==========================================
# 🔮 PREDICTION AGENT (FUTURE FAILURE)
# ==========================================

def predict_failure_risk(machine):

    future_temp = machine.get("future_temperature", 0)
    risk = machine.get("prediction", 0)

    if future_temp > 305:
        return "High probability of overheating failure"

    if risk > 0.7:
        return "Failure likely soon"

    if risk > 0.5:
        return "Moderate risk increasing"

    return "Stable in near term"