// ============================================================
// components/Simulator.jsx — Message Simulator Panel
// Allows the user to type or paste a test message,
// select the source type, and submit it to the backend.
// Used to demo the system without a live message feed.
// ============================================================

import { useState } from "react";
import { classifyMessage } from "../services/api";

const SOURCES = ["SMS", "Social Media", "Email", "Voice"];

// Sample messages for quick demo testing
const SAMPLE_MESSAGES = [
  "Building collapsed, people trapped inside need help immediately",
  "Person having a heart attack at downtown plaza",
  "Wildfire spreading rapidly towards residential area",
  "Minor traffic accident no injuries reported",
  "Gas leak detected in apartment building everyone evacuating",
];

function Simulator({ onNewMessage }) {
  const [text, setText] = useState("");
  const [source, setSource] = useState("SMS");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await classifyMessage(text, source);
      onNewMessage(result);
      setText("");
    } catch (err) {
      setError("Could not reach backend. Make sure uvicorn is running.");
    }
    setLoading(false);
  };

  const loadSample = () => {
    const random = SAMPLE_MESSAGES[Math.floor(Math.random() * SAMPLE_MESSAGES.length)];
    setText(random);
  };

  return (
    <div style={{ backgroundColor: "#f9f9f9", padding: "16px", borderRadius: "8px", marginBottom: "20px" }}>
      <h2>🧪 Message Simulator</h2>

      {/* Text Input */}
      <textarea
        rows={3}
        style={{ width: "100%", padding: "10px", fontSize: "14px", borderRadius: "6px", border: "1px solid #ccc", marginBottom: "10px" }}
        placeholder="Type an emergency message here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      {/* Source Selector and Buttons */}
      <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          style={{ padding: "8px", borderRadius: "6px", border: "1px solid #ccc" }}
        >
          {SOURCES.map((s) => <option key={s}>{s}</option>)}
        </select>

        <button onClick={loadSample} style={{ padding: "8px 14px", borderRadius: "6px", cursor: "pointer", backgroundColor: "#e0e0e0", border: "none" }}>
          Load Random Message
        </button>

        <button
          onClick={handleSubmit}
          disabled={loading || !text.trim()}
          style={{ padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: "#1a73e8", color: "#fff", border: "none", fontWeight: "bold" }}
        >
          {loading ? "Classifying..." : "Submit Message"}
        </button>
      </div>

      {error && <p style={{ color: "red", marginTop: "8px" }}>{error}</p>}
    </div>
  );
}

export default Simulator;
