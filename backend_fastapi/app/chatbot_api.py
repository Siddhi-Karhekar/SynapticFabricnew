from fastapi import APIRouter, Body
import ollama

from digital_twin.simulator import MACHINE_MEMORY
from backend_fastapi.ai_engine.machine_analyzer import machine_analyzer

# ✅ OPTIONAL (if LSTM available)
try:
    from ml_models.lstm_model import predict_future
    LSTM_AVAILABLE = True
except:
    LSTM_AVAILABLE = False

router = APIRouter()


@router.post("/chat")
async def chat(payload: dict = Body(...)):

    query = payload.get("query", "")
    query_lower = query.lower()

    print("📩 QUERY:", query)

    # ==========================================
    # 🔍 MACHINE ANALYSIS
    # ==========================================

    try:
        machines = []

        for k, v in MACHINE_MEMORY.items():
            machines.append({
                "machine_id": k,
                "temperature": v.get("temperature", 295),
                "torque": v.get("torque", 40),
                "tool_wear": v.get("tool_wear", 0.1),
                "vibration_index": v.get("vibration_index", 0.2)
            })

        analyzed = machine_analyzer.analyze_machines(machines)

        analyzed_sorted = sorted(
            analyzed,
            key=lambda x: x.get("prediction", 0),
            reverse=True
        )

        highest = analyzed_sorted[0] if analyzed_sorted else {}

    except Exception as e:
        print("❌ ANALYSIS ERROR:", e)

        analyzed = []
        analyzed_sorted = []

        highest = {
            "machine_id": "M_1",
            "prediction": 0.5,
            "health_status": "Unknown",
            "rul_cycles": 0,
            "rul_time": "unknown",
            "root_cause": [],
            "ai_reason": "Unavailable",
            "shap": {}
        }

    # ==========================================
    # 🎯 INTENT DETECTION (FIXED ORDER)
    # ==========================================

    # -------------------------------
    # 🔍 SPECIFIC MACHINE QUERY (FIRST)
    # -------------------------------
    for m in analyzed:
        if m["machine_id"].lower() in query_lower:

            issue = (
                m["root_cause"][0]["issue"]
                if m.get("root_cause") else "unknown cause"
            )

            # ✅ WHY intent
            if any(x in query_lower for x in ["why", "reason", "cause"]):
                return {
                    "answer": (
                        f"{m['machine_id']} is degrading due to {issue}. "
                        f"Failure risk is {round(m.get('prediction',0)*100)}% "
                        f"with RUL {m.get('rul_cycles')} cycles "
                        f"({m.get('rul_time')})."
                    )
                }

            # ✅ STATUS intent
            return {
                "answer": (
                    f"{m['machine_id']} risk is {round(m.get('prediction',0)*100)}% "
                    f"due to {issue}. "
                    f"RUL: {m.get('rul_cycles')} cycles ({m.get('rul_time')})."
                )
            }

    # -------------------------------
    # 🛠 MAINTENANCE DECISION
    # -------------------------------
    if any(x in query_lower for x in [
        "maintain", "maintenance", "which machine", "priority"
    ]):

        if analyzed_sorted:
            top = analyzed_sorted[0]

            issue = (
                top["root_cause"][0]["issue"]
                if top.get("root_cause") else "unknown issue"
            )

            return {
                "answer": (
                    f"🔧 Maintain {top['machine_id']} first "
                    f"(risk {round(top.get('prediction',0)*100)}%). "
                    f"Cause: {issue}. "
                    f"RUL: {top.get('rul_cycles')} cycles."
                )
            }

    # -------------------------------
    # ⚠ FAILURE RANKING (FIXED)
    # -------------------------------
    if any(x in query_lower for x in ["highest", "most", "top"]):
        return {
            "answer": (
                f"{highest.get('machine_id')} has highest failure risk "
                f"({round(highest.get('prediction',0)*100)}%)."
            )
        }

    # -------------------------------
    # 🔮 FUTURE PREDICTION (LSTM)
    # -------------------------------
    if "future" in query_lower or "next" in query_lower:

        if LSTM_AVAILABLE:
            try:
                sequence = [
                    [
                        m["temperature"],
                        m["torque"],
                        m["tool_wear"],
                        m["vibration_index"]
                    ]
                    for m in machines
                ]

                prediction = predict_future(sequence)

                return {
                    "answer": (
                        f"📈 Future trend shows temperature reaching {prediction}°C, "
                        f"indicating potential degradation."
                    )
                }

            except Exception as e:
                print("❌ LSTM ERROR:", e)

        return {
            "answer": "Future prediction unavailable (LSTM not ready)."
        }

    # ==========================================
    # 🔍 ROOT CAUSE (FOR LLM)
    # ==========================================

    root_causes = highest.get("root_cause", [])

    root_cause_text = (
        "\n".join([
            f"- {c.get('issue')} ({round(c.get('confidence',0)*100)}%)"
            for c in root_causes if c.get("confidence", 0) > 0.3
        ])
        if root_causes else "No major issue"
    )

    # ==========================================
    # 🧠 FULL CONTEXT
    # ==========================================

    machine_lines = []

    for m in analyzed:
        machine_lines.append(
            f"{m['machine_id']} | "
            f"{round(m.get('prediction',0)*100)}% | "
            f"{m.get('health_status')}"
        )

    context = f"""
Machines:
{chr(10).join(machine_lines)}

Top Machine:
{highest.get('machine_id')}

Root Cause:
{root_cause_text}

RUL:
{highest.get('rul_cycles')} cycles
"""

    # ==========================================
    # 🤖 LLM RESPONSE
    # ==========================================

    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an industrial AI decision agent.

Rules:
- Give actionable insight
- Mention machine ID
- Explain cause
- Be concise (1-2 lines)
- If specific machine is asked, focus only on that"""
                },
                {
                    "role": "user",
                    "content": f"{context}\n\nQuestion: {query}"
                }
            ],
            options={"temperature": 0.3}
        )

        answer = response.get("message", {}).get("content")

    except Exception as e:
        print("❌ LLM ERROR:", e)
        answer = None

    # ==========================================
    # 🛡 FINAL FALLBACK
    # ==========================================

    if not answer:
        answer = (
            f"{highest.get('machine_id')} has highest risk "
            f"({round(highest.get('prediction',0)*100)}%)."
        )

    print("✅ ANSWER:", answer)

    return {"answer": answer}