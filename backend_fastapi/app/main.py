from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import time
from datetime import datetime, timedelta

from digital_twin.simulator import run_digital_twin, MACHINE_MEMORY
from backend_fastapi.ai_engine.machine_analyzer import machine_analyzer
from backend_fastapi.app.chatbot_api import router as chatbot_router
from backend_fastapi.database.database import SessionLocal, get_db
from backend_fastapi.database.models import MachineLog
from backend_fastapi.chatbot.rag_service import build_context_from_db

app = FastAPI()

# ==========================================
# 🌐 CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)

# ==========================================
# 🔧 CONFIG
# ==========================================
MAINTENANCE_COOLDOWN = {}
COOLDOWN_TIME = 20

AUTO_MAINTENANCE_THRESHOLD = 0.75
ALERT_THRESHOLD = 0.4

LAST_CLEANUP = 0


# ==========================================
# 💾 SAVE MACHINE SNAPSHOT (EVERY SECOND)
# ==========================================
def save_machine_snapshot(machines):

    db = SessionLocal()

    try:
        for m in machines:
            log = MachineLog(
                machine_id=m.get("machine_id"),
                temperature=m.get("temperature"),
                torque=m.get("torque"),
                tool_wear=m.get("tool_wear"),
                vibration_index=m.get("vibration_index"),
                anomaly_score=m.get("anomaly_score", 0),
                health_status=m.get("health_status"),
                failure_probability=m.get("prediction", 0)
            )
            db.add(log)

        db.commit()

    except Exception as e:
        print("❌ DB SAVE ERROR:", e)

    finally:
        db.close()


# ==========================================
# 🧹 CLEAN OLD DATA
# ==========================================
def cleanup_old_data():

    db = SessionLocal()

    try:
        cutoff = datetime.utcnow() - timedelta(minutes=30)

        deleted = db.query(MachineLog).filter(
            MachineLog.timestamp < cutoff
        ).delete()

        db.commit()

        print(f"🧹 Cleaned {deleted} old records")

    except Exception as e:
        print("❌ CLEANUP ERROR:", e)

    finally:
        db.close()


