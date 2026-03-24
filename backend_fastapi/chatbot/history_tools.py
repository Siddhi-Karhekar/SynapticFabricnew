# backend_fastapi/chatbot/history_tools.py

from sqlalchemy.orm import Session
from backend_fastapi.database.models import MachineLog
from datetime import datetime, timedelta


# ==========================================
# GET RECENT LOGS FROM DB
# ==========================================
def get_recent_events(db: Session, minutes: int = 10):
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)

    logs = (
        db.query(MachineLog)
        .filter(MachineLog.timestamp >= cutoff)
        .order_by(MachineLog.timestamp.asc())
        .all()
    )

    return logs


# ==========================================
# DETECT FAILURES
# ==========================================
def detect_failures(logs):
    failures = []

    for log in logs:
        if (
            log.health_status == "Critical"
            or (log.failure_probability and log.failure_probability > 0.7)
        ):
            failures.append(log)

    return failures


# ==========================================
# SUMMARIZE MACHINE BEHAVIOR
# ==========================================
def summarize_machine_behavior(logs):
    summary = {}

    for log in logs:
        m = log.machine_id

        if m not in summary:
            summary[m] = {
                "max_temp": log.temperature,
                "max_vibration": log.vibration_index,
                "max_failure": log.failure_probability or 0,
            }

        summary[m]["max_temp"] = max(summary[m]["max_temp"], log.temperature)
        summary[m]["max_vibration"] = max(
            summary[m]["max_vibration"], log.vibration_index
        )
        summary[m]["max_failure"] = max(
            summary[m]["max_failure"], log.failure_probability or 0
        )

    return summary


# ==========================================
# BUILD TIMELINE STRING
# ==========================================
def build_timeline(logs):
    lines = []

    for log in logs[-30:]:  # last 30 events
        lines.append(
            f"{log.timestamp.strftime('%H:%M:%S')} | {log.machine_id} | "
            f"T={log.temperature:.1f} | Vib={log.vibration_index:.3f} | "
            f"Risk={log.failure_probability:.2f} | {log.health_status}"
        )

    return "\n".join(lines)
    from datetime import datetime

def get_machine_state_at_time(db, machine_id, time_str):
    try:
        target_time = datetime.strptime(time_str, "%H:%M")

        logs = (
            db.query(MachineLog)
            .filter(MachineLog.machine_id == machine_id)
            .all()
        )

        if not logs:
            return None

        # 🔥 find closest timestamp
        closest = min(
            logs,
            key=lambda l: abs(
                l.timestamp.replace(year=1900, month=1, day=1) - target_time
            )
        )

        return closest

    except Exception as e:
        return None