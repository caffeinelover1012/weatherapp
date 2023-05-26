import re
import pandas as pd
from openpyxl import load_workbook
import requests
from uszipcode import SearchEngine
from .models import Customer
import json
from django.core.cache import cache

unique_zip_codes = set(Customer.objects.exclude(zip_code__isnull=True).values_list('zip_code', flat=True))
affected_zips = set()

def get_rain_affected_zips():
    # return a subset of unique_zip_codes where rain is >0.25
    for zip_code in unique_zip_codes:  # iterating through zip codes
        response = requests.get(f'http://api.weatherapi.com/v1/current.json?key=ab0a585060344e8aaf670744232105&q={zip_code}&aqi=no')

        # Check if response is valid JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Invalid response for zip code: {zip_code}")
            continue  # Skip to next zip code

        if 'current' in data:
            precip_in = data['current']['precip_in']
            print(data)
            if precip_in >= 0.05:
                affected_zips.add(zip_code)
        else:
            print(f"No 'current' data for zip code: {zip_code}")

    return set(affected_zips)

def get_wind_affected_zips():
    # return a subset of unique_zip_codes where wind is >30mph
    for zip_code in unique_zip_codes:  # iterating through zip codes
        response = requests.get(f'http://api.weatherapi.com/v1/current.json?key=ab0a585060344e8aaf670744232105&q={zip_code}&aqi=no')

        # Check if response is valid JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Invalid response for zip code: {zip_code}")
            continue  # Skip to next zip code

        if 'current' in data:
            wind_mph = data['current']['wind_mph']
            if wind_mph >= 15:
                affected_zips.add(zip_code)
        else:
            print(f"No 'current' data for zip code: {zip_code}")
    return set(affected_zips)

def update_affected_zips():
    rain_affected_zips = get_rain_affected_zips()
    wind_affected_zips = get_wind_affected_zips()

    cache.set('rain_affected_zips', rain_affected_zips, 3600 * 6)  # Cache for 6 hours
    cache.set('wind_affected_zips', wind_affected_zips, 3600 * 6)  # Cache for 6 hours


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
