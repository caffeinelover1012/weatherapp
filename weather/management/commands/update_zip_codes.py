from django.core.management.base import BaseCommand
from weather.models import Customer
import requests

API_KEY = 'AIzaSyBJB4L6udpCiLujeNeseP548aYJa1m4pwM'

def get_zip_from_address(address):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(endpoint)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:
        address_components = data['results'][0].get('address_components', [])
        for component in address_components:
            if 'postal_code' in component['types']:
                return component['long_name']

    return None


class Command(BaseCommand):
    help = 'Update missing or invalid zip codes from address'

    def handle(self, *args, **options):
        for customer in Customer.objects.all():
            new_zip_code = get_zip_from_address(customer.address)
            
            if new_zip_code is None:
                self.stdout.write(self.style.WARNING(f'Could not fetch zip code for customer {customer.id}'))
                continue

            if customer.zip_code is None or customer.zip_code != new_zip_code:
                customer.zip_code = new_zip_code
                customer.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated zip code for customer {customer.id}'))

        self.stdout.write(self.style.SUCCESS('Done updating zip codes'))