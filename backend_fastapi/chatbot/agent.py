# ==========================================
# 🤖 AGENT DECISION ENGINE
# ==========================================

def decide_strategy(intent):
    """
    Decide how to answer based on intent.
    """

    if intent["type"] == "metric":
        return "fast"

    if intent["type"] in ["comparison", "maintenance"]:
        return "fast"

    if intent["type"] == "root_cause":
        return "hybrid"

    if intent["type"] in ["historical", "failure_analysis"]:
        return "llm"

    return "llm"