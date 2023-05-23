import re
import pandas as pd
from openpyxl import load_workbook
import requests
from uszipcode import SearchEngine
from .models import Customer
API_KEY = '42c4aedf6be59e305e18ba215a373a9b'

unique_zip_codes = set(Customer.objects.exclude(zip_code__isnull=True).values_list('zip_code', flat=True))

def get_rain_affected_zips():
    # return a subset of unique_zip_codes where rain is >0.25
    affected_zips = []
    return set(affected_zips)

def get_wind_affected_zips():
        # return a subset of unique_zip_codes where wind is >30mph
    affected_zips = []

    return set(affected_zips)

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
