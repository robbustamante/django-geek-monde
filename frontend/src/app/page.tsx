import ProductCard from "@/components/ui/ProductCard";
import styles from "./Home.module.css";

async function getProducts() {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/v1/catalog/products/', { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`Failed to fetch data: ${res.status}`);
    }
    return res.json();
  } catch (error) {
    console.error("Error fetching products:", error);
    return null;
  }
}

export default async function Home() {
  const data = await getProducts();
  const products = data?.results || [];

  return (
    <main className={styles.main}>
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroBg}></div>
        <div className={styles.heroContent}>
          <h1 className={styles.title}>
            Lleva tu pasión al <span className="text-gradient">siguiente nivel</span>
          </h1>
          <p className={styles.subtitle}>
            Ropa exclusiva, coleccionables de edición limitada y el mejor equipamiento para tu setup. 
            Adéntrate en el universo Geek Monde.
          </p>
          <a href="#catalog" className={styles.ctaBtn}>
            Explorar Catálogo
          </a>
        </div>
      </section>

      {/* Catalog Section */}
      <section id="catalog" className={styles.catalog}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Últimos Lanzamientos</h2>
        </div>

        {!data ? (
          <div className={styles.errorBox}>
            <h3>No se pudo conectar con la API</h3>
            <p>Asegúrate de que el servidor de Django esté corriendo en el puerto 8000.</p>
            <code>
              # En otra terminal, corre:<br/>
              python manage.py runserver
            </code>
          </div>
        ) : products.length === 0 ? (
          <div className={styles.emptyBox}>
            <p>La conexión funciona, pero no hay productos en la base de datos.</p>
          </div>
        ) : (
          <div className={styles.grid}>
            {products.map((product: any) => (
              <ProductCard key={product.id || product.slug} product={product} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
