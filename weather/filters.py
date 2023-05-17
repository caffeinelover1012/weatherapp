import django_filters
from fuzzywuzzy import fuzz
from django.db.models import Q
from .models import Customer
from .utils import get_nearby_zip_codes
    
class CustomerFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    zip_code = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Customer
        fields = ['full_name', 'zip_code']