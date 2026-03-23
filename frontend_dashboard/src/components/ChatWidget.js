import { useState } from "react";
import Chatbot from "./Chatbot"; // your existing chatbot

export default function ChatWidget() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* ================= CHAT WINDOW ================= */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: 90,
            right: 20,
            width: 350,
            height: 450,
            background: "#1e1e1e",
            borderRadius: 12,
            boxShadow: "0 0 20px rgba(0,0,0,0.5)",
            zIndex: 999,
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* HEADER */}
          <div
            style={{
              background: "#2c2c2c",
              padding: 10,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              color: "white",
            }}
          >
            🤖 Industrial AI Assistant
            <button
              onClick={() => setOpen(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "white",
                cursor: "pointer",
                fontSize: 16,
              }}
            >
              ✕
            </button>
          </div>

          {/* CHATBOT BODY */}
          <div style={{ flex: 1, overflow: "hidden" }}>
            <Chatbot />
          </div>
        </div>
      )}

      {/* ================= FLOATING BUTTON ================= */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          background: "#007bff",
          color: "white",
          padding: "12px 16px",
          borderRadius: 30,
          cursor: "pointer",
          boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
          display: "flex",
          alignItems: "center",
          gap: 8,
          zIndex: 1000,
          fontWeight: "bold",
        }}
      >
        🤖 Need help? Ask here
      </div>
    </>
  );
}