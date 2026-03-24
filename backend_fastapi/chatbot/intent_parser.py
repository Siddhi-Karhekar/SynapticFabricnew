# ==========================================
# 🧠 ADVANCED INTENT PARSER (PRODUCTION GRADE)
# ==========================================

import re

MACHINES = ["M_1", "M_2", "M_3"]

METRIC_KEYWORDS = {
    "temperature": ["temperature", "temp", "heat"],
    "vibration_index": ["vibration", "vibe", "oscillation"],
    "torque": ["torque", "load"],
    "tool_wear": ["wear", "tool wear", "degradation"]
}


# ==========================================
# 🧠 MAIN INTENT PARSER
# ==========================================
def parse_intent(question: str):
    q = question.lower()

    # ==========================================
    # 🔴 ROOT CAUSE
    # ==========================================
    if any(x in q for x in ["why", "cause", "reason", "root cause", "explain"]):
        return {"type": "root_cause"}

    # ==========================================
    # 📈 COMPARISON
    # ==========================================
    if any(x in q for x in [
        "compare", "highest", "max", "worst",
        "critical", "best", "healthiest",
        "safest", "lowest", "top"
    ]):
        return {"type": "comparison"}

    # ==========================================
    # 🔧 MAINTENANCE
    # ==========================================
    if any(x in q for x in [
        "maintain", "maintenance", "repair",
        "fix", "priority", "service"
    ]):
        return {"type": "maintenance"}

    # ==========================================
    # 🔮 PREDICTION
    # ==========================================
    if any(x in q for x in [
        "predict", "future", "next", "rul", "remaining life"
    ]):
        return {"type": "prediction"}

    # ==========================================
    # 📊 METRIC (MOVE UP 🔥)
    # ==========================================
    for metric, keywords in METRIC_KEYWORDS.items():
        if any(k in q for k in keywords):
            return {"type": "metric", "metric": metric}

    # ==========================================
    # ⏱ TIME DETECTION (STRICT)
    # ==========================================
    if re.search(r'\d{1,2}:\d{2}', q):
        return {"type": "historical"}

    # ==========================================
    # 📊 HISTORICAL (NO "at" ❌)
    # ==========================================
    if any(x in q for x in ["history", "trend", "last", "past", "timeline"]):
        return {"type": "historical"}

    # ==========================================
    # 🔴 FAILURE ANALYSIS
    # ==========================================
    if any(x in q for x in ["failure", "fail", "breakdown"]):
        return {"type": "failure_analysis"}

    return {"type": "general"}


# ==========================================
# 🔍 MACHINE EXTRACTOR (ROBUST)
# ==========================================
def extract_machine(question: str):
    q = question.upper()

    for m in MACHINES:
        if m in q:
            return m

    match = re.search(r"M[\s\-_]?(\d)", q)
    if match:
        return f"M_{match.group(1)}"

    return None


# ==========================================
# ⏱ TIME EXTRACTOR
# ==========================================
def extract_time(question: str):
    q = question.lower()

    match = re.search(r'(\d{1,2}:\d{2})', q)

    if match:
        return match.group(1)

    return None