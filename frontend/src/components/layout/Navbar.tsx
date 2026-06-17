"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  return (
    <nav className={styles.navbar}>
      <Link href="/" className={styles.logo}>
        <span className={styles.logoText}>Geek Monde</span>
      </Link>
      
      <div className={styles.navLinks}>
        <Link href="/catalog" className={styles.link}>Catálogo</Link>
        <Link href="/discounts" className={styles.link}>Ofertas</Link>
        <Link href="/collections" className={styles.link}>Colecciones</Link>
      </div>
      
      <div className={styles.actions}>
        <button className={styles.iconBtn} aria-label="Buscar">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </button>

        {isLoading ? null : isAuthenticated ? (
          <>
            <span className={styles.userEmail}>{user?.email}</span>
            <button className={styles.iconBtn} onClick={logout} aria-label="Cerrar sesión" title="Cerrar sesión">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
            </button>
          </>
        ) : (
          <Link href="/login" className={styles.iconBtn} aria-label="Iniciar sesión" title="Iniciar sesión">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </Link>
        )}

        <Link href="/cart" className={styles.iconBtn} aria-label="Carrito">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
        </Link>
      </div>
    </nav>
  );
}

