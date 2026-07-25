import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../services/api";

export default function Login() {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await authApi.register(form.email, form.username, form.password);
        setMode("login");
        setError("Account created. Sign in below.");
      } else {
        const { data } = await authApi.login(form.username, form.password);
        localStorage.setItem("access_token", data.access_token);
        navigate("/");
      }
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="sidebar-logo" style={{ marginBottom: 4 }}>
          <span className="signal-dot" />
          Traffic Predict
        </div>
        <p style={{ color: "var(--text-secondary)", fontSize: 13, marginBottom: 24 }}>
          {mode === "login" ? "Sign in to your console" : "Create an account"}
        </p>

        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <div className="form-row">
              <label>Email</label>
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
          )}
          <div className="form-row">
            <label>Username</label>
            <input
              required
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </div>
          <div className="form-row">
            <label>Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>

          <button className="btn" type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
          {error && <p className="error-text">{error}</p>}
        </form>

        <p style={{ fontSize: 13, marginTop: 16, color: "var(--text-secondary)" }}>
          {mode === "login" ? (
            <>No account? <a onClick={() => setMode("register")} style={{ cursor: "pointer" }}>Create one</a></>
          ) : (
            <>Already registered? <a onClick={() => setMode("login")} style={{ cursor: "pointer" }}>Sign in</a></>
          )}
        </p>
      </div>
    </div>
  );
}
