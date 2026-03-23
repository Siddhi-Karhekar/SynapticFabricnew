export default function AlertPanel({ machines }) {

  const allAlerts = Object.values(machines || {})
    .flatMap((m) =>
      (m.alerts || []).map((a) => ({
        ...a,
        machine_id: m.machine_id
      }))
    )
    .filter((a) => a.level === "WARNING" || a.level === "CRITICAL");

  return (
    <div style={box}>
      <h2>🚨 AI Alerts</h2>

      {allAlerts.length === 0 ? (
        <p style={{ opacity: 0.7 }}>No active alerts</p>
      ) : (
        allAlerts.map((a, i) => (
          <div
            key={i}
            style={{
              margin: "8px 0",
              padding: 10,
              borderRadius: 6,
              background:
                a.level === "CRITICAL"
                  ? "#e74c3c"
                  : "#f39c12",
              color: "white"
            }}
          >
            <strong>{a.level}</strong> — [{a.machine_id}] {a.message}
          </div>
        ))
      )}
    </div>
  );
}

const box = {
  background: "#111",
  color: "white",
  padding: 15,
  marginTop: 20,
  borderRadius: 10,
  minHeight: 180,
};