"""
API views for the SIFEN electronic invoicing app.
"""
import logging
from django.http import FileResponse, Http404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.invoicing.models import Invoice
from apps.invoicing.serializers import InvoiceSerializer, InvoiceListSerializer
from apps.invoicing.services import InvoiceService

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(summary='List my electronic invoices'),
    retrieve=extend_schema(summary='Get invoice detail'),
)
class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for electronic invoices (SIFEN KuDE).

    Customers can view their own invoices and download the KuDE PDF.
    Staff users can see all invoices and perform admin actions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Invoice.objects.select_related(
            'order__user'
        ).prefetch_related('items')

        if user.is_staff:
            return qs.all()
        # Regular customers see only their own invoices
        return qs.filter(order__user=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer

    @extend_schema(summary='Download KuDE PDF')
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """
        Download the KuDE (Kuatia Documento Electrónico) PDF for this invoice.
        """
        invoice = self.get_object()

        if not invoice.kude_pdf:
            # Try regenerating on-the-fly
            ok = InvoiceService.regenerate_kude(invoice)
            if not ok:
                return Response(
                    {'detail': 'KuDE PDF not available for this invoice.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        filename = f"factura_{invoice.numero_display}.pdf"
        response = FileResponse(
            invoice.kude_pdf.open('rb'),
            content_type='application/pdf',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @extend_schema(summary='Resend KuDE by email')
    @action(detail=True, methods=['post'], url_path='send-email')
    def send_email(self, request, pk=None):
        """
        Resend the KuDE PDF to the customer's email.
        """
        invoice = self.get_object()

        if invoice.status == Invoice.STATUS_CANCELLED:
            return Response(
                {'detail': 'Cannot send email for a cancelled invoice.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        InvoiceService.send_kude_email_sync(invoice)
        return Response({'detail': f'KuDE sent to {invoice.receptor_email}.'})

    @extend_schema(summary='Issue invoice for an order (staff only)')
    @action(
        detail=False,
        methods=['post'],
        url_path='issue',
        permission_classes=[permissions.IsAdminUser],
    )
    def issue(self, request):
        """
        Manually issue an invoice for an order (staff only).
        Body: { "order_id": <int> }
        """
        from apps.order.models import Order

        order_id = request.data.get('order_id')
        if not order_id:
            return Response(
                {'detail': 'order_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.prefetch_related('items__product').get(pk=order_id)
        except Order.DoesNotExist:
            return Response(
                {'detail': f'Order {order_id} not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        invoice = InvoiceService.issue_invoice(order)
        serializer = InvoiceSerializer(invoice, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary='Cancel an invoice (staff only)')
    @action(
        detail=True,
        methods=['post'],
        url_path='cancel',
        permission_classes=[permissions.IsAdminUser],
    )
    def cancel(self, request, pk=None):
        """
        Cancel an issued invoice (staff only).
        Body: { "motivo": "..." }
        """
        invoice = self.get_object()
        motivo = request.data.get('motivo', '')

        try:
            invoice = InvoiceService.cancel_invoice(invoice, motivo=motivo)
        except ValueError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = InvoiceSerializer(invoice, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary='Regenerate KuDE PDF (staff only)')
    @action(
        detail=True,
        methods=['post'],
        url_path='regenerate-kude',
        permission_classes=[permissions.IsAdminUser],
    )
    def regenerate_kude(self, request, pk=None):
        """Regenerate the KuDE PDF for an existing invoice (staff only)."""
        invoice = self.get_object()
        ok = InvoiceService.regenerate_kude(invoice)
        if ok:
            return Response({'detail': 'KuDE PDF regenerated successfully.'})
        return Response(
            {'detail': 'Failed to regenerate KuDE PDF.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
