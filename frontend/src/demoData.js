const DEMO_USER = {
  user_id: 0,
  first_name: "Demo",
  last_name: "User",
  organization: "RapidRelief",
  role: "Analyst",
};

const INITIAL_MESSAGES = [
  {
    id: 101,
    raw_text: "Building collapse reported downtown. Multiple people trapped inside.",
    urgency_label: "Critical",
    urgency_score: 0.98,
    category: "Collapse",
    roberta_label: "Critical",
    roberta_score: 0.98,
    lr_label: "High",
    lr_score: 0.76,
    rf_label: "Critical",
    rf_score: 0.88,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 14).toISOString(),
    override_applied: false,
    status: "active",
  },
  {
    id: 102,
    raw_text: "Wildfire spreading toward residential blocks near Route 9.",
    urgency_label: "High",
    urgency_score: 0.86,
    category: "Fire",
    roberta_label: "High",
    roberta_score: 0.86,
    lr_label: "High",
    lr_score: 0.79,
    rf_label: "Medium",
    rf_score: 0.63,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    override_applied: false,
    status: "active",
  },
  {
    id: 103,
    raw_text: "Flooding reported under the freeway overpass, vehicles stalled.",
    urgency_label: "Medium",
    urgency_score: 0.62,
    category: "Flood",
    roberta_label: "Medium",
    roberta_score: 0.62,
    lr_label: "Medium",
    lr_score: 0.58,
    rf_label: "Medium",
    rf_score: 0.6,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 95).toISOString(),
    override_applied: false,
    status: "active",
  },
];

function countBy(items, key) {
  return items.reduce((accumulator, item) => {
    const value = item[key];
    accumulator[value] = (accumulator[value] || 0) + 1;
    return accumulator;
  }, {});
}

export function getDemoSession() {
  return {
    token: "demo-token",
    user: DEMO_USER,
  };
}

export function getInitialDemoState() {
  return {
    messages: INITIAL_MESSAGES.map((message) => ({ ...message })),
  };
}

export function classifyDemoMessage(text, nextId) {
  const lower = text.toLowerCase();
  let urgency_label = "Low";
  let category = "General";
  let urgency_score = 0.34;
  let override_applied = false;

  if (/(collapse|trapped|not breathing|explosion|active shooter|heart attack|unconscious)/.test(lower)) {
    urgency_label = "Critical";
    category = /(collapse|trapped)/.test(lower) ? "Collapse" : "Medical";
    urgency_score = 0.97;
  } else if (/(fire|wildfire|gas leak|shooting|flood|evacuat)/.test(lower)) {
    urgency_label = "High";
    category = /fire|wildfire/.test(lower)
      ? "Fire"
      : /flood/.test(lower)
        ? "Flood"
        : /gas leak/.test(lower)
          ? "Environmental"
          : "Disaster";
    urgency_score = 0.83;
  } else if (/(injury|injured|accident|storm|water)/.test(lower)) {
    urgency_label = "Medium";
    category = /storm/.test(lower) ? "Hurricane" : /water/.test(lower) ? "Flood" : "Medical";
    urgency_score = 0.61;
  }

  if (urgency_label === "High" && /(trapped|unconscious|multiple)/.test(lower)) {
    urgency_label = "Critical";
    urgency_score = 0.94;
    override_applied = true;
  }

  return {
    id: nextId,
    message_id: nextId,
    raw_text: text,
    urgency_label,
    urgency_score,
    category,
    roberta_label: override_applied ? "High -> Critical" : urgency_label,
    roberta_score: urgency_score,
    lr_label: urgency_label,
    lr_score: Math.max(urgency_score - 0.08, 0.25),
    rf_label: urgency_label,
    rf_score: Math.max(urgency_score - 0.05, 0.25),
    analyzed_at: new Date().toISOString(),
    override_applied,
    status: "active",
  };
}

export function buildDemoAnalytics(messages) {
  const total_messages = messages.length;
  const urgencyCounts = countBy(messages, "urgency_label");
  const categoryCounts = countBy(messages, "category");
  const avgConfidence = total_messages
    ? messages.reduce((sum, message) => sum + (message.urgency_score || 0), 0) / total_messages
    : 0;

  const urgencyDistribution = ["Critical", "High", "Medium", "Low"].map((level) => {
    const count = urgencyCounts[level] || 0;
    const colorMap = {
      Critical: "#E24B4A",
      High: "#EF9F27",
      Medium: "#c9b800",
      Low: "#639922",
    };

    return {
      urgency_label: level,
      count,
      percentage: total_messages ? Number(((count / total_messages) * 100).toFixed(1)) : 0,
      color: colorMap[level],
    };
  });

  const categoryBreakdown = Object.entries(categoryCounts)
    .sort((left, right) => right[1] - left[1])
    .map(([category, count]) => ({
      category,
      count,
      percentage: total_messages ? Number(((count / total_messages) * 100).toFixed(1)) : 0,
    }));

  const today = new Date();
  const trendMap = new Map();
  for (let offset = 6; offset >= 0; offset -= 1) {
    const date = new Date(today);
    date.setDate(today.getDate() - offset);
    const key = date.toISOString().slice(0, 10);
    trendMap.set(key, { date: key, total: 0, critical: 0, high: 0, medium: 0, low: 0 });
  }

  messages.forEach((message) => {
    const key = message.analyzed_at.slice(0, 10);
    const bucket = trendMap.get(key);
    if (!bucket) {
      return;
    }
    bucket.total += 1;
    bucket[message.urgency_label.toLowerCase()] += 1;
  });

  const recent = [...messages]
    .sort((left, right) => right.analyzed_at.localeCompare(left.analyzed_at))
    .slice(0, 10)
    .map((message) => ({
      id: message.id,
      raw_text: message.raw_text,
      urgency_label: message.urgency_label,
      urgency_score: message.urgency_score,
      category: message.category,
      status: message.status || "active",
      analyzed_at: message.analyzed_at,
    }));

  const model_performance = [
    {
      model: "RoBERTa",
      avg_confidence: avgConfidence,
      agreement_rate: 1,
      color: "#E24B4A",
    },
    {
      model: "Logistic Regression",
      avg_confidence: total_messages
        ? messages.reduce((sum, message) => sum + (message.lr_score || 0), 0) / total_messages
        : 0,
      agreement_rate: total_messages
        ? messages.filter((message) => message.lr_label === message.urgency_label).length / total_messages
        : 0,
      color: "#378ADD",
    },
    {
      model: "Random Forest",
      avg_confidence: total_messages
        ? messages.reduce((sum, message) => sum + (message.rf_score || 0), 0) / total_messages
        : 0,
      agreement_rate: total_messages
        ? messages.filter((message) => message.rf_label === message.urgency_label).length / total_messages
        : 0,
      color: "#1D9E75",
    },
  ];

  return {
    overview: {
      total_messages,
      urgency_counts: urgencyCounts,
      category_counts: categoryCounts,
      avg_confidence: Number(avgConfidence.toFixed(4)),
    },
    urgencyDistribution: { distribution: urgencyDistribution, total: total_messages },
    messageTrends: { trends: [...trendMap.values()], days: 7 },
    modelPerformance: { model_performance, total: total_messages },
    confidenceDistribution: { buckets: [], total: total_messages, avg: Number(avgConfidence.toFixed(4)) },
    categoryBreakdown: { categories: categoryBreakdown, total: total_messages },
    recentActivity: { recent, total: recent.length },
  };
}
