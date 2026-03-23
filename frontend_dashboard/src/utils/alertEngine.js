export function generateAlert(machine, health) {
  if (!machine) return null;

  if (health < 40) {
    return {
      level: "HIGH",
      message: `${machine.machine_id} critical risk detected`,
    };
  }

  if (machine.vibration > 0.8) {
    return {
      level: "WARNING",
      message: `${machine.machine_id} vibration increasing`,
    };
  }

  if (machine.process_temp > 312) {
    return {
      level: "WARNING",
      message: `${machine.machine_id} overheating trend`,
    };
  }

  return null;
}