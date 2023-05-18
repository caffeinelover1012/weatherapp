from django import forms
from django_filters import FilterSet, CharFilter, ChoiceFilter
from .models import Customer
from django_filters import FilterSet, BooleanFilter
from django.forms import CheckboxInput
from .utils import get_affected_zip_codes  # import the method for getting zip codes


WEATHER_CHOICES = [('Rain', 'Rain'),
        ('Clouds', 'Clouds'),
        ('Sun', 'Sun')]

class CustomerFilter(FilterSet):
    full_name = CharFilter(field_name='full_name', lookup_expr='icontains', label='Full Name')
    zip_code = CharFilter(field_name='zip_code', lookup_expr='icontains', label='Zip Code')
    search_by = ChoiceFilter(field_name='zip_code', lookup_expr='in', label='Search by', 
                             choices=WEATHER_CHOICES, method='filter_by_weather')
    exclude_missing_contact = BooleanFilter(method='exclude_missing_contact_info', widget=CheckboxInput)

    class Meta:
        model = Customer
        fields = ['full_name', 'zip_code','search_by', 'exclude_missing_contact']

    def filter_by_weather(self, queryset, name, value):
        if value:
            affected_zip_codes = get_affected_zip_codes(value)  # get the zip codes affected by the weather
            return queryset.filter(zip_code__in=affected_zip_codes)
        return queryset
    
    def exclude_missing_contact_info(self, queryset, name, value):
        if value:  # if checkbox is checked
            return queryset.exclude(phone_number=None).exclude(email__isnull=True).exclude(email__iexact='nan')
        else:
            return queryset