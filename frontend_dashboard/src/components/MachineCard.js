import React, { useState } from "react";
import "./MachineCard.css";
import { MACHINE_INFO } from "../utils/machineInfo";

export default function MachineCard({ machine, onMaintain }) {

  const [maintaining, setMaintaining] = useState(false);

  const info = MACHINE_INFO[machine.machine_id] || {};
  const name = info.name || machine.machine_id;
  const process = info.process || "Unknown Process";

  // =========================
  // STATUS COLORS
  // =========================
  const STATUS_COLORS = {
    Healthy: "#00e676",
    Warning: "#ffeb3b",
    Critical: "#ff5252"
  };

  const getStatusColor = () =>
    STATUS_COLORS[machine.health_status] || "#ff5252";

  // =========================
  // 🔥 GLOW CLASS LOGIC
  // =========================
  const getCardClass = () => {
    let base = "machine-card";

    if (machine.health_status === "Critical") {
      return `${base} critical-glow`;
    }

    if (machine.health_status === "Warning") {
      return `${base} warning-glow`;
    }

    return base;
  };

  // =========================
  // 🔧 MAINTENANCE
  // =========================
  const handleMaintainClick = async () => {
    setMaintaining(true);
    try {
      await onMaintain(machine.machine_id);
    } catch (e) {
      console.error("Maintenance error:", e);
    }
    setMaintaining(false);
  };

  // =========================
  // 🧠 SAFE VALUES
  // =========================
  const temp = machine.temperature ?? 0;
  const torque = machine.torque ?? 0;
  const wear = machine.tool_wear ?? 0;
  const vib = machine.vibration_index ?? 0;
  const prediction = machine.prediction ?? 0;

  const rulCycles = machine.rul_cycles ?? null;
  const rulTime = machine.rul_time ?? null;

  const rulColor =
    rulCycles === null
      ? "#999"
      : rulCycles < 50
      ? "#ff5252"
      : rulCycles < 100
      ? "#ffeb3b"
      : "#00e676";

  return (
    <div className={getCardClass()}>

      {/* NAME */}
      <h3>{name}</h3>
      <p style={{ fontSize: "12px", opacity: 0.7 }}>
        {process}
      </p>

      {/* STATUS */}
      <p style={{ color: getStatusColor(), fontWeight: "bold" }}>
        {machine.health_status}
      </p>

      {/* METRICS */}
      <div style={{ fontSize: "14px", lineHeight: "1.6" }}>
        <p>🌡 Temp: {temp.toFixed(2)} °C</p>
        <p>⚙ Load: {torque.toFixed(2)} Nm</p>
        <p>🛠 Tool Wear: {(wear * 100).toFixed(1)}%</p>
        <p>📉 Vibration: {vib.toFixed(3)}</p>
      </div>

      {/* FAILURE */}
      <p>
        ⚠ Failure Risk: {(prediction * 100).toFixed(0)}%
      </p>

      {/* ⏳ RUL */}
      <p style={{ color: rulColor, fontWeight: "bold" }}>
        ⏳ RUL: {rulCycles !== null ? `${rulCycles} cycles` : "--"}
      </p>

      <p style={{ fontSize: "12px", opacity: 0.7 }}>
        ⏱ {rulTime ?? "--"}
      </p>

      {/* 📊 ML CONFIDENCE */}
      <p>
        📊 ML Confidence: {(prediction * 100).toFixed(1)}%
      </p>

      {/* 📊 RISK BAR */}
      <div style={{
        height: 6,
        background: "#333",
        borderRadius: 4,
        marginTop: 6
      }}>
        <div style={{
          width: `${prediction * 100}%`,
          height: "100%",
          background:
            prediction > 0.7 ? "#ff5252" :
            prediction > 0.4 ? "#ffeb3b" :
            "#00e676",
          borderRadius: 4,
          transition: "all 0.3s ease"
        }} />
      </div>

      {/* 🔧 MAINTENANCE BUTTON */}
      <button
        onClick={handleMaintainClick}
        style={btnPrimary}
        disabled={maintaining}
      >
        {maintaining ? "Maintaining..." : "🔧 Perform Maintenance"}
      </button>

      {/* 🔍 INSPECTION */}
      <div style={inspectBox}>
        <strong>Inspection Results:</strong>

        {(!machine.diagnosis || machine.diagnosis.length === 0) ? (
          <div style={smallText}>✅ No issues detected</div>
        ) : (
          machine.diagnosis.map((c, i) => (
            <div key={i} style={{ marginTop: "6px" }}>
              <div>⚠ {c.issue}</div>

              <div style={smallText}>
                Confidence: {((c.confidence ?? 0) * 100).toFixed(0)}%
              </div>

              <div style={smallText}>
                {c.reason}
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}

// =====================
// STYLES
// =====================

const btnPrimary = {
  marginTop: "10px",
  padding: "8px",
  background: "#1976d2",
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer"
};

const inspectBox = {
  marginTop: "10px",
  padding: "8px",
  background: "#222",
  borderRadius: "6px",
  fontSize: "13px"
};

const smallText = {
  fontSize: "11px",
  opacity: 0.7
};