# ==========================================
# 🔍 ANALYSIS AGENT (CORRELATION ENGINE)
# ==========================================

def analyze_patterns(machine):

    insights = []

    if machine["temperature"] > 300 and machine["vibration_index"] > 0.6:
        insights.append("Thermal + vibration coupling")

    if machine["tool_wear"] > 0.8 and machine["torque"] > 50:
        insights.append("Wear-induced cutting stress")

    if machine["vibration_index"] > 0.8:
        insights.append("Mechanical instability")

    if not insights:
        insights.append("No abnormal correlation")

    return insights