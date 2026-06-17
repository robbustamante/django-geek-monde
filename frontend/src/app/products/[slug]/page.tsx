"use client";

import { use, useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import styles from "./ProductDetail.module.css";
import Link from "next/link";

interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: string;
  image?: string;
  thumbnail?: string;
  category: {
    name: string;
    slug: string;
  };
  sku: string;
  size?: string;
  color?: string;
  material?: string;
  geek_category?: string;
  character_name?: string;
  franchise?: string;
  clothing_type?: string;
  gender_fit?: string;
}

export default function ProductDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  // En Next.js > 15, params es una Promesa
  const resolvedParams = use(params);
  const slug = resolvedParams.slug;

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Variantes (Si es ropa, podríamos tener múltiples talles. Acá simularemos talles si no vienen de la API aún)
  const [selectedSize, setSelectedSize] = useState<string>("");

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await apiFetch(`/api/v1/catalog/products/${slug}/`);
        if (!res.ok) {
          if (res.status === 404) throw new Error("Producto no encontrado");
          throw new Error("Error al cargar el producto");
        }
        const data = await res.json();
        setProduct(data);
        if (data.size) setSelectedSize(data.size);
        else setSelectedSize("M"); // Default temporal
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [slug]);

  const handleAddToCart = async () => {
    if (!product) return;
    setIsAdding(true);
    try {
      const res = await apiFetch("/api/v1/cart/items/", {
        method: "POST",
        body: JSON.stringify({
          product_id: product.id,
          quantity: quantity,
        }),
      });

      if (!res.ok) {
        const errBody = await res.text();
        throw new Error(`Error: ${errBody}`);
      }

      setIsSuccess(true);
      setTimeout(() => setIsSuccess(false), 2000);
    } catch (err) {
      alert("No se pudo agregar al carrito");
    } finally {
      setIsAdding(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Escaneando base de datos...</div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || "Producto no encontrado"}</div>
        <Link href="/" style={{ color: 'var(--color-accent-cyan)', display: 'block', textAlign: 'center' }}>
          Volver a la terminal principal
        </Link>
      </div>
    );
  }

  const image = product.image || product.thumbnail;

  return (
    <div className={styles.container}>
      <div className={styles.productWrapper}>
        <div className={styles.imageSection}>
          <div className={styles.mainImageContainer}>
            {image ? (
              <img src={image} alt={product.name} className={styles.mainImage} />
            ) : (
              <div className={styles.noImage}>SIN IMAGEN EN SISTEMA</div>
            )}
          </div>
        </div>

        <div className={styles.infoSection}>
          <div className={styles.header}>
            <div className={styles.category}>{product.category?.name || "Catálogo"}</div>
            <h1 className={styles.title}>{product.name}</h1>
            <div className={styles.price}>${product.price}</div>
          </div>

          <p className={styles.description}>
            {product.description || "Sin descripción disponible en la base de datos central."}
          </p>

          <div className={styles.options}>
            <div className={styles.optionGroup}>
              <span className={styles.optionLabel}>Talle / Configuración</span>
              <div className={styles.sizeGrid}>
                {['S', 'M', 'L', 'XL', 'XXL'].map(size => (
                  <button
                    key={size}
                    className={`${styles.sizeBtn} ${selectedSize === size ? styles.selected : ''}`}
                    onClick={() => setSelectedSize(size)}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.actions}>
              <div className={styles.qtyControls}>
                <button 
                  className={styles.qtyBtn} 
                  onClick={() => setQuantity(q => Math.max(1, q - 1))}
                >−</button>
                <span className={styles.qtyValue}>{quantity}</span>
                <button 
                  className={styles.qtyBtn} 
                  onClick={() => setQuantity(q => q + 1)}
                >+</button>
              </div>

              <button 
                className={`${styles.addToCartBtn} ${isSuccess ? styles.successBtn : ''}`}
                onClick={handleAddToCart}
                disabled={isAdding}
              >
                {isAdding ? "PROCESANDO..." : isSuccess ? "¡AÑADIDO AL INVENTARIO!" : "AÑADIR AL CARRITO"}
              </button>
            </div>
          </div>

          <div className={styles.meta}>
            <div>SKU: <span>{product.sku}</span></div>
            {product.franchise && <div>Franquicia: <span>{product.franchise}</span></div>}
            {product.material && <div>Material: <span>{product.material}</span></div>}
          </div>
        </div>
      </div>
    </div>
  );
}
