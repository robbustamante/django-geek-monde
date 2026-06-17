from rest_framework import serializers
from email_auth.models import User
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'name', 'street_address', 'city', 'state',
            'postal_code', 'country', 'is_default', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'addresses')
        read_only_fields = ('id',)
