const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function normalizeMessage(message) {
  if (!message) {
    return message;
  }

  return {
    ...message,
    id: message.id ?? message.message_id,
  };
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, options);
  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail = data?.detail || data?.message || `Request failed with ${response.status}`;
    throw new Error(detail);
  }

  return data;
}

function withAuth(token, options = {}) {
  return {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  };
}

export async function registerUser(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function loginUser(credentials) {
  return apiRequest("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
}

export async function classifyMessage(token, text) {
  const response = await apiRequest(
    "/classify",
    withAuth(token, {
      method: "POST",
      body: JSON.stringify({ text }),
    })
  );

  return normalizeMessage(response);
}

export async function getMessages(token, filters = {}) {
  const params = new URLSearchParams();

  if (filters.urgency) {
    params.set("urgency", filters.urgency);
  }

  if (filters.status) {
    params.set("status", filters.status);
  }

  const query = params.toString() ? `?${params.toString()}` : "";
  const response = await apiRequest(`/messages${query}`, withAuth(token, { method: "GET" }));
  return {
    ...response,
    messages: (response.messages || []).map(normalizeMessage),
  };
}

export async function archiveMessage(token, messageId) {
  return apiRequest(
    `/messages/${messageId}/archive`,
    withAuth(token, { method: "POST", body: JSON.stringify({}) })
  );
}

export async function getAnalyticsSnapshot(token) {
  const [
    overview,
    urgencyDistribution,
    messageTrends,
    modelPerformance,
    confidenceDistribution,
    categoryBreakdown,
    recentActivity,
  ] = await Promise.all([
    apiRequest("/analytics/overview", withAuth(token, { method: "GET" })),
    apiRequest("/analytics/urgency-distribution", withAuth(token, { method: "GET" })),
    apiRequest("/analytics/message-trends", withAuth(token, { method: "GET" })),
    apiRequest("/analytics/model-performance", withAuth(token, { method: "GET" })),
    apiRequest("/analytics/confidence-distribution", withAuth(token, { method: "GET" })),
    apiRequest("/analytics/category-breakdown", withAuth(token, { method: "GET" })),
    apiRequest("/analytics/recent-activity", withAuth(token, { method: "GET" })),
  ]);

  return {
    overview,
    urgencyDistribution,
    messageTrends,
    modelPerformance,
    confidenceDistribution,
    categoryBreakdown,
    recentActivity,
  };
}
