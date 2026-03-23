from digital_twin.simulator import MACHINE_MEMORY

# 🔥 SAME NAMES AS FRONTEND
MACHINE_INFO = {
    "M_1": "CNC Milling Machine (Engine Block Production)",
    "M_2": "CNC Drilling Machine (Cylinder Head)",
    "M_3": "CNC Lathe Machine (Shaft Manufacturing)"
}


def get_machine_context():

    context = ""

    for machine_id, state in MACHINE_MEMORY.items():

        machine_name = MACHINE_INFO.get(machine_id, machine_id)

        temperature = 295 + state["vibration_index"] * 10

        context += f"""
Machine: {machine_name}

Temperature: {round(temperature,2)} °C
Tool Wear: {round(state['tool_wear']*100,1)} %
Vibration Index: {state['vibration_index']}
Anomaly Score: {state['anomaly_score']}

"""

    return context