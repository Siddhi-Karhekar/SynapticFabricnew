export function calculateHealth(machine) {
  if (!machine) return 100;

  let score = 100;

  // temperature penalty
  if (machine.process_temp > 310) score -= 25;
  else if (machine.process_temp > 305) score -= 10;

  // tool wear penalty
  score -= machine.tool_wear * 0.4;

  // vibration penalty
  score -= machine.vibration * 20;

  return Math.max(0, Math.round(score));
}

export function healthColor(score) {
  if (score > 75) return "#2ecc71"; // green
  if (score > 45) return "#f39c12"; // orange
  return "#e74c3c"; // red
}

export function healthLabel(score) {
  if (score > 75) return "Healthy";
  if (score > 45) return "Warning";
  return "High Risk";
}