"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import styles from "./Payment.module.css";
import CreditCardForm from "@/components/payment/CreditCardForm";

interface OrderData {
  id: number;
  number: string;
  total_amount: string;
  status: string;
}

export default function PaymentPage() {
  const router = useRouter();
  const params = useParams();
  const orderNumber = params.orderNumber as string;
  const { user, isLoading: authLoading } = useAuth();
  
  const [order, setOrder] = useState<OrderData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    if (!authLoading && user === null) {
      router.push(`/login?next=/checkout/payment/${orderNumber}`);
      return;
    }
    
    if (user) {
      const fetchOrder = async () => {
        try {
          const data = await apiFetch(`/api/v1/order/${orderNumber}/`);
          
          if (data.status !== 'pending') {
            throw new Error(`Esta orden ya no está pendiente de pago (Estado: ${data.status})`);
          }
          setOrder(data);
        } catch (err: any) {
          setError(err.message || "Error al cargar la orden");
        } finally {
          setLoading(false);
        }
      };
      
      fetchOrder();
    }
  }, [user, orderNumber, router]);

  const handlePayment = async (data: { method: string, provider: string }) => {
    if (!order) return;
    
    setIsSubmitting(true);
    setError("");
    
    try {
      // Usamos el endpoint general de pago como simulador
      await apiFetch("/api/v1/payment/create_payment/", {
        method: "POST",
        body: {
          order_id: order.id,
          method: data.method,
          provider: data.provider
        }
      });
      
      // En una integración real con Stripe, aquí manejaríamos el client_secret
      // y confirmaríamos con Stripe.js. Por ahora, asumimos éxito inmediato.
      setIsSuccess(true);
      
    } catch (err: any) {
      setError(err.message || err.data?.error || "Ocurrió un error al procesar la tarjeta");
      setIsSubmitting(false);
    }
  };

  if (loading || authLoading || !user) {
    return <div className={styles.loading}>Cargando plataforma de pago...</div>;
  }

  if (isSuccess) {
    return (
      <div className={styles.container}>
        <div className={styles.successContainer}>
          <div className={styles.successIcon}>✨</div>
          <h1 className={styles.successTitle}>¡Pago Exitoso!</h1>
          <p className={styles.successText}>
            Tu orden <strong>#{order?.number}</strong> ha sido procesada correctamente.<br/>
            Te enviamos un comprobante por correo electrónico.
          </p>
          <Link href="/" className={styles.homeBtn}>
            Volver a la Tienda
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        <span className="text-gradient">Pago Seguro</span>
      </h1>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.layout}>
        {/* Left side: Interactive Card Form */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Ingresa tu tarjeta</h2>
          <CreditCardForm 
            onSubmit={handlePayment} 
            isSubmitting={isSubmitting} 
          />
        </div>

        {/* Right side: Summary */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Resumen a Pagar</h2>
          <div className={styles.summaryItem}>
            <span>Orden</span>
            <span>#{order?.number}</span>
          </div>
          <div className={styles.summaryItem}>
            <span>Envío</span>
            <span>Gratis</span>
          </div>
          <div className={styles.summaryTotal}>
            <span>Total</span>
            <span className="text-gradient">${order?.total_amount}</span>
          </div>
          <div style={{ marginTop: '2rem', fontSize: '0.85rem', color: '#888', textAlign: 'center' }}>
            🔒 Transacción cifrada con encriptación de 256 bits.
          </div>
        </div>
      </div>
    </div>
  );
}
