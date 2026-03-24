# ==========================================
# 🧠 INDUSTRIAL REASONING ENGINE (FINAL SAFE)
# ==========================================


# ==========================================
# 🔍 SAFE VALUE EXTRACTOR
# ==========================================
def safe_get(m: dict, key: str, default=0):
    try:
        val = m.get(key, default)
        return default if val is None else val
    except Exception:
        return default


# ==========================================
# 🧠 ANALYZE MACHINE CONDITIONS
# ==========================================
def analyze_machine_conditions(m: dict):

    if not isinstance(m, dict):
        return []

    signals = []

    temp = safe_get(m, "temperature")
    vib = safe_get(m, "vibration_index")
    wear = safe_get(m, "tool_wear")
    torque = safe_get(m, "torque")

    if temp > 85:
        signals.append("thermal overload")

    if vib > 0.6:
        signals.append("mechanical instability")

    if wear > 0.8:
        signals.append("tool degradation")

    if torque > 80:
        signals.append("excessive load")

    return signals


# ==========================================
# 🧠 ROOT CAUSE GENERATION (SAFE)
# ==========================================
def generate_root_cause(machine_id: str, m: dict):

    if not isinstance(m, dict):
        return f"{machine_id} data unavailable."

    signals = analyze_machine_conditions(m)

    if not signals:
        return f"{machine_id} is operating within normal parameters."

    return (
        f"{machine_id} shows elevated failure risk due to: "
        f"{', '.join(signals)}. "
        f"These combined factors indicate progressive degradation and potential failure."
    )


# ==========================================
# 📊 COMPARE MACHINES (FULL SAFE VERSION)
# ==========================================
def compare_machines(live_data: dict):

    # ======================================
    # ❌ NO DATA
    # ======================================
    if not isinstance(live_data, dict) or not live_data:
        return "No live machine data available."

    valid_machines = []

    # ======================================
    # 🔍 CLEAN + VALIDATE DATA
    # ======================================
    for m in live_data.values():

        if not isinstance(m, dict):
            continue

        machine_id = m.get("machine_id")

        if not machine_id:
            continue

        risk = safe_get(m, "prediction", 0)

        valid_machines.append({
            "machine_id": machine_id,
            "risk": risk,
            "reason": m.get("ai_reason", "No issue detected"),
            "health": m.get("health_status", "Unknown")
        })

    # ======================================
    # ❌ NO VALID DATA
    # ======================================
    if not valid_machines:
        return "No valid machine data available."

    # ======================================
    # 🔴 WORST MACHINE
    # ======================================
    worst = max(valid_machines, key=lambda x: x["risk"])

    # ======================================
    # 🟢 BEST MACHINE
    # ======================================
    best = min(valid_machines, key=lambda x: x["risk"])

    # ======================================
    # 📊 BUILD RESPONSE
    # ======================================
    return (
        f"Most critical: {worst['machine_id']} "
        f"(Risk {worst['risk']*100:.0f}%)\n"
        f"Issue: {worst['reason']}\n\n"
        f"Healthiest: {best['machine_id']} "
        f"(Risk {best['risk']*100:.0f}%)\n"
        f"Status: {best['health']}"
    )