import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { updateSettings } from "../services/api";

const FILTER_OPTIONS = ["Latest", "Critical", "High", "Medium", "Low"];

function Settings({ apiBaseUrl, user }) {
  const { token, updateUser } = useAuth();
  const [defaultFilter, setDefaultFilter] = useState(user?.default_message_filter || "Latest");
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const handleFilterChange = async (newFilter) => {
    setDefaultFilter(newFilter);
    setSaving(true);
    setSaveMessage("");

    try {
      await updateSettings(token, { default_message_filter: newFilter });
      updateUser({ default_message_filter: newFilter });
      setSaveMessage("Saved");
      setTimeout(() => setSaveMessage(""), 2000);
    } catch (error) {
      setSaveMessage("Failed to save");
      console.error("[Settings] Error updating default filter:", error);
    } finally {
      setSaving(false);
    }
  };

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

      <section className="panel">
        <div className="panel__header">
          <h3>Preferences</h3>
          {saveMessage && <span className="save-message">{saveMessage}</span>}
        </div>

        <div className="settings-row">
          <div className="setting-item">
            <label htmlFor="default-filter">
              <span>Default Message Filter</span>
              <small>Choose which messages to show by default on the dashboard</small>
            </label>
            <select
              id="default-filter"
              value={defaultFilter}
              onChange={(e) => handleFilterChange(e.target.value)}
              disabled={saving}
              className="settings-select"
            >
              {FILTER_OPTIONS.map((filter) => (
                <option key={filter} value={filter}>
                  {filter}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Settings;
