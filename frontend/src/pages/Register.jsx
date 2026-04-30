import { useState } from "react";

const INITIAL_FORM = {
  first_name: "",
  middle_name: "",
  last_name: "",
  email: "",
  password: "",
  confirm_password: "",
  organization: "",
  role: "",
  access_code: "",
};

function Register({ onSubmit, isLoading, error }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [success, setSuccess] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSuccess("");

    try {
      await onSubmit(form);
      setSuccess("Account created.");
      setForm(INITIAL_FORM);
    } catch {
      // parent already manages error display
    }
  };

  return (
    <form className="auth-card auth-card--wide" onSubmit={handleSubmit}>
      <h2>Create Account</h2>

      <div className="grid-two">
        <label className="field">
          <span>First name</span>
          <input name="first_name" onChange={handleChange} required type="text" value={form.first_name} />
        </label>
        <label className="field">
          <span>Middle name</span>
          <input name="middle_name" onChange={handleChange} type="text" value={form.middle_name} />
        </label>
        <label className="field">
          <span>Last name</span>
          <input name="last_name" onChange={handleChange} required type="text" value={form.last_name} />
        </label>
        <label className="field">
          <span>Email</span>
          <input name="email" onChange={handleChange} required type="email" value={form.email} />
        </label>
        <label className="field">
          <span>Organization</span>
          <input name="organization" onChange={handleChange} type="text" value={form.organization} />
        </label>
        <label className="field">
          <span>Role</span>
          <input name="role" onChange={handleChange} type="text" value={form.role} />
        </label>
        <label className="field">
          <span>Password</span>
          <input name="password" onChange={handleChange} required type="password" value={form.password} />
        </label>
        <label className="field">
          <span>Confirm password</span>
          <input
            name="confirm_password"
            onChange={handleChange}
            required
            type="password"
            value={form.confirm_password}
          />
        </label>
      </div>

      {error ? <div className="banner banner--error">{error}</div> : null}
      {success ? <div className="banner banner--success">{success}</div> : null}

      <button className="primary-button" disabled={isLoading} type="submit">
        {isLoading ? "Creating account..." : "Create Account"}
      </button>
    </form>
  );
}

export default Register;
