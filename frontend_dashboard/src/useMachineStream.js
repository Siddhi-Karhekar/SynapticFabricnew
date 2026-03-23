import { useEffect, useState, useRef } from "react";

export default function useMachineStream() {

  // ==========================================
  // 📊 STATE
  // ==========================================

  const [machines, setMachines] = useState({});
  const [factoryAnalytics, setFactoryAnalytics] = useState({});
  const [agentAlerts, setAgentAlerts] = useState([]);
  const [agentActions, setAgentActions] = useState([]);

  // 🔥 POPUP SYSTEM
  const [popupMessage, setPopupMessage] = useState(null);

  const popupQueueRef = useRef([]);
  const isShowingRef = useRef(false);

  // ✅ FIX: TRACK SHOWN ACTIONS (NO DUPLICATES)
  const shownActionsRef = useRef(new Set());

  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  // ==========================================
  // 🎯 POPUP QUEUE HANDLER
  // ==========================================

  const processPopupQueue = () => {

    if (isShowingRef.current) return;
    if (popupQueueRef.current.length === 0) return;

    const next = popupQueueRef.current.shift();

    isShowingRef.current = true;

    console.log("📢 SHOWING POPUP:", next);

    setPopupMessage(next);

    setTimeout(() => {
      setPopupMessage(null);
      isShowingRef.current = false;

      // 🔁 PROCESS NEXT
      processPopupQueue();

    }, 3000);
  };

  // ==========================================
  // 🔌 WEBSOCKET
  // ==========================================

  useEffect(() => {

    const connectWebSocket = () => {

      console.log("🔌 Attempting WebSocket connection...");

      const ws = new WebSocket("ws://127.0.0.1:8000/ws/machines");
      wsRef.current = ws;

      // =========================
      // ✅ CONNECTED
      // =========================
      ws.onopen = () => {
        console.log("✅ WebSocket connected");
      };

      // =========================
      // 📡 MESSAGE
      // =========================
      ws.onmessage = (event) => {
        try {

          const payload = JSON.parse(event.data);

          console.log("📡 WS DATA RECEIVED:", payload);

          const machineArray = payload?.machines || [];
          const analytics = payload?.factory_analytics || {};
          const alerts = payload?.agent_alerts || [];
          const actions = payload?.agent_actions || [];

          const mapped = {};

          // ======================================
          // 🏭 MACHINE MAPPING
          // ======================================
          machineArray.forEach((m) => {

            const id = m.machine_id;

            mapped[id] = {
              machine_id: id,

              temperature: m.temperature ?? 0,
              torque: m.torque ?? 0,
              tool_wear: m.tool_wear ?? 0,
              vibration_index: m.vibration_index ?? 0,

              health_status: m.health_status ?? "Unknown",
              prediction: m.prediction ?? m.anomaly_score ?? 0,
              anomaly_score: m.anomaly_score ?? 0,

              alerts: (m.alerts || []).map((a) => ({
                level: (a.level || "info").toUpperCase(),
                message: a.message || "No message"
              })),

              diagnosis: (m.root_cause || []).map((c) => ({
                issue: c.issue || "Unknown issue",
                confidence: c.confidence ?? 0,
                reason: c.reason || ""
              })),

              rul_cycles: m.rul_cycles ?? null,
              rul_time: m.rul_time ?? null,

              ai_explanation: m.ai_explanation ?? "",
              shap: m.shap ?? {},

              future_prediction: m.future_prediction ?? null
            };
          });

          // ======================================
          // ✅ STATE UPDATE
          // ======================================
          setMachines(mapped);
          setFactoryAnalytics(analytics);
          setAgentAlerts(alerts);
          setAgentActions(actions);

          // ======================================
          // 🚀 POPUP SYSTEM
          // ======================================
          actions.forEach((a) => {

            if (a.action === "AUTO_MAINTENANCE" && a.status === "STARTING") {

              const uniqueKey = `${a.machine_id}-${a.timestamp}`;

              // ❌ PREVENT DUPLICATE POPUPS
              if (shownActionsRef.current.has(uniqueKey)) {
                return;
              }

              shownActionsRef.current.add(uniqueKey);

              const msg = `🤖 Performing auto-maintenance on ${a.machine_id}`;

              console.log("🔥 QUEUED POPUP:", msg);

              popupQueueRef.current.push(msg);
            }
          });

          processPopupQueue();

        } catch (err) {
          console.error("❌ WS PARSE ERROR:", err);
        }
      };

      // =========================
      // ❌ ERROR
      // =========================
      ws.onerror = (err) => {
        console.error("❌ WebSocket error:", err);
      };

      // =========================
      // 🔁 RECONNECT
      // =========================
      ws.onclose = () => {
        console.warn("⚠️ WebSocket closed. Reconnecting...");

        reconnectRef.current = setTimeout(() => {
          connectWebSocket();
        }, 2000);
      };
    };

    connectWebSocket();

    // =========================
    // CLEANUP
    // =========================
    return () => {
      console.log("🔌 Cleaning up WebSocket...");

      if (wsRef.current) wsRef.current.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };

  }, []);

  // ==========================================
  // 📦 RETURN
  // ==========================================

  return {
    machines,
    factoryAnalytics,
    agentAlerts,
    agentActions,
    popupMessage
  };
}