"use client";

import Link from "next/link";
import { useState } from "react";
import { apiFetch } from "@/lib/api";
import styles from "./ProductCard.module.css";

interface Product {
  id: string | number;
  name?: string;
  title?: string;
  price: string | number;
  image?: string;
  thumbnail?: string;
  slug?: string;
}

export default function ProductCard({ product }: { product: Product }) {
  const [isAdding, setIsAdding] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const title = product.name || product.title;
  const image = product.image || product.thumbnail;
  
  const handleAddToCart = async () => {
    setIsAdding(true);
    try {
      const res = await apiFetch("/api/v1/cart/items/", {
        method: "POST",
        body: JSON.stringify({
          product_id: product.id,
          quantity: 1,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Error ${res.status}: ${errText}`);
      }

      setIsSuccess(true);
      setTimeout(() => setIsSuccess(false), 2000);
    } catch (error: any) {
      console.error("Cart Error:", error);
      alert(error.message || "Error al añadir al carrito");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className={styles.card}>
      <Link href={`/products/${product.slug || product.id}`} className={styles.imageContainer}>
        {image ? (
          <img src={image} alt={title} className={styles.image} />
        ) : (
          <div className={styles.noImage}>Sin Imagen</div>
        )}
      </Link>
      
      <div className={styles.content}>
        <Link href={`/products/${product.slug || product.id}`}>
          <h3 className={styles.title}>{title}</h3>
        </Link>
        
        <div className={styles.footer}>
          <span className={styles.price}>${product.price}</span>
          <button 
            className={styles.addBtn} 
            onClick={handleAddToCart}
            disabled={isAdding}
            aria-label="Añadir al carrito"
            style={isSuccess ? { background: 'var(--color-accent-cyan)', color: 'var(--color-bg-primary)' } : {}}
          >
            {isAdding ? (
              <svg className="animate-spin" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            ) : isSuccess ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
