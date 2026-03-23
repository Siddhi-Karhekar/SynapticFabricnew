import React from "react";

function PlantOverview({ factoryAnalytics }) {

  // =============================
  // EMPTY STATE
  // =============================
  if (!factoryAnalytics || Object.keys(factoryAnalytics).length === 0) {
    return (
      <div style={{ padding: "20px" }}>
        <h2>🏭 Factory Analytics</h2>
        <p style={{ opacity: 0.7 }}>
          No analytics data available.
        </p>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>🏭 Factory Analytics Dashboard</h2>

      <div style={containerStyle}>

        {/* HEALTH SCORE */}
        <div style={cardStyle}>
          <h3>Plant Health Score</h3>
          <p style={valueStyle}>
            {factoryAnalytics.plant_health_score != null
              ? `${factoryAnalytics.plant_health_score}%`
              : "N/A"}
          </p>
        </div>

        {/* MOST UNSTABLE MACHINE */}
        <div style={cardStyle}>
          <h3>Most Unstable Machine</h3>
          <p style={valueStyle}>
            {factoryAnalytics.most_unstable_machine || "N/A"}
          </p>
        </div>

        {/* TOTAL MACHINES */}
        <div style={cardStyle}>
          <h3>Total Machines</h3>
          <p style={valueStyle}>
            {factoryAnalytics.total_machines ?? "N/A"}
          </p>
        </div>

        {/* MACHINES NEEDING ATTENTION */}
        <div style={cardStyle}>
          <h3>Machines Needing Attention</h3>

          {(factoryAnalytics.machines_needing_attention || []).length === 0 ? (
            <p style={{ opacity: 0.7 }}>None</p>
          ) : (
            <ul style={{ paddingLeft: "18px", marginTop: "10px" }}>
              {factoryAnalytics.machines_needing_attention.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          )}
        </div>

      </div>
    </div>
  );
}

// =============================
// STYLES
// =============================

const containerStyle = {
  display: "flex",
  flexWrap: "wrap",
  gap: "20px",
  marginTop: "10px"
};

const cardStyle = {
  border: "1px solid #2c2c2c",
  borderRadius: "10px",
  padding: "20px",
  width: "220px",
  backgroundColor: "#1e1e1e",
  color: "white",
  boxShadow: "0 4px 12px rgba(0,0,0,0.5)"
};

const valueStyle = {
  fontSize: "22px",
  fontWeight: "bold",
  marginTop: "10px"
};

export default PlantOverview;