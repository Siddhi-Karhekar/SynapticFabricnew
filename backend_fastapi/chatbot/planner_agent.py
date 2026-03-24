# ==========================================
# 🧠 PLANNER AGENT (INTENT + STRATEGY)
# ==========================================

def plan_execution(intent: dict, question: str) -> dict:

    plan = {
        "use_live": False,
        "use_history": False,
        "use_prediction": False,
        "use_root_cause": False,
        "mode": "fast"
    }

    t = intent.get("type")

    if t == "metric":
        plan["use_live"] = True
        plan["mode"] = "fast"

    elif t == "comparison":
        plan["use_live"] = True

    elif t == "root_cause":
        plan["use_live"] = True
        plan["use_root_cause"] = True
        plan["mode"] = "hybrid"

    elif t in ["historical", "failure_analysis"]:
        plan["use_history"] = True
        plan["mode"] = "llm"

    # 🔥 FINAL BOSS: prediction trigger
    if any(x in question.lower() for x in ["future", "predict", "next failure"]):
        plan["use_prediction"] = True
        plan["mode"] = "llm"

    return plan