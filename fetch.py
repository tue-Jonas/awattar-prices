import requests
import json
from datetime import datetime, timedelta

# fetch from awattar api
def fetch_data(start_date, end_date, api_url):
    params = {
        'start': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end': end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: HTTP Code {response.status_code}")
        return None

# save data to json file
def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# define constants
API_URL = 'https://api.awattar.at/v1/marketdata'
START_DATE = datetime.now() - timedelta(days=365 * 5)  # last 5 years
END_DATE = datetime.now()

# fetch data and save to file
data = fetch_data(START_DATE, END_DATE, API_URL)
if data:
    save_data(data, 'awattar_data.json')
