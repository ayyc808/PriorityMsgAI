import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { useAuth } from "./context/AuthContext";
import {
  buildDemoAnalytics,
  classifyDemoMessage,
  getInitialDemoState,
} from "./demoData";
import {
  archiveMessage,
  classifyMessage,
  getAnalyticsSnapshot,
  getMessages,
  registerUser,
} from "./services/api";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "analytics", label: "Analytics" },
  { id: "settings", label: "Settings" },
];

function App() {
  const { token, user, login, loginDemo, logout } = useAuth();
  const [mode, setMode] = useState("login");
  const [activeView, setActiveView] = useState("dashboard");
  const [messages, setMessages] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const isDemoMode = token === "demo-token";

  useEffect(() => {
    if (!token) {
      setMessages([]);
      setAnalytics(null);
      setLoadError("");
      return;
    }

    let cancelled = false;

    async function loadAppData() {
      if (isDemoMode) {
        const demoState = getInitialDemoState();
        if (!cancelled) {
          setMessages(demoState.messages);
          setAnalytics(buildDemoAnalytics(demoState.messages));
          setLoading(false);
        }
        return;
      }

      setLoading(true);
      setLoadError("");

      try {
        const [messageData, analyticsData] =
          await Promise.all([
            getMessages(token),
            getAnalyticsSnapshot(token),
          ]);

        if (cancelled) {
          return;
        }

        setMessages(messageData.messages || []);
        setAnalytics(analyticsData);
      } catch (error) {
        if (!cancelled) {
          setLoadError(error.message || "Could not load application data.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAppData();

    return () => {
      cancelled = true;
    };
  }, [isDemoMode, token]);

  const handleLogin = async (credentials) => {
    setAuthLoading(true);
    setAuthError("");

    try {
      await login(credentials);
    } catch (error) {
      setAuthError(error.message || "Unable to sign in.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegister = async (payload) => {
    setAuthLoading(true);
    setAuthError("");

    try {
      await registerUser(payload);
    } catch (error) {
      setAuthError(error.message || "Unable to create account.");
      throw error;
    } finally {
      setAuthLoading(false);
    }
  };

  const handleCreateMessage = async (text) => {
    if (isDemoMode) {
      const created = classifyDemoMessage(text, Date.now());
      setMessages((current) => {
        const nextMessages = [created, ...current];
        setAnalytics(buildDemoAnalytics(nextMessages));
        return nextMessages;
      });
      return;
    }

    const created = await classifyMessage(token, text);
    setMessages((current) => [created, ...current]);

    const analyticsData = await getAnalyticsSnapshot(token);
    setAnalytics(analyticsData);
  };

  const handleArchiveMessage = async (messageId) => {
    if (isDemoMode) {
      setMessages((current) => {
        const nextMessages = current.filter((item) => item.id !== messageId);
        setAnalytics(buildDemoAnalytics(nextMessages));
        return nextMessages;
      });
      return;
    }

    await archiveMessage(token, messageId);
    const [messageData, analyticsData] = await Promise.all([
      getMessages(token),
      getAnalyticsSnapshot(token),
    ]);
    setMessages(messageData.messages || []);
    setAnalytics(analyticsData);
  };

  if (!token) {
    return (
      <div className="auth-shell">
        <section className="hero-panel">
          <div className="hero-panel__badge">PriorityMsgAI</div>
          <h1>RapidRelief</h1>
        </section>

        <section className="auth-panel">
          <div className="auth-panel__switch">
            <button
              className={mode === "login" ? "is-active" : ""}
              onClick={() => setMode("login")}
              type="button"
            >
              Sign In
            </button>
            <button
              className={mode === "register" ? "is-active" : ""}
              onClick={() => setMode("register")}
              type="button"
            >
              Create Account
            </button>
          </div>

          {mode === "login" ? (
            <Login
              onDemo={loginDemo}
              onSubmit={handleLogin}
              isLoading={authLoading}
              error={authError}
            />
          ) : (
            <Register
              onSubmit={handleRegister}
              isLoading={authLoading}
              error={authError}
            />
          )}
        </section>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <span className="sidebar__eyebrow">PriorityMsgAI</span>
          <h2>RapidRelief</h2>
        </div>

        <nav className="sidebar__nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={activeView === item.id ? "is-active" : ""}
              onClick={() => setActiveView(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar__footer">
          <p>
            <strong>{user?.first_name} {user?.last_name}</strong>
          </p>
          <button className="ghost-button" onClick={logout} type="button">
            Sign Out
          </button>
        </div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <div>
            <h1>
              {activeView === "dashboard" && "Dashboard"}
              {activeView === "analytics" && "Analytics"}
              {activeView === "settings" && "Settings"}
            </h1>
          </div>
        </header>

        {loadError ? <div className="banner banner--error">{loadError}</div> : null}

        {activeView === "dashboard" ? (
          <Dashboard
            loading={loading}
            messages={messages}
            onArchiveMessage={handleArchiveMessage}
            onCreateMessage={handleCreateMessage}
            user={user}
          />
        ) : null}

        {activeView === "analytics" ? (
          <Analytics analytics={analytics} loading={loading} />
        ) : null}

        {activeView === "settings" ? (
          <Settings
            apiBaseUrl={process.env.REACT_APP_API_URL || "http://localhost:8000"}
            user={user}
          />
        ) : null}
      </main>
    </div>
  );
}

export default App;
