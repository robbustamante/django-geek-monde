"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import styles from "./Checkout.module.css";
import { useAuth } from "@/context/AuthContext";

interface Address {
  id: number;
  name: string;
  street_address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

interface CartData {
  id: number;
  items_count: number;
  subtotal: number;
  total: number;
}

export default function CheckoutPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [cart, setCart] = useState<CartData | null>(null);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);
  const [isAddingNew, setIsAddingNew] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    street_address: "",
    city: "",
    state: "",
    postal_code: "",
    country: "",
  });

  const fetchData = useCallback(async () => {
    try {
      // Fetch cart
      const cartRes = await apiFetch("/api/v1/cart/");
      if (!cartRes.ok) throw new Error("Error al cargar carrito");
      const cartData = await cartRes.json();
      
      if (cartData.items_count === 0) {
        router.push("/cart");
        return;
      }
      setCart(cartData);

      // Fetch addresses
      const addrRes = await apiFetch("/api/v1/customer/addresses/");
      if (addrRes.ok) {
        const addrData = await addrRes.json();
        setAddresses(addrData);
        if (addrData.length > 0) {
          const def = addrData.find((a: Address) => a.is_default) || addrData[0];
          setSelectedAddressId(def.id);
        } else {
          setIsAddingNew(true);
        }
      }
    } catch (err) {
      setError("Error al cargar los datos de checkout");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!authLoading && user === null) {
      // User is loaded but not authenticated
      router.push("/login?next=/checkout");
    } else if (user) {
      fetchData();
    }
  }, [user, authLoading, fetchData, router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleProceed = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      let finalAddressId = selectedAddressId;

      // If adding new address, save it first
      if (isAddingNew || addresses.length === 0) {
        const addrRes = await apiFetch("/api/v1/customer/addresses/", {
          method: "POST",
          body: JSON.stringify(formData),
        });
        
        if (!addrRes.ok) throw new Error("Error al guardar la dirección");
        const newAddress = await addrRes.json();
        finalAddressId = newAddress.id;
      }

      if (!finalAddressId) {
        throw new Error("Debe seleccionar o ingresar una dirección de envío");
      }

      // Create order
      const orderRes = await apiFetch("/api/v1/order/", {
        method: "POST",
        body: JSON.stringify({ shipping_address_id: finalAddressId }),
      });

      if (!orderRes.ok) {
        const errorData = await orderRes.json();
        console.error("Order error", errorData);
        throw new Error("Error al crear la orden. " + (errorData.error || ""));
      }

      const orderData = await orderRes.json();
      
      // Navigate to payment screen
      router.push(`/checkout/payment/${orderData.number}`);

    } catch (err: any) {
      setError(err.message || "Ocurrió un error inesperado");
      setSubmitting(false);
    }
  };

  if (loading || authLoading || !user) {
    return <div className={styles.container}>Cargando datos...</div>;
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        <span className="text-gradient">Checkout</span>
      </h1>

      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      <div className={styles.layout}>
        {/* Left side: Address Selection / Form */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>1. Dirección de Envío</h2>
          
          {addresses.length > 0 && !isAddingNew && (
            <div className={styles.addressesList}>
              {addresses.map((addr) => (
                <div
                  key={addr.id}
                  className={`${styles.addressCard} ${selectedAddressId === addr.id ? styles.selected : ""}`}
                  onClick={() => setSelectedAddressId(addr.id)}
                >
                  <div className={styles.addressName}>{addr.name}</div>
                  <div className={styles.addressDetails}>
                    {addr.street_address}<br />
                    {addr.city}, {addr.state} {addr.postal_code}<br />
                    {addr.country}
                  </div>
                </div>
              ))}
              <button 
                className={styles.addNewBtn}
                onClick={() => setIsAddingNew(true)}
              >
                + Añadir nueva dirección
              </button>
            </div>
          )}

          {(isAddingNew || addresses.length === 0) && (
            <form id="checkout-form" onSubmit={handleProceed} className={styles.form}>
              <div className={`${styles.inputGroup} ${styles.fullWidth}`}>
                <label>Nombre Completo</label>
                <input required type="text" name="name" value={formData.name} onChange={handleInputChange} />
              </div>
              <div className={`${styles.inputGroup} ${styles.fullWidth}`}>
                <label>Dirección (Calle y Número)</label>
                <input required type="text" name="street_address" value={formData.street_address} onChange={handleInputChange} />
              </div>
              <div className={styles.inputGroup}>
                <label>Ciudad</label>
                <input required type="text" name="city" value={formData.city} onChange={handleInputChange} />
              </div>
              <div className={styles.inputGroup}>
                <label>Provincia / Estado</label>
                <input required type="text" name="state" value={formData.state} onChange={handleInputChange} />
              </div>
              <div className={styles.inputGroup}>
                <label>Código Postal</label>
                <input required type="text" name="postal_code" value={formData.postal_code} onChange={handleInputChange} />
              </div>
              <div className={styles.inputGroup}>
                <label>País</label>
                <input required type="text" name="country" value={formData.country} onChange={handleInputChange} />
              </div>
              
              {addresses.length > 0 && (
                <div className={styles.fullWidth}>
                  <button 
                    type="button" 
                    className={styles.addNewBtn}
                    onClick={() => setIsAddingNew(false)}
                  >
                    Volver a mis direcciones guardadas
                  </button>
                </div>
              )}
            </form>
          )}
        </div>

        {/* Right side: Cart Summary */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Resumen de Orden</h2>
          <div className={styles.summaryItem}>
            <span>Items ({cart?.items_count})</span>
            <span>${cart?.subtotal.toFixed(2)}</span>
          </div>
          <div className={styles.summaryItem}>
            <span>Envío</span>
            <span>Gratis</span>
          </div>
          <div className={styles.summaryTotal}>
            <span>Total a Pagar</span>
            <span className="text-gradient">${cart?.total.toFixed(2)}</span>
          </div>

          <button 
            type="submit" 
            form={isAddingNew || addresses.length === 0 ? "checkout-form" : undefined}
            onClick={(!isAddingNew && addresses.length > 0) ? handleProceed : undefined}
            className={styles.submitBtn} 
            disabled={submitting}
          >
            {submitting ? "Procesando..." : "Continuar al Pago"}
          </button>
        </div>
      </div>
    </div>
  );
}
