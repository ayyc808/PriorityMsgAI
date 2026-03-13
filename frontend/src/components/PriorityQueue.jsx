// ============================================================
// components/PriorityQueue.jsx — Sorted Message Queue
// Displays all classified messages sorted by urgency score.
// Most critical messages appear at the top.
// Shows summary counters by urgency level.
// ============================================================

import MessageCard from "./MessageCard";

const URGENCY_ORDER = { Critical: 0, High: 1, Medium: 2, Low: 3 };

function PriorityQueue({ messages }) {

  // Sort messages: highest urgency first, then by score within same level
  const sorted = [...messages].sort((a, b) => {
    const levelDiff = URGENCY_ORDER[a.urgency_level] - URGENCY_ORDER[b.urgency_level];
    if (levelDiff !== 0) return levelDiff;
    return b.urgency_score - a.urgency_score;
  });

  // Count messages per urgency level
  const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
  messages.forEach((m) => counts[m.urgency_level]++);

  return (
    <div style={{ marginTop: "30px" }}>
      <h2>📋 Priority Queue</h2>

      {/* Summary Counters */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "20px" }}>
        {Object.entries(counts).map(([level, count]) => (
          <div key={level} style={{ textAlign: "center", padding: "8px 16px", borderRadius: "8px", backgroundColor: "#f5f5f5" }}>
            <div style={{ fontSize: "22px", fontWeight: "bold" }}>{count}</div>
            <div style={{ fontSize: "13px", color: "#555" }}>{level}</div>
          </div>
        ))}
        <div style={{ textAlign: "center", padding: "8px 16px", borderRadius: "8px", backgroundColor: "#f5f5f5" }}>
          <div style={{ fontSize: "22px", fontWeight: "bold" }}>{messages.length}</div>
          <div style={{ fontSize: "13px", color: "#555" }}>Total</div>
        </div>
      </div>

      {/* Message List */}
      {sorted.length === 0 ? (
        <p style={{ color: "#aaa" }}>No messages yet. Use the simulator to send a test message.</p>
      ) : (
        sorted.map((msg) => <MessageCard key={msg.id} message={msg} />)
      )}
    </div>
  );
}

export default PriorityQueue;
