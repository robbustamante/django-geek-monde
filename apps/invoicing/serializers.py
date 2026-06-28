"""
Serializers for the SIFEN electronic invoicing app.
"""
from rest_framework import serializers
from apps.invoicing.models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    tasa_iva_display = serializers.CharField(read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'descripcion',
            'cantidad',
            'precio_unitario',
            'tasa_iva',
            'tasa_iva_display',
            'subtotal_item',
            'iva_item',
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    numero_display = serializers.CharField(read_only=True)
    cdc_display = serializers.CharField(read_only=True)
    tipo_documento_display = serializers.CharField(
        source='get_tipo_documento_display', read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condicion_venta_display = serializers.CharField(
        source='get_condicion_venta_display', read_only=True
    )
    kude_url = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id',
            'cdc',
            'cdc_display',
            'numero_display',
            'tipo_documento',
            'tipo_documento_display',
            'timbrado',
            'timbrado_fecha_inicio',
            'status',
            'status_display',
            'issued_at',
            'receptor_tipo_doc',
            'receptor_ruc',
            'receptor_nombre',
            'receptor_direccion',
            'receptor_email',
            'condicion_venta',
            'condicion_venta_display',
            'moneda',
            'subtotal_gravado10',
            'subtotal_gravado5',
            'subtotal_exento',
            'total_iva10',
            'total_iva5',
            'total_iva',
            'total_general',
            'qr_url',
            'kude_url',
            'items',
            'created_at',
            'updated_at',
        ]

    def get_kude_url(self, obj):
        """Return absolute URL to download the KuDE PDF."""
        request = self.context.get('request')
        if obj.kude_pdf and request:
            return request.build_absolute_uri(obj.kude_pdf.url)
        return None


class InvoiceListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing invoices."""
    numero_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    kude_url = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id',
            'cdc',
            'numero_display',
            'status',
            'status_display',
            'issued_at',
            'receptor_nombre',
            'total_general',
            'moneda',
            'kude_url',
        ]

    def get_kude_url(self, obj):
        request = self.context.get('request')
        if obj.kude_pdf and request:
            return request.build_absolute_uri(obj.kude_pdf.url)
        return None