# ==========================================
# 🌐 WEBSOCKET STREAM
# ==========================================
@app.websocket("/ws/machines")
async def stream(ws: WebSocket):

    await ws.accept()
    print("✅ WebSocket connected")

    global LAST_CLEANUP

    try:
        while True:

            # 🔵 DIGITAL TWIN
            machines = run_digital_twin()

            # 🔧 MAINTENANCE COOLDOWN
            for m in machines:
                mid = m["machine_id"]

                if mid in MAINTENANCE_COOLDOWN:

                    elapsed = time.time() - MAINTENANCE_COOLDOWN[mid]

                    if elapsed < COOLDOWN_TIME:

                        MACHINE_MEMORY[mid].update({
                            "tool_wear": 0.02,
                            "vibration_index": 0.15,
                            "temperature": 293,
                            "torque": 38
                        })

                        m.update({
                            "tool_wear": 0.02,
                            "vibration_index": 0.15,
                            "temperature": 293,
                            "torque": 38
                        })

                    else:
                        del MAINTENANCE_COOLDOWN[mid]

            # 🤖 AI ANALYSIS
            analyzed = machine_analyzer.analyze_machines(machines)

            # 💾 SAVE EVERY SECOND
            save_machine_snapshot(analyzed)

            # 🧹 CLEANUP
            if time.time() - LAST_CLEANUP > 60:
                cleanup_old_data()
                LAST_CLEANUP = time.time()

            # 🤖 AGENT LOGIC
            agent_alerts = []
            agent_actions = []

            for m in analyzed:
                mid = m["machine_id"]

                risk = max(
                    m.get("prediction", 0),
                    m.get("anomaly_score", 0)
                )

                # ALERT
                if risk > ALERT_THRESHOLD:
                    agent_alerts.append({
                        "machine_id": mid,
                        "level": "CRITICAL" if risk > 0.7 else "WARNING",
                        "message": f"Failure risk {round(risk*100)}%"
                    })

                # AUTO MAINTENANCE
                if risk > AUTO_MAINTENANCE_THRESHOLD:

                    if mid not in MAINTENANCE_COOLDOWN:

                        agent_actions.append({
                            "machine_id": mid,
                            "action": "AUTO_MAINTENANCE",
                            "status": "STARTING"
                        })

                        await asyncio.sleep(1.5)

                        MACHINE_MEMORY[mid].update({
                            "tool_wear": 0.02,
                            "vibration_index": 0.15,
                            "temperature": 293,
                            "torque": 38
                        })

                        MAINTENANCE_COOLDOWN[mid] = time.time()

                        agent_actions.append({
                            "machine_id": mid,
                            "action": "AUTO_MAINTENANCE",
                            "status": "SUCCESS"
                        })

            # 📊 ANALYTICS
            risks = [
                max(m.get("prediction", 0), m.get("anomaly_score", 0))
                for m in analyzed
            ]

            avg_risk = sum(risks) / len(risks)

            unstable = max(
                analyzed,
                key=lambda x: max(
                    x.get("prediction", 0),
                    x.get("anomaly_score", 0)
                )
            )

            analytics = {
                "plant_health_score": round((1 - avg_risk) * 100, 1),
                "most_unstable_machine": unstable["machine_id"],
                "total_machines": len(analyzed),
                "machines_needing_attention": [
                    m["machine_id"]
                    for m in analyzed
                    if m.get("health_status") != "Healthy"
                ]
            }

            # 📡 SEND
            await ws.send_json({
                "machines": analyzed,
                "factory_analytics": analytics,
                "agent_alerts": agent_alerts,
                "agent_actions": agent_actions
            })

            await asyncio.sleep(1)

    except Exception as e:
        print("❌ WebSocket error:", e)

    finally:
        print("🔌 WebSocket closed")


# ==========================================
# 🔧 MANUAL MAINTENANCE
# ==========================================
@app.post("/maintenance/{machine_id}")
def maintain(machine_id: str):

    if machine_id not in MACHINE_MEMORY:
        return {"status": "error"}

    MACHINE_MEMORY[machine_id].update({
        "tool_wear": 0.02,
        "vibration_index": 0.15,
        "temperature": 293,
        "torque": 38
    })

    MAINTENANCE_COOLDOWN[machine_id] = time.time()

    return {"status": "success"}


# ==========================================
# 📊 HISTORY API (🔥 FIXED — PER SECOND)
# ==========================================
@app.get("/history")
def get_history(minutes: int = 5):

    db = SessionLocal()

    try:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        records = (
            db.query(MachineLog)
            .filter(MachineLog.timestamp >= cutoff)
            .order_by(MachineLog.timestamp.asc())
            .all()
        )

        # 🔥 GROUP BY SECOND
        grouped = {}

        for r in records:
            key = r.timestamp.strftime("%H:%M:%S")

            if key not in grouped:
                grouped[key] = {
                    "time": key,
                    "M_1": None,
                    "M_2": None,
                    "M_3": None
                }

            grouped[key][r.machine_id] = r.temperature

        # 🔥 CONVERT TO LIST
        data = list(grouped.values())

        return data

    finally:
        db.close()


# ==========================================
# 🤖 CHAT WITH HISTORY (NEW 🔥)
# ==========================================
@app.post("/chat")
def chat(payload: dict, db: Session = Depends(get_db)):

    user_message = payload.get("message", "")

    if not user_message:
        return {"response": "No question provided"}

    # 🔥 BUILD CONTEXT FROM DB
    context = build_context_from_db(db)

    prompt = f"""
You are an Industrial AI Assistant.

Use the factory history below to answer.

{context}

Question: {user_message}

Explain root cause clearly.
"""

    # TEMP MOCK (replace with OpenAI)
    response = f"[AI]\n\n{prompt[:800]}"

    return {"response": response}