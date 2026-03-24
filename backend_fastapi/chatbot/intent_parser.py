# ==========================================
# 🧠 ADVANCED INTENT PARSER (INDUSTRIAL GRADE)
# ==========================================

import re

MACHINES = ["M_1", "M_2", "M_3"]

METRIC_KEYWORDS = {
    "temperature": ["temperature", "temp", "heat"],
    "vibration_index": ["vibration", "vibe", "oscillation"],
    "torque": ["torque", "load"],
    "tool_wear": ["wear", "tool wear", "degradation"]
}


def parse_intent(question: str):
    q = question.lower()

    # ==========================================
    # 🔴 ROOT CAUSE / REASONING
    # ==========================================
    if any(x in q for x in ["why", "cause", "reason", "root cause"]):
        return {"type": "root_cause"}

    # ==========================================
    # 📊 HISTORICAL ANALYSIS
    # ==========================================
    if any(x in q for x in ["history", "trend", "last", "past", "timeline"]):
        return {"type": "historical"}

    # ==========================================
    # 🔴 FAILURE ANALYSIS
    # ==========================================
    if any(x in q for x in ["failure", "fail", "breakdown"]):
        return {"type": "failure_analysis"}

    # ==========================================
    # 📈 COMPARISON
    # ==========================================
    if any(x in q for x in ["compare", "highest", "max", "worst", "critical"]):
        return {"type": "comparison"}

    # ==========================================
    # 🔧 MAINTENANCE
    # ==========================================
    if any(x in q for x in ["maintain", "maintenance", "repair", "fix", "priority"]):
        return {"type": "maintenance"}

    # ==========================================
    # 📊 METRIC DETECTION
    # ==========================================
    for metric, keywords in METRIC_KEYWORDS.items():
        if any(k in q for k in keywords):
            return {"type": "metric", "metric": metric}

    # ==========================================
    # GENERAL
    # ==========================================
    return {"type": "general"}


# ==========================================
# 🔍 MACHINE EXTRACTOR (ROBUST)
# ==========================================
def extract_machine(question: str):
    q = question.upper()

    for m in MACHINES:
        if m in q:
            return m

    # regex fallback (e.g., m1, m-1, machine 1)
    match = re.search(r"M[\s\-_]?(\d)", q)
    if match:
        return f"M_{match.group(1)}"

    return None