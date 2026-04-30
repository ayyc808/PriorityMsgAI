import AddMessage from "./AddMessage";

const URGENCY_STYLES = {
  Critical: "critical",
  High: "high",
  Medium: "medium",
  Low: "low",
};

function formatTime(value) {
  return new Date(value).toLocaleString();
}

function Dashboard({
  loading,
  messages,
  onArchiveMessage,
  onCreateMessage,
  user,
}) {
  const urgencyCounts = messages.reduce(
    (counts, message) => {
      counts[message.urgency_label] = (counts[message.urgency_label] || 0) + 1;
      return counts;
    },
    { Critical: 0, High: 0, Medium: 0, Low: 0 }
  );

  return (
    <div className="page-stack">
      <section className="masthead">
        <h2>{user?.first_name}</h2>

        <div className="status-strip">
          <div className="status-pill">
            <span>Active queue</span>
            <strong>{messages.length}</strong>
          </div>
        </div>
      </section>

      <div className="page-stack">
        <AddMessage onSubmit={onCreateMessage} />

        <section className="panel">
          <div className="panel__header">
            <h3>Urgency</h3>
          </div>

          <div className="metric-row">
            {Object.entries(urgencyCounts).map(([label, count]) => (
              <article key={label} className={`metric-card metric-card--${URGENCY_STYLES[label]}`}>
                <span>{label}</span>
                <strong>{count}</strong>
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <h3>Messages</h3>
          </div>

          {loading ? <div className="empty-state">Loading queue...</div> : null}

          {!loading && messages.length === 0 ? (
            <div className="empty-state">No messages.</div>
          ) : null}

          <div className="message-list">
            {messages.map((message) => (
              <article key={message.id} className={`message-card message-card--${URGENCY_STYLES[message.urgency_label]}`}>
                <div className="message-card__header">
                  <div className="message-card__labels">
                    <span className="badge">{message.urgency_label}</span>
                    <span className="badge badge--muted">{message.category}</span>
                    {message.override_applied ? <span className="badge badge--alert">Override</span> : null}
                  </div>
                  <span className="timestamp">{formatTime(message.analyzed_at)}</span>
                </div>

                <p>{message.raw_text}</p>

                <div className="message-card__footer">
                  <div className="score-grid">
                    <span>Primary score {Math.round((message.urgency_score || 0) * 100)}%</span>
                    <span>RoBERTa {Math.round((message.roberta_score || 0) * 100)}%</span>
                    <span>LR {Math.round((message.lr_score || 0) * 100)}%</span>
                    <span>RF {Math.round((message.rf_score || 0) * 100)}%</span>
                  </div>

                  <div className="panel__actions">
                    <button className="ghost-button" onClick={() => onArchiveMessage(message.id)} type="button">
                      Archive
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
