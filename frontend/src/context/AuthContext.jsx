import { useEffect, useState } from "react";
import { authService } from "../services/authService";
import { userService } from "../services/userService";
import { AuthContext } from "./useAuth";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("access_token")));

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      if (!token) {
        if (isMounted) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const profile = await userService.getProfile();
        if (isMounted) {
          setUser(profile);
        }
      } catch {
        localStorage.removeItem("access_token");
        if (isMounted) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadUser();
    return () => {
      isMounted = false;
    };
  }, [token]);

  async function login(email, password) {
    const data = await authService.login(email, password);
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);

    const profile = await userService.getProfile();
    setUser(profile);
    return profile;
  }

  async function register(email, password, full_name) {
    return authService.register(email, password, full_name);
  }

  async function refreshProfile() {
    const profile = await userService.getProfile();
    setUser(profile);
    return profile;
  }

  function logout() {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: Boolean(token && user),
    login,
    register,
    logout,
    refreshProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
