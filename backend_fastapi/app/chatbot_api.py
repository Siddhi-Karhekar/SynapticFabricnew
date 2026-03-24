# ==========================================
# 🤖 INDUSTRIAL AI CHATBOT (OPTIMIZED)
# ==========================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend_fastapi.database.database import get_db
from backend_fastapi.chatbot.intent_parser import parse_intent, extract_machine
from backend_fastapi.chatbot.history_tools import get_recent_events
from backend_fastapi.app.state import LIVE_MACHINES
from backend_fastapi.chatbot.reasoning_engine import (
    generate_root_cause,
    compare_machines
)
from backend_fastapi.chatbot.llm_client import generate_llm_response

router = APIRouter()


# ==========================================
# ⚡ MINIMAL CONTEXT BUILDER (HIGH PERFORMANCE)
# ==========================================
def build_minimal_context(question: str, machine_id: str, db: Session) -> str:
    """
    Builds a compact, relevant context for LLM.
    Designed for phi3-mini → minimal tokens, max signal.
    """

    context_parts = []

    # ==========================================
    # 🔴 LIVE MACHINE CONTEXT (PRIMARY SIGNAL)
    # ==========================================
    if machine_id and machine_id in LIVE_MACHINES:
        m = LIVE_MACHINES[machine_id]

        context_parts.append(
            f"{machine_id}: "
            f"T={m.get('temperature', 0):.1f}, "
            f"V={m.get('vibration_index', 0):.2f}, "
            f"W={m.get('tool_wear', 0):.2f}, "
            f"R={m.get('prediction', 0):.2f}, "
            f"H={m.get('health_status', 'Unknown')}"
        )

    # ==========================================
    # 🔴 SHORT HISTORY (LAST FEW EVENTS ONLY)
    # ==========================================
    try:
        logs = get_recent_events(db, minutes=2)

        # 🔥 only last 3 entries (CRITICAL FOR SPEED)
        for log in logs[-3:]:
            context_parts.append(
                f"{log.machine_id}: "
                f"T={log.temperature:.1f}, "
                f"V={log.vibration_index:.2f}, "
                f"R={log.failure_probability:.2f}, "
                f"H={log.health_status}"
            )
    except Exception:
        context_parts.append("History unavailable")

    return "\n".join(context_parts)


# ==========================================
# ⚡ PROMPT BUILDER (STRICT + SHORT OUTPUT)
# ==========================================
def build_prompt(question: str, context: str) -> str:
    """
    Strict prompt to force short, precise answers.
    """

    return f"""
You are a senior industrial reliability engineer.

Rules:
- Answer in MAX 2 sentences
- Be direct and technical
- No explanations unless necessary
- No filler text

Question:
{question}

Data:
{context}
""".strip()


# ==========================================
# 🤖 CHAT ENDPOINT
# ==========================================
@router.post("/chat")
def chat(payload: dict, db: Session = Depends(get_db)):

    question = payload.get("message", "").strip()

    if not question:
        return {"response": "Empty query"}

    intent = parse_intent(question)
    machine_id = extract_machine(question)

    # ==========================================
    # ⚡ FAST PATHS (NO LLM → INSTANT RESPONSE)
    # ==========================================

    if intent["type"] == "metric" and machine_id:
        m = LIVE_MACHINES.get(machine_id)

        if not m:
            return {"response": f"{machine_id} not available"}

        return {
            "response": (
                f"{machine_id}: {m['temperature']:.1f}°C | "
                f"Risk {m['prediction']*100:.0f}%"
            )
        }

    if intent["type"] == "comparison":
        return {"response": compare_machines(LIVE_MACHINES)}

    if intent["type"] == "maintenance":
        return {"response": compare_machines(LIVE_MACHINES)}

    # ==========================================
    # 🧠 ROOT CAUSE (HYBRID: RULE + LLM)
    # ==========================================
    if intent["type"] == "root_cause" and machine_id:
        m = LIVE_MACHINES.get(machine_id)

        if not m:
            return {"response": "No data available"}

        # ⚡ RULE-BASED (FAST + RELIABLE)
        rule_response = generate_root_cause(machine_id, m)

        # ⚡ MINIMAL CONTEXT FOR LLM
        context = build_minimal_context(question, machine_id, db)
        prompt = build_prompt(question, context)

        llm_response = generate_llm_response(prompt)

        return {
            "response": f"{rule_response}. {llm_response}"
        }

    # ==========================================
    # 📜 HISTORICAL / FAILURE ANALYSIS
    # ==========================================
    if intent["type"] in ["historical", "failure_analysis"]:
        context = build_minimal_context(question, machine_id, db)
        prompt = build_prompt(question, context)

        llm_response = generate_llm_response(prompt)

        return {"response": llm_response}

    # ==========================================
    # 🤖 GENERAL (LLM FALLBACK)
    # ==========================================
    context = build_minimal_context(question, machine_id, db)
    prompt = build_prompt(question, context)

    llm_response = generate_llm_response(prompt)

    return {"response": llm_response}