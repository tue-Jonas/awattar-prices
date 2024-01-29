import requests
import json
from datetime import datetime, timedelta
import pymysql
from influxdb import InfluxDBClient

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
    
# Initialize MySQL database
def init_mysql():
    connection = pymysql.connect(host='localhost', user='root', password='awattar', db='awattar')
    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS `prices`")
            cursor.execute("""
                CREATE TABLE `prices` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `start_timestamp` BIGINT NOT NULL,
                    `end_timestamp` BIGINT NOT NULL,
                    `marketprice` FLOAT NOT NULL
                )
            """)
        connection.commit()
    finally:
        connection.close()

# Initialize InfluxDB database
def init_influxdb():
    client = InfluxDBClient(host='localhost', port=8086, username='admin', password='awattar')
    client.drop_database('awattardb')
    client.create_database('awattardb')
    client.switch_database('awattardb')

# Save data to MySQL
def save_to_mysql(data):
    connection = pymysql.connect(host='localhost', user='root', password='awattar', db='awattar')
    try:
        with connection.cursor() as cursor:
            for entry in data['data']:
                sql = "INSERT INTO `prices` (`start_timestamp`, `end_timestamp`, `marketprice`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (entry['start_timestamp'], entry['end_timestamp'], entry['marketprice']))
        connection.commit()
    finally:
        connection.close()

# Save data to InfluxDB
def save_to_influxdb(data):
    client = InfluxDBClient(host='localhost', port=8086, username='admin', password='awattar')
    client.switch_database('awattardb')
    points = []
    for entry in data['data']:
        point = {
            "measurement": "prices",
            "tags": {
                "unit": entry['unit'],
            },
            "time": datetime.utcfromtimestamp(entry['start_timestamp'] / 1000.0).isoformat(),
            "fields": {
                "marketprice": float(entry['marketprice'])  # This ensures the price is a float
            }
        }
        points.append(point)
    client.write_points(points)

# Define constants
API_URL = 'https://api.awattar.at/v1/marketdata'
START_DATE = datetime.now() - timedelta(days=365 * 5)  # last 5 years
END_DATE = datetime.now()

# Initialize databases
init_mysql()
init_influxdb()

# Fetch data
data = fetch_data(START_DATE, END_DATE, API_URL)
if data:
    save_to_mysql(data)
    save_to_influxdb(data)