# digital_twin/simulator.py

import random

# ==========================================
# MACHINE MEMORY (STATEFUL) ✅ REQUIRED
# ==========================================

MACHINE_MEMORY = {
    "M_1": {
        "tool_wear": 0.12,
        "vibration_index": 0.30,
        "temperature": 295,
        "torque": 40
    },
    "M_2": {
        "tool_wear": 0.08,
        "vibration_index": 0.18,
        "temperature": 295,
        "torque": 40
    },
    "M_3": {
        "tool_wear": 0.10,
        "vibration_index": 0.15,
        "temperature": 295,
        "torque": 42
    },
}

# ==========================================
# HELPER
# ==========================================

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))


# ==========================================
# DIGITAL TWIN ENGINE
# ==========================================

def run_digital_twin():

    machines = []

    for machine_id, state in MACHINE_MEMORY.items():

        # ======================================
        # 🔵 VERY LIGHT BASE DRIFT (SLIGHTLY SLOWER)
        # ======================================
        state["tool_wear"] += random.uniform(0.00007, 0.0002)
        state["vibration_index"] += random.uniform(0.00003, 0.00012)

        # ======================================
        # 🔵 CNC MILLING (M1)
        # ======================================
        if machine_id == "M_1":

            state["vibration_index"] += random.uniform(0.0015, 0.004)
            state["tool_wear"] += state["vibration_index"] * 0.002

            if random.random() < 0.02:
                state["vibration_index"] += random.uniform(0.02, 0.06)

            state["temperature"] += random.uniform(-0.05, 0.1)

        # ======================================
        # 🟡 CNC DRILLING (M2)
        # ======================================
        elif machine_id == "M_2":

            state["temperature"] += random.uniform(0.08, 0.25)

            if state["temperature"] > 303:
                state["tool_wear"] += 0.001

            if state["temperature"] > 310:
                state["temperature"] -= random.uniform(0.3, 0.7)

            state["vibration_index"] += random.uniform(0.00008, 0.0002)

        # ======================================
        # 🟢 CNC LATHE (M3)
        # ======================================
        elif machine_id == "M_3":

            state["torque"] = 40 + state["tool_wear"] * 32
            state["tool_wear"] += random.uniform(0.0002, 0.0007)

            if random.random() < 0.015:
                state["torque"] += random.uniform(5, 9)

            state["vibration_index"] *= 0.992
            state["temperature"] += random.uniform(-0.05, 0.1)

        # ======================================
        # 🌡 GLOBAL THERMAL STABILIZATION
        # ======================================
        if state["temperature"] > 300:
            state["temperature"] -= random.uniform(0.05, 0.2)

        # ======================================
        # 🔁 NATURAL RECOVERY
        # ======================================
        if random.random() < 0.1:
            state["vibration_index"] *= 0.97

        if random.random() < 0.05:
            state["temperature"] -= random.uniform(0.1, 0.3)

        # ======================================
        # LIMITS
        # ======================================
        state["tool_wear"] = clamp(state["tool_wear"], 0, 1)
        state["vibration_index"] = clamp(state["vibration_index"], 0, 1)
        state["temperature"] = clamp(state["temperature"], 290, 330)
        state["torque"] = clamp(state["torque"], 35, 85)

        # ======================================
        # OUTPUT
        # ======================================
        machines.append({
            "machine_id": machine_id,
            "temperature": round(state["temperature"], 2),
            "torque": round(state["torque"], 2),
            "tool_wear": round(state["tool_wear"], 4),
            "vibration_index": round(state["vibration_index"], 4)
        })

    return machines