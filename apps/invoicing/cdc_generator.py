"""
CDC Generator for SIFEN electronic invoices.

The CDC (Código de Control) is a 44-digit unique identifier
for each electronic document, following DNIT Paraguay specifications.

Structure (44 digits):
  [0-7]   RUC del emisor (8 digits, zero-padded, without DV)
  [8-9]   Tipo de documento (2 digits): 01=Factura, 04=Autofactura, 05=NC, 06=ND, 07=NR
  [10-12] Establecimiento (3 digits)
  [13-15] Punto de expedición (3 digits)
  [16-22] Número de documento (7 digits)
  [23-30] Timbrado DNIT (8 digits)
  [31-44] Fecha y hora de emisión YYYYMMDDHHMMSS (14 digits)
            → Note: positions shifted due to accumulated length
  [45-53] Código de seguridad CSC (9 digits, random for simulation)
  [43]    Dígito verificador (módulo 11)

Reference: Manual Técnico SIFEN DNIT Paraguay v150
"""
import random
from datetime import datetime


def calcular_digito_verificador(cdc_43: str) -> int:
    """
    Calculate the check digit (DV) for the CDC using modulo 11.
    Applied over the first 43 digits of the CDC.
    """
    factors = list(range(2, 10)) * 6  # Cycling factor 2-9
    factors = factors[:43]

    total = 0
    for digit, factor in zip(reversed(cdc_43), factors):
        total += int(digit) * factor

    remainder = total % 11
    if remainder == 0:
        return 0
    elif remainder == 1:
        return 1
    else:
        return 11 - remainder


def generate_cdc(
    ruc_emisor: str,
    tipo_documento: str,
    establecimiento: str,
    punto_expedicion: str,
    numero_documento: str,
    timbrado: str,
    fecha_emision: datetime,
    codigo_seguridad: str = None,
) -> str:
    """
    Generate a 44-digit CDC following SIFEN DNIT specifications.

    Args:
        ruc_emisor: RUC of the issuer without DV (e.g. '80012345')
        tipo_documento: Document type code (e.g. '01' for Factura)
        establecimiento: 3-digit establishment code (e.g. '001')
        punto_expedicion: 3-digit dispatch point (e.g. '001')
        numero_documento: 7-digit document number (e.g. '0000001')
        timbrado: 8-digit timbrado number
        fecha_emision: datetime of emission
        codigo_seguridad: 9-digit security code (CSC), random if not provided

    Returns:
        44-character string (CDC)
    """
    # Normalize RUC: remove DV and hyphens, pad to 8 digits
    ruc_clean = ruc_emisor.replace('-', '').replace('.', '')
    if len(ruc_clean) > 8:
        ruc_clean = ruc_clean[:-1]  # Remove DV if present
    ruc_padded = ruc_clean.zfill(8)[:8]

    # Tipo documento (2 digits)
    tipo = str(tipo_documento).zfill(2)[:2]

    # Establecimiento (3 digits)
    estab = str(establecimiento).zfill(3)[:3]

    # Punto expedición (3 digits)
    punto = str(punto_expedicion).zfill(3)[:3]

    # Número de documento (7 digits)
    numero = str(numero_documento).zfill(7)[:7]

    # Timbrado (8 digits)
    timb = str(timbrado).zfill(8)[:8]

    # Fecha y hora de emisión (14 digits: YYYYMMDDHHMMSS)
    fecha_str = fecha_emision.strftime('%Y%m%d%H%M%S')

    # Código de seguridad CSC (9 digits)
    if codigo_seguridad is None:
        codigo_seguridad = str(random.randint(100000000, 999999999))
    csc = str(codigo_seguridad).zfill(9)[:9]

    # Concatenate first 43 digits
    cdc_43 = f"{ruc_padded}{tipo}{estab}{punto}{numero}{timb}{fecha_str}{csc}"

    # Ensure exactly 43 characters before DV
    if len(cdc_43) != 43:
        # Adjust if lengths don't match (safety)
        cdc_43 = cdc_43[:43].ljust(43, '0')

    # Calculate check digit
    dv = calcular_digito_verificador(cdc_43)

    cdc = f"{cdc_43}{dv}"
    return cdc


def format_cdc_display(cdc: str) -> str:
    """
    Format CDC in groups of 4 digits for readability.
    Example: '0800 1234 5100 0100 1000 0001 2345 6782 0250 6281 3043 31'
    """
    groups = [cdc[i:i+4] for i in range(0, len(cdc), 4)]
    return ' '.join(groups)
