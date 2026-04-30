function Settings({ apiBaseUrl, user }) {
  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <h3>Profile</h3>
        </div>

        <div className="details-grid">
          <article className="detail-card">
            <span>Name</span>
            <strong>{user?.first_name} {user?.last_name}</strong>
          </article>
          <article className="detail-card">
            <span>Organization</span>
            <strong>{user?.organization || "-"}</strong>
          </article>
          <article className="detail-card">
            <span>Role</span>
            <strong>{user?.role || "-"}</strong>
          </article>
          <article className="detail-card">
            <span>API endpoint</span>
            <strong>{apiBaseUrl}</strong>
          </article>
        </div>
      </section>
    </div>
  );
}

export default Settings;
