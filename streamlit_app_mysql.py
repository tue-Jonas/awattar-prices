import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pymysql
import time

# Establish a connection to the database
def connect_to_mysql():
    start_time = time.time()
    conn = pymysql.connect(
        host='localhost', 
        user='root', 
        password='awattar', 
        db='awattar', 
        cursorclass=pymysql.cursors.DictCursor
    )
    end_time = time.time()
    print(f"Time taken to connect to MySQL Database: {end_time - start_time} seconds")
    return conn

# Load data from MySQL database
@st.cache_data
def load_data_from_mysql():
    start_time = time.time()
    conn = connect_to_mysql()
    try:
        with conn.cursor() as cursor:
            # Adjust the SQL query if your table has different column names
            sql = "SELECT start_timestamp, end_timestamp, marketprice FROM prices;"
            cursor.execute(sql)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            # Convert timestamps from milliseconds to seconds
            df['start_datetime'] = pd.to_datetime(df['start_timestamp'] / 1000, unit='s')
            df['end_datetime'] = pd.to_datetime(df['end_timestamp'] / 1000, unit='s')
    finally:
        conn.close()
    end_time = time.time()
    print(f"Time taken to load data from MySQL: {end_time - start_time} seconds")
    return df

# Fetch data
data = load_data_from_mysql()

# Streamlit app layout
st.title('aWATTar Electricity Price Visualization')

# Display the raw data if the user wants to see it
if st.checkbox('Show raw data'):
    st.write(data[['start_datetime', 'marketprice']])  # Removed 'unit' column

# Interactive Streamlit line chart
st.line_chart(data.set_index('start_datetime')['marketprice'], use_container_width=True)

# Data visualization using Matplotlib
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data['start_datetime'], data['marketprice'], marker='o', linestyle='-')

# Set the x-axis major locator and formatter to display just the year
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45)

# Setting the labels and title
ax.set_xlabel('Year')
ax.set_ylabel('Market Price (€/MWh)')
ax.set_title('Market Price Over Time')

st.pyplot(fig)
