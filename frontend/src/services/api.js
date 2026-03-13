// ============================================================
// services/api.js — All Backend API Calls
// Centralizes all fetch() calls to the FastAPI backend.
// Import these functions in any component that needs backend data.
// ============================================================

const BASE_URL = "http://localhost:8000";

/**
 * Sends a message to the backend for classification.
 * @param {string} text - The message text to classify
 * @param {string} source - The source type: SMS, Social Media, Email, Voice
 * @returns {object} - { id, text, source, urgency_level, emergency_type, urgency_score, timestamp }
 */
export async function classifyMessage(text, source) {
  const response = await fetch(`${BASE_URL}/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, source }),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  return response.json();
}
