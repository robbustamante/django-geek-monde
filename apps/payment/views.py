from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class PaymentMethodListView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        methods = [
            {'id': 'credit_card', 'name': 'Credit Card'},
            {'id': 'debit_card', 'name': 'Debit Card'},
            {'id': 'bank_transfer', 'name': 'Bank Transfer'},
            {'id': 'cash', 'name': 'Cash'},
        ]
        return Response(methods)
