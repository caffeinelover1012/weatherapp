import re
import pandas as pd
from openpyxl import load_workbook
import requests
from uszipcode import SearchEngine

def get_rain_affected_zips(api_key, weather):
    if weather=="Sun":
        return set(['85281', '85280', '85234','85282'])
    search = SearchEngine()
    # A list of large cities to check. You could expand this list as needed.
    cities = ["Tempe", "Mesa", "Houston", "Phoenix", "Gilbert"]
    affected_zips = []

    for city in cities:
        # Get the current weather for the city
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city},us&appid={api_key}")
        data = response.json()

        print(data)

        # If the city is currently experiencing the specified weather, add all its zip codes to the list
        try:
            if data['weather'][0]['main'].lower() == weather.lower():
                zipcodes = search.by_city_and_state(city, "US")
                for zipcode in zipcodes:
                    affected_zips.append(zipcode.zipcode)
        except KeyError as e:
            print(f"Key error: {e}")

    return set(affected_zips)

def get_affected_zip_codes(weather_condition):
    # Add your logic to get the affected zip codes based on the weather condition
    x= get_rain_affected_zips('42c4aedf6be59e305e18ba215a373a9b',weather_condition)
    print("ZIPS",x)
    return x

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
