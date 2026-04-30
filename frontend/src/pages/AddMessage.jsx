import { useState } from "react";

const QUICK_PROMPTS = [
  "Building collapsed, people trapped inside need immediate rescue.",
  "Wildfire is spreading toward homes near the highway.",
  "Person unconscious after chemical leak in warehouse.",
  "Minor traffic accident, no reported injuries.",
];

function AddMessage({ onSubmit }) {
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!text.trim()) {
      setError("Enter a message before classifying.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await onSubmit(text);
      setText("");
    } catch (submitError) {
      setError(submitError.message || "Unable to classify message.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel panel--accent">
      <div className="panel__header">
        <h3>New Message</h3>
      </div>

      <textarea
        className="message-composer"
        onChange={(event) => setText(event.target.value)}
        placeholder="Paste or type an emergency report..."
        rows={6}
        value={text}
      />

      <div className="quick-prompts">
        {QUICK_PROMPTS.map((prompt) => (
          <button key={prompt} className="chip" onClick={() => setText(prompt)} type="button">
            {prompt}
          </button>
        ))}
      </div>

      {error ? <div className="banner banner--error">{error}</div> : null}

      <div className="panel__actions">
        <button className="primary-button" disabled={loading} onClick={submit} type="button">
          {loading ? "Classifying..." : "Run Classification"}
        </button>
      </div>
    </section>
  );
}

export default AddMessage;
