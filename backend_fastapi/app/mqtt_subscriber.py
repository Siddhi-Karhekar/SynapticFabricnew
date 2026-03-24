from backend_fastapi.app.state import LIVE_MACHINES

def on_message(client, userdata, msg):

    data = json.loads(msg.payload)

    mid = data.get("machine_id")

    if not mid:
        return

    LIVE_MACHINES[mid] = {
        "machine_id": mid,
        "temperature": data.get("temperature", 0),
        "vibration_index": data.get("vibration_index", 0),
        "tool_wear": data.get("tool_wear", 0),
        "torque": data.get("torque", 0),
        "prediction": data.get("prediction", 0),
        "health_status": data.get("health_status", "Unknown")
    }