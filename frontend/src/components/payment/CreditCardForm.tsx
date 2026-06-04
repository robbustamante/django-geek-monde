"use client";

import { useState, ChangeEvent } from "react";
import styles from "./CreditCardForm.module.css";

interface CreditCardFormProps {
  onSubmit: (data: { method: string, provider: string }) => Promise<void>;
  isSubmitting: boolean;
}

export default function CreditCardForm({ onSubmit, isSubmitting }: CreditCardFormProps) {
  const [cardNumber, setCardNumber] = useState("");
  const [cardName, setCardName] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");
  const [isFlipped, setIsFlipped] = useState(false);

  // Formatting helpers
  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || "";
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(" ");
    } else {
      return value;
    }
  };

  const formatExpiry = (value: string) => {
    const v = value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
    if (v.length >= 3) {
      return `${v.substring(0, 2)}/${v.substring(2, 4)}`;
    }
    return v;
  };

  const handleCardNumber = (e: ChangeEvent<HTMLInputElement>) => {
    setCardNumber(formatCardNumber(e.target.value));
  };

  const handleExpiry = (e: ChangeEvent<HTMLInputElement>) => {
    setExpiry(formatExpiry(e.target.value));
  };

  const handleCvv = (e: ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
    setCvv(v.substring(0, 4));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cardNumber || !cardName || !expiry || !cvv) return;
    
    // Call parent handler with the fake data
    onSubmit({ method: 'credit_card', provider: 'stripe' });
  };

  // Display values for the card visual
  const displayNum = cardNumber || "#### #### #### ####";
  const displayName = cardName || "NOMBRE DEL TITULAR";
  const displayExp = expiry || "MM/YY";
  const displayCvv = cvv || "###";

  return (
    <div className={styles.container}>
      {/* Visual Interactive 3D Card */}
      <div className={styles.cardScene}>
        <div className={`${styles.cardInner} ${isFlipped ? styles.isFlipped : ""}`}>
          
          {/* FRONT */}
          <div className={styles.cardFront}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className={styles.chip}></div>
              <div className={styles.cardLogo}>GeekPay</div>
            </div>
            
            <div className={styles.cardNumberDisplay}>
              {displayNum}
            </div>
            
            <div className={styles.cardDetails}>
              <div>
                <div className={styles.detailLabel}>Titular de la tarjeta</div>
                <div className={styles.detailValue}>{displayName}</div>
              </div>
              <div>
                <div className={styles.detailLabel}>Expira</div>
                <div className={styles.detailValue}>{displayExp}</div>
              </div>
            </div>
          </div>

          {/* BACK */}
          <div className={styles.cardBack}>
            <div className={styles.magneticStrip}></div>
            <div className={styles.cvvContainer}>
              <span className={styles.cvvLabel}>CVV</span>
              <div className={styles.cvvBox}>{displayCvv}</div>
            </div>
          </div>

        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.inputGroup}>
          <label>Número de Tarjeta</label>
          <input 
            type="text" 
            placeholder="0000 0000 0000 0000" 
            value={cardNumber}
            onChange={handleCardNumber}
            onFocus={() => setIsFlipped(false)}
            maxLength={19}
            required
          />
        </div>
        
        <div className={styles.inputGroup}>
          <label>Nombre del Titular</label>
          <input 
            type="text" 
            placeholder="Como aparece en la tarjeta"
            value={cardName}
            onChange={(e) => setCardName(e.target.value.toUpperCase())}
            onFocus={() => setIsFlipped(false)}
            required
          />
        </div>

        <div className={styles.inputRow}>
          <div className={styles.inputGroup}>
            <label>Vencimiento</label>
            <input 
              type="text" 
              placeholder="MM/YY"
              value={expiry}
              onChange={handleExpiry}
              onFocus={() => setIsFlipped(false)}
              maxLength={5}
              required
            />
          </div>
          <div className={styles.inputGroup}>
            <label>Código CVV</label>
            <input 
              type="text" 
              placeholder="123"
              value={cvv}
              onChange={handleCvv}
              onFocus={() => setIsFlipped(true)}
              onBlur={() => setIsFlipped(false)}
              maxLength={4}
              required
            />
          </div>
        </div>

        <button 
          type="submit" 
          className={styles.submitBtn}
          disabled={isSubmitting}
        >
          {isSubmitting ? "Procesando pago..." : "Pagar Ahora"}
        </button>
      </form>
    </div>
  );
}
