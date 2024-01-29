import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from influxdb import DataFrameClient

# InfluxDB connection parameters
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USERNAME = 'admin'
INFLUXDB_PASSWORD = 'awattar'
INFLUXDB_DBNAME = 'awattardb'

# Establish a connection to the InfluxDB database
def connect_to_influxdb():
    return DataFrameClient(
        host=INFLUXDB_HOST, 
        port=INFLUXDB_PORT, 
        username=INFLUXDB_USERNAME, 
        password=INFLUXDB_PASSWORD, 
        database=INFLUXDB_DBNAME
    )

# Load data from InfluxDB database
@st.cache_data
def load_data_from_influxdb():
    client = connect_to_influxdb()
    # Query the measurement (table) where your data is stored
    query = 'SELECT * FROM "prices"'
    data = client.query(query)
    df = data['prices']  # The measurement name is the key in the returned dict
    df.index = pd.to_datetime(df.index)  # Convert the index to datetime
    return df

# Fetch data
data = load_data_from_influxdb()

# Streamlit app layout
st.title('aWATTar Electricity Price Visualization')

# Display the raw data if the user wants to see it
if st.checkbox('Show raw data'):
    st.write(data)

# Interactive Streamlit line chart
# Assuming the DataFrame index is the datetime
st.line_chart(data[['marketprice']], use_container_width=True)

# Data visualization using Matplotlib
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data.index, data['marketprice'], marker='o', linestyle='-')

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
