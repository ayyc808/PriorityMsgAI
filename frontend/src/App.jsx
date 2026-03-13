// ============================================================
// App.jsx — Root React Component
// The main layout of the app. Holds all components together.
// Manages the global message state shared across components.
// ============================================================

import { useState } from "react";
import PriorityQueue from "./components/PriorityQueue";
import Simulator from "./components/Simulator";

function App() {
  // Global list of all classified messages
  // Each message: { id, text, source, urgency_level, emergency_type, urgency_score, timestamp }
  const [messages, setMessages] = useState([]);

  // Called by Simulator when a new message comes back from the backend
  const handleNewMessage = (newMessage) => {
    setMessages((prev) => [...prev, newMessage]);
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "20px" }}>

      {/* Header */}
      <h1>🚨 PriorityMsgAI — Emergency Message Prioritizer</h1>

      {/* Message Simulator — sends test messages to backend */}
      <Simulator onNewMessage={handleNewMessage} />

      {/* Priority Queue — displays messages sorted by urgency */}
      <PriorityQueue messages={messages} />

    </div>
  );
}

export default App;
