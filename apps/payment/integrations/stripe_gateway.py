import stripe
from django.conf import settings
from .base import PaymentGatewayInterface

class StripeGateway(PaymentGatewayInterface):
    """
    Stripe implementation of the PaymentGatewayInterface.
    """
    
    def __init__(self):
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        
    def create_intent(self, order, amount, **kwargs):
        """
        Creates a Stripe PaymentIntent.
        Note: Stripe expects the amount in cents.
        """
        amount_in_cents = int(amount * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='usd', # Or your default currency
            metadata={
                'order_id': order.id,
                'order_number': order.number
            }
        )
        
        return {
            'intent_id': intent.id,
            'client_secret': intent.client_secret
        }
        
    def confirm_payment(self, payment_id, payload):
        # Manually confirm if necessary, usually handled on the frontend via Stripe.js
        # and verified via Webhooks
        return stripe.PaymentIntent.confirm(payment_id)
        
    def process_webhook(self, payload, signature):
        """
        Validates and processes a Stripe webhook.
        Returns the parsed event if valid, otherwise raises ValueError/stripe.error.SignatureVerificationError.
        """
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        event = stripe.Webhook.construct_event(
            payload, signature, endpoint_secret
        )
        
        return event
