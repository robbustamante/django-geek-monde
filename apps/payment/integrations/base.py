from abc import ABC, abstractmethod

class PaymentGatewayInterface(ABC):
    """
    Base interface for all payment gateways (Stripe, MercadoPago, etc).
    """
    
    @abstractmethod
    def create_intent(self, order, amount, **kwargs):
        """
        Create a payment intent/preference with the provider.
        Should return a dict containing the intent ID and client secret or init point URL.
        """
        pass
        
    @abstractmethod
    def confirm_payment(self, payment_id, payload):
        """
        Confirm a payment manually if needed by the provider.
        """
        pass
        
    @abstractmethod
    def process_webhook(self, payload, signature):
        """
        Process incoming webhooks/IPN from the provider.
        """
        pass
