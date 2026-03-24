# ==========================================
# 📊 RAG SERVICE (OPTIMIZED FOR SPEED + LLM)
# ==========================================

from backend_fastapi.chatbot.history_tools import (
    get_recent_events,
    detect_failures,
    summarize_machine_behavior,
    build_timeline,
)


# ==========================================
# 🔴 BUILD CONTEXT FROM DATABASE (OPTIMIZED)
# ==========================================
def build_context_from_db(db, machine_id=None, minutes=2, max_logs=15):

    logs = get_recent_events(db, minutes=minutes)

    if not logs:
        return "No historical data."

    # ==========================================
    # 🎯 FILTER BY MACHINE (BIG SPEED BOOST)
    # ==========================================
    if machine_id:
        logs = [l for l in logs if l.machine_id == machine_id]

    # 🔥 LIMIT LOG SIZE
    logs = logs[-max_logs:]

    # ==========================================
    # 🔴 DETECT FAILURES
    # ==========================================
    failures = detect_failures(logs)

    # ==========================================
    # 🔴 SUMMARY
    # ==========================================
    summary = summarize_machine_behavior(logs)

    # ==========================================
    # 🔴 TIMELINE (SHORTENED)
    # ==========================================
    timeline_lines = []

    for log in logs[-8:]:  # 🔥 only last 8 events
        timeline_lines.append(
            f"{log.machine_id} T={log.temperature:.1f} "
            f"V={log.vibration_index:.2f} "
            f"R={log.failure_probability:.2f}"
        )

    timeline = "\n".join(timeline_lines)

    # ==========================================
    # 🔴 BUILD CONTEXT STRING (COMPACT)
    # ==========================================
    context_parts = []

    # TIMELINE
    context_parts.append("TIMELINE:")
    context_parts.append(timeline)

    # FAILURES (ONLY LAST 3)
    if failures:
        context_parts.append("FAILURES:")
        for f in failures[-3:]:
            context_parts.append(
                f"{f.machine_id} T={f.temperature:.1f} "
                f"V={f.vibration_index:.2f} "
                f"R={f.failure_probability:.2f}"
            )

    # SUMMARY (SHORT)
    context_parts.append("SUMMARY:")
    for m, data in summary.items():
        context_parts.append(
            f"{m}: T={data['max_temp']:.1f} "
            f"V={data['max_vibration']:.2f} "
            f"R={data['max_failure']:.2f}"
        )

    # FINAL CONTEXT
    context = "\n".join(context_parts)

    return context


# ==========================================
# 🔴 BUILD LIVE CONTEXT (OPTIMIZED)
# ==========================================
def build_live_context(live_data: dict, machine_id=None):

    if not live_data:
        return "No live data."

    lines = []

    # 🎯 FILTER SINGLE MACHINE (CRITICAL)
    if machine_id and machine_id in live_data:
        m = live_data[machine_id]

        return (
            f"{machine_id}: "
            f"T={m.get('temperature', 0):.1f}, "
            f"V={m.get('vibration_index', 0):.2f}, "
            f"W={m.get('tool_wear', 0):.2f}, "
            f"R={m.get('prediction', 0):.2f}, "
            f"H={m.get('health_status', 'Unknown')}"
        )

    # 🔴 OTHERWISE → ALL MACHINES (LIMITED)
    for m_id, m in list(live_data.items())[:3]:  # 🔥 limit to 3 machines
        lines.append(
            f"{m_id}: "
            f"T={m.get('temperature', 0):.1f}, "
            f"V={m.get('vibration_index', 0):.2f}, "
            f"R={m.get('prediction', 0):.2f}"
        )

    return "\n".join(lines)


# ==========================================
# 🔴 SMART CONTEXT BUILDER (USED BY CHATBOT)
# ==========================================
def build_smart_context(question, machine_id, db, live_data):

    live_context = build_live_context(live_data, machine_id)
    db_context = build_context_from_db(db, machine_id)

    context = f"""
QUESTION:
{question}

LIVE:
{live_context}

HISTORY:
{db_context}
"""

    return context.strip()