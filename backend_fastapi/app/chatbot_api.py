# ==========================================
# 🤖 INDUSTRIAL AI CHATBOT (FINAL PRODUCTION)
# FAST + RAG + REAL-TIME + REASONING
# ==========================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend_fastapi.database.database import get_db
from backend_fastapi.chatbot.intent_parser import (
    parse_intent,
    extract_machine,
    extract_time
)

from backend_fastapi.chatbot.history_tools import (
    get_recent_events,
    get_machine_state_at_time
)

from backend_fastapi.app.state import LIVE_MACHINES

from backend_fastapi.chatbot.reasoning_engine import (
    generate_root_cause,
    compare_machines
)

from backend_fastapi.chatbot.llm_client import generate_llm_response

from backend_fastapi.chatbot.memory import (
    add_to_memory,
    get_memory_context
)

from backend_fastapi.chatbot.analysis_agent import analyze_patterns
from backend_fastapi.chatbot.prediction_agent import predict_failure_risk

from vectordb.semantic_retriever import retrieve_similar_context

router = APIRouter()

CACHE = {}


def respond(question, response):
    CACHE[question] = response
    add_to_memory(question, response)
    return {"response": response}


@router.post("/chat")
def chat(payload: dict, db: Session = Depends(get_db)):

    try:
        question = payload.get("message", "").strip()

        if not question:
            return {"response": "Empty query"}

        if question in CACHE:
            return {"response": CACHE[question]}

        # FOLLOW-UP HANDLING
        if question.lower() in ["why", "why?", "reason?"]:
            memory = get_memory_context()
            if memory:
                question = memory.split("\n")[0].replace("Q: ", "")

        intent = parse_intent(question)
        machine_id = extract_machine(question)
        query_time = extract_time(question)

        machine = LIVE_MACHINES.get(machine_id) if machine_id else None

        # ==========================================
        # 🔥 HARD ROUTING FOR COMPARISON (CRITICAL)
        # ==========================================
        q_lower = question.lower()
        if any(x in q_lower for x in [
            "which machine", "which is",
            "most critical", "worst",
            "healthiest", "best"
        ]):
            return respond(question, compare_machines(LIVE_MACHINES))

        # ==========================================
        # ⏱ TIME QUERY
        # ==========================================
        if intent["type"] in ["metric", "historical"] and machine_id and query_time:

            try:
                log = get_machine_state_at_time(db, machine_id, query_time)

                if log:
                    return respond(
                        question,
                        f"{machine_id} at {query_time} → "
                        f"{log.temperature:.2f}°C | "
                        f"Risk {(log.failure_probability or 0)*100:.0f}%"
                    )

                return respond(question, "No data for that time")

            except Exception as e:
                print("TIME ERROR:", e)
                return respond(question, "Error retrieving historical data")

        # ==========================================
        # 📊 METRIC HANDLING
        # ==========================================
        if intent["type"] == "metric":

            if not LIVE_MACHINES:
                return respond(question, "No live machine data available")

            try:
                metric = intent.get("metric")

                if machine_id and machine_id in LIVE_MACHINES:
                    m = LIVE_MACHINES[machine_id]
                    value = m.get(metric)

                    if value is None:
                        return respond(
                            question,
                            f"{metric} not available for {machine_id}"
                        )

                    return respond(
                        question,
                        f"{machine_id} {metric.replace('_',' ')} = {value:.2f}"
                    )

                best = max(
                    LIVE_MACHINES.values(),
                    key=lambda x: x.get(metric, 0)
                )

                return respond(
                    question,
                    f"{best['machine_id']} highest {metric.replace('_',' ')} "
                    f"({best.get(metric,0):.2f})"
                )

            except Exception as e:
                print("METRIC ERROR:", e)
                return respond(question, "Error processing metric query")

        # ==========================================
        # 📊 COMPARISON (FIXED 🔥)
        # ==========================================
        if intent["type"] == "comparison":

            if not LIVE_MACHINES:
                return respond(question, "No live machine data available")

            try:
                return respond(question, compare_machines(LIVE_MACHINES))
            except Exception as e:
                print("COMPARISON ERROR:", e)
                return respond(question, "Unable to compare machines")

        # ==========================================
        # 🧠 ROOT CAUSE (ALIGNED WITH SYSTEM 🔥)
        # ==========================================
        if intent["type"] == "root_cause" and machine:

            try:
                # ======================================
                # ✅ 1. USE ANALYZER ROOT CAUSE (PRIMARY)
                # ======================================
                root_causes = machine.get("root_cause", [])
                alerts = machine.get("alerts", [])
                ai_reason = machine.get("ai_reason", "")

                reasons = []

                # 🔴 structured root causes
                if root_causes:
                    for cause in root_causes:
                        issue = cause.get("issue")
                        if issue:
                            reasons.append(issue)

                # 🟡 alerts fallback
                if not reasons and alerts:
                    reasons = [a["message"] for a in alerts]

                # 🔵 SHAP explanation fallback
                if not reasons and ai_reason:
                    reasons.append(ai_reason)

                # ======================================
                # ❌ LAST RESORT (OLD LOGIC)
                # ======================================
                if not reasons:
                    reasons.append(generate_root_cause(machine_id, machine))

                # ======================================
                # 🧠 ADD INSIGHTS + PREDICTION
                # ======================================
                insights = ", ".join(analyze_patterns(machine))
                prediction = predict_failure_risk(machine)

                return respond(
                    question,
                    f"{machine_id}: {', '.join(reasons)} | {insights} | {prediction}"
                )

            except Exception as e:
                print("ROOT ERROR:", e)

                # ==========================================
                # 🕒 HISTORY
                # ==========================================
                if intent["type"] == "historical":
                    try:
                        logs = get_recent_events(db, minutes=2)[-5:]

                        if not logs:
                            return respond(question, "No historical data")

                        summary = [
                            f"{l.machine_id}: T={l.temperature:.1f} "
                            f"V={l.vibration_index:.2f} "
                            f"R={l.failure_probability:.2f}"
                            for l in logs
                        ]

                        return respond(question, "\n".join(summary))

                    except Exception as e:
                        print("HISTORY ERROR:", e)

                # ==========================================
                # 📚 RAG
                # ==========================================
                if intent["type"] in ["failure_analysis", "general"]:
                    try:
                        rag = retrieve_similar_context(question)

                        if rag:
                            prompt = f"""
        Answer in 1 short sentence.

        Context:
        {rag}

        Q: {question}
        """
                            llm = generate_llm_response(prompt)
                            return respond(question, llm)

                    except Exception as e:
                        print("RAG ERROR:", e)

        # ==========================================
        # 🤖 FINAL LLM
        # ==========================================
        context = ""

        if machine:
            context = (
                f"{machine_id}: T={machine.get('temperature',0):.1f}, "
                f"V={machine.get('vibration_index',0):.2f}, "
                f"R={machine.get('prediction',0):.2f}"
            )

        memory = get_memory_context()

        prompt = f"""
Answer in 1 short sentence.

Q: {question}
Data: {context}
Memory: {memory}
"""

        return respond(question, generate_llm_response(prompt))

    except Exception as e:
        print("🔥 CRITICAL ERROR:", e)
        return {
            "response": "System running but encountered an issue. Try again."
        }