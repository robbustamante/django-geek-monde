import Link from "next/link";
import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.content}>
        <div className={styles.section}>
          <h3>Geek Monde</h3>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem', lineHeight: '1.6' }}>
            Tu destino definitivo para cultura pop, gaming y coleccionables.
          </p>
        </div>
        
        <div className={styles.section}>
          <h3>Enlaces</h3>
          <div className={styles.links}>
            <Link href="/catalog" className={styles.link}>Catálogo</Link>
            <Link href="/discounts" className={styles.link}>Ofertas Especiales</Link>
            <Link href="/about" className={styles.link}>Sobre Nosotros</Link>
          </div>
        </div>
        
        <div className={styles.section}>
          <h3>Soporte</h3>
          <div className={styles.links}>
            <Link href="/faq" className={styles.link}>Preguntas Frecuentes</Link>
            <Link href="/shipping" className={styles.link}>Envíos y Devoluciones</Link>
            <Link href="/contact" className={styles.link}>Contacto</Link>
          </div>
        </div>
      </div>
      
      <div className={styles.bottom}>
        <p>&copy; {new Date().getFullYear()} Geek Monde. Todos los derechos reservados.</p>
      </div>
    </footer>
  );
}
