"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import styles from "./Cart.module.css";

interface CartItemData {
  id: number;
  product: {
    id: number;
    name: string;
    price: string;
    image?: string;
    thumbnail?: string;
    slug?: string;
  };
  quantity: number;
  subtotal: number;
}

interface CartData {
  id: number;
  items: CartItemData[];
  items_count: number;
  subtotal: number;
  discount_amount: number;
  total: number;
}

export default function CartPage() {
  const [cart, setCart] = useState<CartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchCart = useCallback(async () => {
    try {
      const data = await apiFetch("/api/v1/cart/");
      setCart(data);
    } catch (err) {
      setError("No se pudo cargar el carrito");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const updateQuantity = async (itemId: number, newQty: number) => {
    if (newQty <= 0) {
      await removeItem(itemId);
      return;
    }
    try {
      await apiFetch(`/api/v1/cart/items/${itemId}/`, {
        method: "PATCH",
        body: { quantity: newQty },
      });
      await fetchCart();
    } catch {
      alert("Error al actualizar la cantidad");
    }
  };

  const removeItem = async (itemId: number) => {
    try {
      await apiFetch(`/api/v1/cart/items/${itemId}/`, {
        method: "DELETE",
      });
      await fetchCart();
    } catch {
      alert("Error al eliminar el item");
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Cargando carrito...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error}</div>
      </div>
    );
  }

  const items = cart?.items || [];

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        <span className="text-gradient">Mi Carrito</span>
      </h1>

      {items.length === 0 ? (
        <div className={styles.emptyState}>
          <p>Tu carrito está vacío</p>
          <Link href="/#catalog" className={styles.shopBtn}>
            Explorar Catálogo
          </Link>
        </div>
      ) : (
        <>
          <div className={styles.itemsList}>
            {items.map((item) => (
              <div key={item.id} className={styles.item}>
                <div className={styles.itemImage}>
                  {(item.product.image || item.product.thumbnail) ? (
                    <img
                      src={item.product.image || item.product.thumbnail}
                      alt={item.product.name}
                    />
                  ) : (
                    <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-secondary)', fontSize: '0.7rem' }}>
                      Sin img
                    </div>
                  )}
                </div>

                <div className={styles.itemInfo}>
                  <div className={styles.itemName}>{item.product.name}</div>
                  <div className={styles.itemPrice}>${item.product.price} c/u</div>
                </div>

                <div className={styles.qtyControls}>
                  <button
                    className={styles.qtyBtn}
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                  >
                    −
                  </button>
                  <span className={styles.qtyValue}>{item.quantity}</span>
                  <button
                    className={styles.qtyBtn}
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  >
                    +
                  </button>
                </div>

                <div className={styles.itemSubtotal}>
                  ${item.subtotal.toFixed(2)}
                </div>

                <button
                  className={styles.removeBtn}
                  onClick={() => removeItem(item.id)}
                  aria-label="Eliminar"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
              </div>
            ))}
          </div>

          <div className={styles.summary}>
            <div className={styles.summaryRow}>
              <span>Subtotal ({cart?.items_count} items)</span>
              <span>${cart?.subtotal.toFixed(2)}</span>
            </div>
            {cart && cart.discount_amount > 0 && (
              <div className={styles.summaryRow}>
                <span>Descuento</span>
                <span style={{ color: 'var(--color-accent-cyan)' }}>
                  -${cart.discount_amount.toFixed(2)}
                </span>
              </div>
            )}
            <div className={`${styles.summaryRow} ${styles.totalRow}`}>
              <span>Total</span>
              <span>${cart?.total.toFixed(2)}</span>
            </div>
            <Link href="/checkout" className={styles.checkoutBtn}>
              Proceder al Pago
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
