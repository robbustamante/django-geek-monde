import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    """
    Filtros avanzados para productos.
    """
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    clothing_type = django_filters.CharFilter(field_name='clothing_type', lookup_expr='iexact')
    geek_category = django_filters.CharFilter(field_name='geek_category', lookup_expr='iexact')
    size = django_filters.CharFilter(field_name='variants__size', lookup_expr='iexact')
    color = django_filters.CharFilter(field_name='variants__color', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'is_active', 'clothing_type', 'geek_category']
