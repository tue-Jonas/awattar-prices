import requests
import json
import time
from datetime import datetime, timedelta
import pymysql
from influxdb import InfluxDBClient

# fetch from awattar api
def fetch_data(start_date, end_date, api_url):
    start_time = time.time()
    params = {
        'start': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end': end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    response = requests.get(api_url, params=params)
    end_time = time.time()
    print(f"Time taken to fetch data: {end_time - start_time} seconds")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: HTTP Code {response.status_code}")
        return None

# Initialize MySQL database
def init_mysql():
    start_time = time.time()
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
    end_time = time.time()
    print(f"Time taken to initialize MySQL: {end_time - start_time} seconds")

# Initialize InfluxDB database
def init_influxdb():
    start_time = time.time()
    client = InfluxDBClient(host='localhost', port=8086, username='admin', password='awattar')
    client.drop_database('awattardb')
    client.create_database('awattardb')
    client.switch_database('awattardb')
    end_time = time.time()
    print(f"Time taken to initialize InfluxDB: {end_time - start_time} seconds")

# Save data to MySQL
def save_to_mysql(data):
    start_time = time.time()
    connection = pymysql.connect(host='localhost', user='root', password='awattar', db='awattar')
    try:
        with connection.cursor() as cursor:
            for entry in data['data']:
                sql = "INSERT INTO `prices` (`start_timestamp`, `end_timestamp`, `marketprice`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (entry['start_timestamp'], entry['end_timestamp'], entry['marketprice']))
        connection.commit()
    finally:
        connection.close()
    end_time = time.time()
    print(f"Time taken to save data to MySQL: {end_time - start_time} seconds")

# Save data to InfluxDB
def save_to_influxdb(data):
    start_time = time.time()
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
    end_time = time.time()
    print(f"Time taken to save data to InfluxDB: {end_time - start_time} seconds")

# Define constants
API_URL = 'https://api.awattar.at/v1/marketdata'
START_DATE = datetime.now() - timedelta(days=365 * 5)  # last 5 years
END_DATE = datetime.now()

# Initialize databases
init_mysql()
init_influxdb()

# Fetch and save data
data = fetch_data(START_DATE, END_DATE, API_URL)
if data is not None:
    save_to_mysql(data)
    save_to_influxdb(data)