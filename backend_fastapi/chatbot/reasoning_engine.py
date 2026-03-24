# ==========================================
# 🧠 INDUSTRIAL REASONING ENGINE
# ==========================================

def analyze_machine_conditions(m):
    signals = []

    if m.get("temperature", 0) > 85:
        signals.append("thermal overload")

    if m.get("vibration_index", 0) > 0.6:
        signals.append("mechanical instability")

    if m.get("tool_wear", 0) > 0.8:
        signals.append("tool degradation")

    if m.get("torque", 0) > 80:
        signals.append("excessive load")

    return signals


def generate_root_cause(machine_id: str, m: dict):
    signals = analyze_machine_conditions(m)

    if not signals:
        return f"{machine_id} is operating within normal parameters."

    return (
        f"{machine_id} shows elevated failure risk due to: "
        f"{', '.join(signals)}. "
        f"These combined factors indicate progressive degradation and potential failure."
    )


def compare_machines(live_data: dict):
    if not live_data:
        return "No live machine data available."

    worst = max(
        live_data.values(),
        key=lambda m: m.get("prediction", 0)
    )

    return (
        f"{worst['machine_id']} is the most critical machine.\n"
        f"Failure risk: {worst.get('prediction', 0)*100:.0f}%\n"
        f"Primary issue: {worst.get('ai_reason', 'unknown')}"
    )