"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { apiFetch } from "@/lib/api";

interface User {
  pk: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>;
  register: (email: string, password1: string, password2: string) => Promise<{ ok: boolean; error?: string }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount: check for existing token and validate it
  useEffect(() => {
    const savedToken = localStorage.getItem("auth_token");
    if (savedToken) {
      setToken(savedToken);
      fetchUser(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (authToken: string) => {
    try {
      const data = await apiFetch("/api/auth/user/", {
        headers: { Authorization: `Token ${authToken}` },
      });
      setUser(data);
      setToken(authToken);
    } catch {
      localStorage.removeItem("auth_token");
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = useCallback(async (email: string, password: string) => {
    try {
      const data = await apiFetch("/api/auth/login/", {
        method: "POST",
        body: { email, password },
      });

      const authToken = data.key;
      localStorage.setItem("auth_token", authToken);
      setToken(authToken);

      // Fetch user info
      await fetchUser(authToken);

      // Merge anonymous cart
      try {
        await apiFetch("/api/v1/cart/merge-cart/", {
          method: "POST",
          headers: { Authorization: `Token ${authToken}` },
        });
      } catch {
        // Merge is best-effort, don't block login
      }

      return { ok: true };
    } catch (err: any) {
      if (err.data) {
        const errorMsg =
          err.data.non_field_errors?.[0] ||
          err.data.email?.[0] ||
          err.data.detail ||
          "Error al iniciar sesión";
        return { ok: false, error: errorMsg };
      }
      return { ok: false, error: "Error de conexión con el servidor" };
    }
  }, []);

  const register = useCallback(
    async (email: string, password1: string, password2: string) => {
      try {
        const username = email.split('@')[0] + Math.random().toString(36).substring(2, 8);
        await apiFetch("/api/auth/registration/", {
          method: "POST",
          body: { username, email, password1, password2 },
        });

        return { ok: true };
      } catch (err: any) {
        if (err.data) {
          const errorMsg =
            err.data.username?.[0] ||
            err.data.email?.[0] ||
            err.data.password1?.[0] ||
            err.data.non_field_errors?.[0] ||
            err.data.detail ||
            "Error al registrarse";
          return { ok: false, error: errorMsg };
        }
        return { ok: false, error: "Error de conexión con el servidor" };
      }
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      await apiFetch("/api/auth/logout/", { method: "POST" });
    } catch {
      // Logout even if server call fails
    }
    localStorage.removeItem("auth_token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
