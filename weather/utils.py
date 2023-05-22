import re
import pandas as pd
from openpyxl import load_workbook
import requests
from uszipcode import SearchEngine
from .models import Customer

def get_affected_zip_codes(weather_condition):
    # All unique zip codes in the database
    unique_zip_codes = set(Customer.objects.exclude(zip_code__isnull=True).values_list('zip_code', flat=True))
    
    affected_zip_codes = set()  # Set to store unique affected zip codes

    for zip_code in unique_zip_codes:  # iterating through zip codes
        response = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key=ab0a585060344e8aaf670744232105&q={zip_code}&days=1&aqi=no')
        data = response.json()

        # If response contains 'error', the API request was unsuccessful
        if 'error' in data:
            # print(data['error']['message'])
            continue

        # Checking conditions for different weather parameters
        precip_in = data['forecast']['forecastday'][0]['day']['totalprecip_in']
        wind_mph = data['current']['wind_mph']

        if weather_condition.lower() == 'rain' and (precip_in >= 0.3 or wind_mph >= 30):
            affected_zip_codes.add(zip_code)

    return affected_zip_codes  # return the set of affected zip codes



def get_nearby_zip_codes(zipcode, radius):
    endpoint = f'https://www.zipcodeapi.com/rest/{API_KEY}/radius.json/{zipcode}/{radius}/mile'
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return [zip_info['zip_code'] for zip_info in data['zip_codes']]
    else:
        return []
    
def process_excel(file_name, nrows):
    # Load workbook
    wb = load_workbook(filename=file_name, read_only=True)
    ws = wb.active

    # Read the data into a DataFrame, skipping the first 5 rows and reading the next nrows
    df = pd.read_excel(file_name, usecols="B:G", nrows=nrows, skiprows=4)

    # Rename columns for easier access
    df.columns = ['Customer', 'PhoneNumbers', 'Email', 'FullName', 'BillingAddress', 'ShippingAddress']

    # Function to extract phone number
    def extract_phone_number(s):
        s = str(s)
        if 'Phone:' in s:
            return s.split('Phone:')[1].strip()
        return None

    # Function to extract zip code
    def extract_zip_code(s):
        s = str(s)
        match = re.search(r'\b\d{5}(?:-\d{4})?\b', s)
        if match:
            return match.group(0)
        return None
    
    # Apply the functions to the relevant columns
    df['PhoneNumbers'] = df['PhoneNumbers'].apply(extract_phone_number)
    df['ShippingAddress'] = df['BillingAddress'].apply(extract_zip_code)

    return df
