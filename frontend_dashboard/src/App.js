import React, { useState, useEffect } from "react";
import useMachineStream from "./useMachineStream";

import MachineCard from "./components/MachineCard";
import FactoryTwin3D from "./components/FactoryTwin3D";
import TemperatureChart from "./components/TemperatureChart";
import AlertPanel from "./components/AlertPanel";
import Chatbot from "./components/Chatbot";

function App() {

  const {
    machines = {},
    factoryAnalytics = {},
    agentAlerts = [],
    agentActions = [],
    popupMessage
  } = useMachineStream();

  const [showChatbot, setShowChatbot] = useState(false);
  const [timeRange, setTimeRange] = useState(5);

  // ==========================================
  // 🔧 MANUAL MAINTENANCE
  // ==========================================
  const handleMaintain = async (machineId) => {
    try {
      const res = await fetch(
        `http://localhost:8000/maintenance/${machineId}`,
        { method: "POST" }
      );

      const data = await res.json();

      if (!data || data.status !== "success") {
        throw new Error("Invalid response");
      }

      console.log("✅ Manual maintenance success:", machineId);

    } catch (err) {
      console.error("❌ Maintenance error:", err);
      alert("Maintenance failed");
    }
  };

  return (
    <div style={styles.container}>

      <h1 style={styles.title}>
        🤖 Autonomous Industrial AI Control Center
      </h1>

      {/* ===================================== */}
      {/* 🏭 DIGITAL TWIN */}
      {/* ===================================== */}
      <FactoryTwin3D machines={machines} />

      {/* ===================================== */}
      {/* 🏭 MACHINE CARDS */}
      {/* ===================================== */}
      <div style={styles.grid}>
        {Object.values(machines).map((machine) => (
          <MachineCard
            key={machine.machine_id}
            machine={machine}
            onMaintain={handleMaintain}
          />
        ))}
      </div>

      {/* ===================================== */}
      {/* 📊 ANALYTICS */}
      {/* ===================================== */}
      <div style={styles.analytics}>
        <h2>📊 Factory Intelligence</h2>

        <div style={styles.analyticsGrid}>
          <div style={styles.card}>
            <h3>Plant Health Score</h3>
            <p>{factoryAnalytics.plant_health_score ?? "--"}%</p>
          </div>

          <div style={styles.card}>
            <h3>Most Unstable Machine</h3>
            <p>{factoryAnalytics.most_unstable_machine ?? "--"}</p>
          </div>

          <div style={styles.card}>
            <h3>Total Machines</h3>
            <p>{factoryAnalytics.total_machines ?? "--"}</p>
          </div>

          <div style={styles.card}>
            <h3>Machines Needing Attention</h3>
            <p>
              {(factoryAnalytics.machines_needing_attention || []).join(", ") || "--"}
            </p>
          </div>
        </div>
      </div>

  

      {/* ===================================== */}
      {/* 🤖 AGENT ALERTS */}
      {/* ===================================== */}
      <div style={styles.section}>
        <h2>🤖 Agent Alerts</h2>

        {agentAlerts.length === 0 ? (
          <p style={{ opacity: 0.6 }}>No agent alerts</p>
        ) : (
          agentAlerts.map((a, i) => (
            <div
              key={i}
              style={{
                ...styles.alertBox,
                background:
                  a.level === "CRITICAL"
                    ? "#ff1744"
                    : "#ff9100",
                animation:
                  a.level === "CRITICAL"
                    ? "blink 1s infinite"
                    : "none"
              }}
            >
              ⚠ {a.machine_id} → {a.message}
            </div>
          ))
        )}
      </div>

     

      {/* ===================================== */}
      {/* 📈 TEMPERATURE */}
      {/* ===================================== */}
      <div style={styles.section}>
        <h2>📈 Live Temperature</h2>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
        >
          <option value={1}>Last 1 min</option>
          <option value={5}>Last 5 min</option>
          <option value={10}>Last 10 min</option>
        </select>
        <TemperatureChart range={timeRange} />
      </div>

      {/* ===================================== */}
      {/* 🤖 CHATBOT */}
      {/* ===================================== */}
      <button
        style={styles.chatButton}
        onClick={() => setShowChatbot(!showChatbot)}
      >
        🤖 AI Assistant
      </button>

      {showChatbot && (
        <div style={styles.chatPopup}>
          <Chatbot />
        </div>
      )}

      {/* ===================================== */}
      {/* 🚀 AUTO-MAINTENANCE POPUP */}
      {/* ===================================== */}
      {popupMessage && (
        <div style={styles.popup}>
          {popupMessage}
        </div>
      )}

    </div>
  );
}

export default App;

//
// ==========================================
// 🎨 STYLES
// ==========================================
//

const styles = {
  container: {
    padding: "24px 40px",
    background: "radial-gradient(circle at top, #0f172a, #020617)",
    color: "white",
    minHeight: "100vh",
    fontFamily: "Inter, sans-serif",
  },

  title: {
    marginBottom: "25px",
    fontSize: "28px",
    fontWeight: "600",
    letterSpacing: "0.5px"
  },

  section: {
    marginTop: "35px",
  },

  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
    gap: "22px",
    marginTop: "25px",
  },

  analytics: {
    marginTop: "45px",
  },

  analyticsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "20px",
    marginTop: "15px",
  },

  card: {
    background: "linear-gradient(145deg, #111827, #020617)",
    padding: "18px",
    borderRadius: "14px",
    minWidth: "180px",
    boxShadow: "0 8px 30px rgba(0,0,0,0.6)",
    border: "1px solid rgba(255,255,255,0.05)",
    transition: "0.25s ease"
  },

  alertBox: {
    padding: "14px",
    margin: "10px 0",
    borderRadius: "10px",
    fontWeight: "600",
    color: "white",
    boxShadow: "0 0 12px rgba(0,0,0,0.5)"
  },

  chatButton: {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    padding: "12px 18px",
    background: "linear-gradient(135deg, #2563eb, #1e40af)",
    color: "white",
    border: "none",
    borderRadius: "30px",
    cursor: "pointer",
    fontWeight: "bold",
    boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
    zIndex: 1000,
  },

  chatPopup: {
    position: "fixed",
    bottom: "80px",
    right: "20px",
    width: "320px",
    height: "400px",
    background: "#020617",
    borderRadius: "12px",
    boxShadow: "0 0 25px rgba(0,0,0,0.7)",
    overflow: "hidden",
    zIndex: 1000,
  },

  popup: {
  position: "fixed",
  top: "20px",
  left: "50%",
  transform: "translateX(-50%)",
  background: "linear-gradient(135deg, #2563eb, #1e40af)",
  color: "white",
  padding: "14px 26px",
  borderRadius: "12px",
  fontWeight: "bold",
  boxShadow: "0 0 25px rgba(0,0,0,0.6)",
  zIndex: 3000,
  animation: "fadeIn 0.3s ease"
}
};