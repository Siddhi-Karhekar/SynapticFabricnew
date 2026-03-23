# backend_fastapi/chatbot/rag_service.py

from backend_fastapi.chatbot.history_tools import (
    get_recent_events,
    detect_failures,
    summarize_machine_behavior,
    build_timeline,
)


# ==========================================
# BUILD CONTEXT FROM DATABASE
# ==========================================
def build_context_from_db(db):

    logs = get_recent_events(db, minutes=10)

    if not logs:
        return "No historical data available."

    failures = detect_failures(logs)
    summary = summarize_machine_behavior(logs)
    timeline = build_timeline(logs)

    context = "================ FACTORY HISTORY ================\n\n"

    # 🔴 TIMELINE
    context += "RECENT TIMELINE:\n"
    context += timeline + "\n\n"

    # 🔴 FAILURES
    context += "CRITICAL EVENTS:\n"
    if failures:
        for f in failures[-10:]:
            context += (
                f"- {f.machine_id} at {f.timestamp.strftime('%H:%M:%S')} | "
                f"Temp={f.temperature:.1f}, Vib={f.vibration_index:.3f}, "
                f"Risk={f.failure_probability:.2f}\n"
            )
    else:
        context += "No critical failures detected.\n"

    context += "\n"

    # 🔴 SUMMARY
    context += "MACHINE SUMMARY:\n"
    for m, data in summary.items():
        context += (
            f"- {m}: MaxTemp={data['max_temp']:.1f}, "
            f"MaxVibration={data['max_vibration']:.3f}, "
            f"MaxFailure={data['max_failure']:.2f}\n"
        )

    context += "\n===============================================\n"

    return context