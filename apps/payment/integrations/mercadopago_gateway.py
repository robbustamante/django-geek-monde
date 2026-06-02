import mercadopago
from django.conf import settings
from django.urls import reverse
from .base import PaymentGatewayInterface

class MercadoPagoGateway(PaymentGatewayInterface):
    """
    MercadoPago implementation of the PaymentGatewayInterface.
    """
    
    def __init__(self):
        access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
        self.sdk = mercadopago.SDK(access_token)
        
    def create_intent(self, order, amount, **kwargs):
        """
        Creates a MercadoPago Preference.
        Returns the preference ID and the init_point URL.
        """
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': f'order_{order.id}'
        }
        
        preference_data = {
            "items": [
                {
                    "id": str(order.id),
                    "title": f"Order {order.number}",
                    "quantity": 1,
                    "currency_id": getattr(settings, 'DEFAULT_CURRENCY', 'ARS'),
                    "unit_price": float(amount)
                }
            ],
            "payer": {
                "email": order.user.email,
            },
            "external_reference": str(order.id),
            # Optional: back_urls to return to your frontend
            # "back_urls": {
            #     "success": "https://tusitio.com/success",
            #     "failure": "https://tusitio.com/failure",
            #     "pending": "https://tusitio.com/pending"
            # },
            # "auto_return": "approved",
        }
        
        preference_response = self.sdk.preference().create(preference_data, request_options)
        preference = preference_response["response"]
        
        return {
            'intent_id': preference['id'],
            'client_secret': preference['init_point'], # Reusing client_secret field for the init_point URL
            'init_point': preference['init_point']
        }
        
    def confirm_payment(self, payment_id, payload):
        """
        Not typically used manually in MP. Handled by webhook.
        """
        return {"status": "pending"}
        
    def process_webhook(self, payload, signature=None):
        """
        Process incoming IPN/Webhook from MercadoPago.
        In MP, we typically receive the Payment ID in the payload and query the API for status.
        payload = request.GET usually for IPN, or request.data for webhooks.
        """
        action = payload.get('action')
        data_id = payload.get('data', {}).get('id') or payload.get('id')
        
        if not data_id:
            raise ValueError("No payment ID provided")
            
        # Verify payment status with MP API
        payment_info = self.sdk.payment().get(data_id)
        
        if payment_info["status"] != 200:
            raise ValueError("Payment not found in MercadoPago")
            
        payment_data = payment_info["response"]
        
        # Return a structured event similar to what we expect
        return {
            'type': payment_data['status'], # 'approved', 'rejected', 'pending'
            'data': payment_data,
            'external_reference': payment_data.get('external_reference')
        }
