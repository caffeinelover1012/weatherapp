from django.core.management.base import BaseCommand
from weather.models import Customer
import requests

API_KEY = 'AIzaSyBJB4L6udpCiLujeNeseP548aYJa1m4pwM'

def get_zip_from_address(address):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(endpoint)
    data = response.json()
    print(data)
    if 'results' in data and len(data['results']) > 0:
        address_components = data['results'][0].get('address_components', [])
        for component in address_components:
            if 'postal_code' in component['types']:
                return component['long_name']

    return None


class Command(BaseCommand):
    help = 'Update missing zip codes from address'

    def handle(self, *args, **options):
        for customer in Customer.objects.filter(zip_code=None):
            print('a')
            customer.zip_code = get_zip_from_address(customer.address)
            customer.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated zip codes'))