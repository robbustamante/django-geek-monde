from django.contrib import admin
from .models import Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
