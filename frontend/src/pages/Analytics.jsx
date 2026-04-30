function maxCount(items, key) {
  if (!items?.length) {
    return 1;
  }

  return Math.max(...items.map((item) => item[key] || 0), 1);
}

function Analytics({ analytics, loading }) {
  if (loading && !analytics) {
    return <div className="panel">Loading...</div>;
  }

  if (!analytics) {
    return <div className="panel">No data.</div>;
  }

  const totalMessages = analytics.overview?.total_messages || 0;
  const urgencyDistribution = analytics.urgencyDistribution?.distribution || [];
  const categoryBreakdown = analytics.categoryBreakdown?.categories || [];
  const trendPoints = analytics.messageTrends?.trends || [];
  const modelPerformance = analytics.modelPerformance?.model_performance || [];
  const recentActivity = analytics.recentActivity?.recent || [];
  const distributionMax = maxCount(urgencyDistribution, "count");
  const categoryMax = maxCount(categoryBreakdown, "count");
  const trendMax = maxCount(trendPoints, "total");

  return (
    <div className="page-stack">
      <section className="metric-row">
        <article className="metric-card metric-card--neutral">
          <span>Total messages</span>
          <strong>{totalMessages}</strong>
        </article>
        <article className="metric-card metric-card--neutral">
          <span>Average confidence</span>
          <strong>{Math.round((analytics.overview?.avg_confidence || 0) * 100)}%</strong>
        </article>
        <article className="metric-card metric-card--neutral">
          <span>Top category</span>
          <strong>{categoryBreakdown[0]?.category || "None"}</strong>
        </article>
      </section>

      <div className="analytics-grid">
        <section className="panel">
          <div className="panel__header">
            <h3>Urgency</h3>
          </div>

          <div className="chart-list">
            {urgencyDistribution.map((item) => (
              <div key={item.urgency_label} className="chart-row">
                <div className="chart-row__label">
                  <span>{item.urgency_label}</span>
                  <strong>{item.count}</strong>
                </div>
                <div className="chart-bar">
                  <div
                    className="chart-bar__fill"
                    style={{
                      width: `${(item.count / distributionMax) * 100}%`,
                      background: item.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <h3>Categories</h3>
          </div>

          <div className="chart-list">
            {categoryBreakdown.map((item) => (
              <div key={item.category} className="chart-row">
                <div className="chart-row__label">
                  <span>{item.category}</span>
                  <strong>{item.percentage}%</strong>
                </div>
                <div className="chart-bar">
                  <div
                    className="chart-bar__fill chart-bar__fill--cool"
                    style={{ width: `${(item.count / categoryMax) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <h3>Trend</h3>
          </div>

          <div className="trend-grid">
            {trendPoints.map((point) => (
              <div key={point.date} className="trend-grid__item">
                <div
                  className="trend-grid__bar"
                  style={{ height: `${Math.max((point.total / trendMax) * 180, 8)}px` }}
                />
                <strong>{point.total}</strong>
                <span>{point.date.slice(5)}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <h3>Models</h3>
          </div>

          <div className="stack-list">
            {modelPerformance.map((item) => (
              <article key={item.model} className="compact-card">
                <strong>{item.model}</strong>
                <p>Average confidence: {Math.round((item.avg_confidence || 0) * 100)}%</p>
                <p>Agreement rate: {Math.round((item.agreement_rate || 0) * 100)}%</p>
              </article>
            ))}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel__header">
          <h3>Recent</h3>
        </div>

        <div className="stack-list stack-list--two-up">
          {recentActivity.map((item) => (
            <article key={item.id} className="compact-card">
              <span className="badge badge--muted">{item.urgency_label}</span>
              <strong>{item.category}</strong>
              <p>{item.raw_text}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Analytics;
