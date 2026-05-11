import { createContext, useContext, useEffect, useState } from "react";
import { getDemoSession } from "../demoData";
import { loginUser } from "../services/api";

const STORAGE_KEY = "rapidrelief-auth";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log("[AuthContext] Initializing - checking localStorage");
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      console.log("[AuthContext] No stored auth found");
      return;
    }

    try {
      const parsed = JSON.parse(stored);
      console.log("[AuthContext] Restoring auth for user:", parsed.user?.email || "unknown");
      setToken(parsed.token || "");
      setUser(parsed.user || null);
    } catch (error) {
      console.error("[AuthContext] Error parsing stored auth:", error);
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const login = async (credentials) => {
    console.log("[AuthContext] Logging in user:", credentials.email);
    const response = await loginUser(credentials);

    const nextUser = {
      user_id: response.user_id,
      first_name: response.first_name,
      last_name: response.last_name,
      organization: response.organization,
      role: response.role,
      default_message_filter: response.default_message_filter || "Latest",
    };

    console.log("[AuthContext] Login successful - user_id:", nextUser.user_id, "default_filter:", nextUser.default_message_filter);
    setToken(response.access_token);
    setUser(nextUser);
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ token: response.access_token, user: nextUser })
    );

    return response;
  };

  const logout = () => {
    console.log("[AuthContext] Logging out user:", user?.email || "unknown");
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

  const updateUser = (updates) => {
    console.log("[AuthContext] Updating user:", updates);
    const nextUser = { ...user, ...updates };
    setUser(nextUser);
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ token, user: nextUser })
    );
  };

  return (
    <AuthContext.Provider value={{ token, user, login, loginDemo, logout, updateUser }}>
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
