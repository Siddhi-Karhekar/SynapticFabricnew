from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
from datetime import datetime, timedelta

from digital_twin.simulator import run_digital_twin, MACHINE_MEMORY
from backend_fastapi.ai_engine.machine_analyzer import machine_analyzer
from backend_fastapi.app.chatbot_api import router as chatbot_router
from backend_fastapi.database.database import SessionLocal
from backend_fastapi.database.models import MachineLog

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)

# ==========================================
# 🔧 MAINTENANCE CONTROL
# ==========================================
MAINTENANCE_COOLDOWN = {}
COOLDOWN_TIME = 20

# ==========================================
# 🤖 AGENT CONFIG
# ==========================================
AUTO_MAINTENANCE_THRESHOLD = 0.75
ALERT_THRESHOLD = 0.4

# ==========================================
# 🧠 DB SAVE FUNCTION (1 SECOND LOGGING)
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
                anomaly_score=m.get("anomaly_score"),
                health_status=m.get("health_status"),
                failure_probability=m.get("prediction")
            )
            db.add(log)

        db.commit()

    finally:
        db.close()


# ==========================================
# 🧹 CLEANUP OLD DATA (PREVENT DB OVERLOAD)
# ==========================================
LAST_CLEANUP = 0

def cleanup_old_data():

    db = SessionLocal()

    try:
        cutoff = datetime.utcnow() - timedelta(minutes=30)

        db.query(MachineLog).filter(
            MachineLog.timestamp < cutoff
        ).delete()

        db.commit()

    finally:
        db.close()


# ==========================================
# 🌐 WEBSOCKET STREAM
# ==========================================
@app.websocket("/ws/machines")
async def stream(ws: WebSocket):

    await ws.accept()
    print("✅ WebSocket connected")
    print("🤖 Autonomous Agent Activated")

    global LAST_CLEANUP

    try:
        while True:

            # ======================================
            # 🔥 DIGITAL TWIN
            # ======================================
            machines = run_digital_twin()

            # ======================================
            # 🔧 COOLDOWN LOGIC
            # ======================================
            for m in machines:
                mid = m["machine_id"]

                if mid in MAINTENANCE_COOLDOWN:

                    elapsed = time.time() - MAINTENANCE_COOLDOWN[mid]

                    if elapsed < COOLDOWN_TIME:

                        MACHINE_MEMORY[mid]["tool_wear"] = 0.02
                        MACHINE_MEMORY[mid]["vibration_index"] = 0.15
                        MACHINE_MEMORY[mid]["temperature"] = 293
                        MACHINE_MEMORY[mid]["torque"] = 38

                        m["tool_wear"] = 0.02
                        m["vibration_index"] = 0.15
                        m["temperature"] = 293
                        m["torque"] = 38

                    else:
                        del MAINTENANCE_COOLDOWN[mid]

            # ======================================
            # 🤖 AI ANALYSIS
            # ======================================
            analyzed = machine_analyzer.analyze_machines(machines)

            # ======================================
            # 💾 SAVE EVERY SECOND (🔥 KEY CHANGE)
            # ======================================
            save_machine_snapshot(analyzed)

            # ======================================
            # 🧹 CLEANUP EVERY 60s
            # ======================================
            if time.time() - LAST_CLEANUP > 60:
                cleanup_old_data()
                LAST_CLEANUP = time.time()

            # ======================================
            # 🤖 AGENT LOGIC
            # ======================================
            agent_alerts = []
            agent_actions = []

            for m in analyzed:
                mid = m.get("machine_id")

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
                            "status": "STARTING",
                            "risk": round(risk, 3),
                            "timestamp": time.time()
                        })

                        await asyncio.sleep(1.5)

                        MACHINE_MEMORY[mid]["tool_wear"] = 0.02
                        MACHINE_MEMORY[mid]["vibration_index"] = 0.15
                        MACHINE_MEMORY[mid]["temperature"] = 293
                        MACHINE_MEMORY[mid]["torque"] = 38

                        MAINTENANCE_COOLDOWN[mid] = time.time()

                        agent_actions.append({
                            "machine_id": mid,
                            "action": "AUTO_MAINTENANCE",
                            "status": "SUCCESS",
                            "risk": round(risk, 3),
                            "timestamp": time.time()
                        })

            # ======================================
            # 📊 ANALYTICS
            # ======================================
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
                "most_unstable_machine": unstable.get("machine_id"),
                "total_machines": len(analyzed),
                "machines_needing_attention": [
                    m.get("machine_id")
                    for m in analyzed
                    if m.get("health_status") != "Healthy"
                ]
            }

            # ======================================
            # 📡 SEND
            # ======================================
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
        return {"status": "error", "message": "machine not found"}

    MACHINE_MEMORY[machine_id]["tool_wear"] = 0.02
    MACHINE_MEMORY[machine_id]["vibration_index"] = 0.15
    MACHINE_MEMORY[machine_id]["temperature"] = 293
    MACHINE_MEMORY[machine_id]["torque"] = 38

    MAINTENANCE_COOLDOWN[machine_id] = time.time()

    return {"status": "success", "machine": machine_id}


# ==========================================
# 📊 HISTORY API (FIXED GROUPING)
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

        data_map = {}

        for r in records:

            # 🔥 GROUP BY MINUTE (FIXES CHART)
            t = r.timestamp.strftime("%H:%M")

            if t not in data_map:
                data_map[t] = {
                    "time": t,
                    "M_1": None,
                    "M_2": None,
                    "M_3": None
                }

            data_map[t][r.machine_id] = r.temperature

        return list(data_map.values())

    finally:
        db.close()