// ============================================================
// components/MessageCard.jsx — Individual Message Display
// Displays a single classified message with its urgency level,
// emergency type, score, source, and timestamp.
// Color coded by urgency: Critical=red, High=orange, Medium=yellow, Low=green
// ============================================================

const URGENCY_COLORS = {
  Critical: "#FF4C4C",
  High: "#FF9900",
  Medium: "#FFD700",
  Low: "#4CAF50",
};

function MessageCard({ message }) {
  const { text, source, urgency_level, emergency_type, urgency_score, timestamp } = message;

  const bgColor = URGENCY_COLORS[urgency_level] || "#ccc";

  return (
    <div style={{
      border: `2px solid ${bgColor}`,
      borderRadius: "8px",
      padding: "12px 16px",
      marginBottom: "10px",
      backgroundColor: "#fff",
      boxShadow: "0 1px 4px rgba(0,0,0,0.1)"
    }}>
      {/* Urgency Badge and Emergency Type */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "6px" }}>
        <span style={{ backgroundColor: bgColor, padding: "2px 10px", borderRadius: "12px", fontWeight: "bold", fontSize: "13px" }}>
          {urgency_level}
        </span>
        <span style={{ backgroundColor: "#e0e0e0", padding: "2px 10px", borderRadius: "12px", fontSize: "13px" }}>
          {emergency_type}
        </span>
        <span style={{ backgroundColor: "#e8f0fe", padding: "2px 10px", borderRadius: "12px", fontSize: "13px" }}>
          {source}
        </span>
      </div>

      {/* Message Text */}
      <p style={{ margin: "6px 0", fontSize: "15px" }}>{text}</p>

      {/* Score and Timestamp */}
      <div style={{ fontSize: "12px", color: "#888", display: "flex", justifyContent: "space-between" }}>
        <span>Urgency Score: <strong>{(urgency_score * 100).toFixed(0)}%</strong></span>
        <span>{new Date(timestamp).toLocaleTimeString()}</span>
      </div>
    </div>
  );
}

export default MessageCard;
