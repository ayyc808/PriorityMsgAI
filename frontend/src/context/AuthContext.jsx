import { createContext, useContext, useEffect, useState } from "react";
import { getDemoSession } from "../demoData";
import { loginUser } from "../services/api";

const STORAGE_KEY = "rapidrelief-auth";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return;
    }

    try {
      const parsed = JSON.parse(stored);
      setToken(parsed.token || "");
      setUser(parsed.user || null);
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const login = async (credentials) => {
    const response = await loginUser(credentials);

    const nextUser = {
      user_id: response.user_id,
      first_name: response.first_name,
      last_name: response.last_name,
      organization: response.organization,
      role: response.role,
    };

    setToken(response.access_token);
    setUser(nextUser);
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ token: response.access_token, user: nextUser })
    );

    return response;
  };

  const logout = () => {
    setToken("");
    setUser(null);
    window.localStorage.removeItem(STORAGE_KEY);
  };

  const loginDemo = () => {
    const session = getDemoSession();
    setToken(session.token);
    setUser(session.user);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  };

  return (
    <AuthContext.Provider value={{ token, user, login, loginDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
