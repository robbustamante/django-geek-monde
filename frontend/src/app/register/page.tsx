"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import styles from "../login/Login.module.css"; // reuse same styles

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password1 !== password2) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setLoading(true);
    const result = await register(email, password1, password2);

    if (result.ok) {
      router.push("/login");
    } else {
      setError(result.error || "Error al registrarse");
    }

    setLoading(false);
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>
          <span className="text-gradient">Crear Cuenta</span>
        </h1>
        <p className={styles.subtitle}>Únete al universo Geek Monde</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.field}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="password1">Contraseña</label>
            <input
              id="password1"
              type="password"
              placeholder="••••••••"
              value={password1}
              onChange={(e) => setPassword1(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="password2">Confirmar Contraseña</label>
            <input
              id="password2"
              type="password"
              placeholder="••••••••"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? "Registrando..." : "Crear Cuenta"}
          </button>
        </form>

        <div className={styles.footer}>
          ¿Ya tenés cuenta?{" "}
          <Link href="/login">Iniciar Sesión</Link>
        </div>
      </div>
    </div>
  );
}
