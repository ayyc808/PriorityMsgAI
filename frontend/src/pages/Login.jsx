import { useState } from "react";

function Login({ onDemo, onSubmit, isLoading, error }) {
  const [form, setForm] = useState({ email: "", password: "" });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="auth-card" onSubmit={handleSubmit}>
      <h2>Sign In</h2>

      <label className="field">
        <span>Email</span>
        <input
          autoComplete="email"
          name="email"
          onChange={handleChange}
          placeholder="dispatcher@agency.org"
          required
          type="email"
          value={form.email}
        />
      </label>

      <label className="field">
        <span>Password</span>
        <input
          autoComplete="current-password"
          name="password"
          onChange={handleChange}
          required
          type="password"
          value={form.password}
        />
      </label>

      {error ? <div className="banner banner--error">{error}</div> : null}

      <button className="primary-button" disabled={isLoading} type="submit">
        {isLoading ? "Signing in..." : "Sign In"}
      </button>

      <button className="ghost-button" onClick={onDemo} type="button">
        Demo
      </button>
    </form>
  );
}

export default Login;
