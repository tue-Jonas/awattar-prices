import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from datetime import datetime

# Load the data
@st.cache_data
def load_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)['data']
    df = pd.DataFrame(data)
    df['start_datetime'] = pd.to_datetime(df['start_timestamp'], unit='ms')
    df['marketprice'] = pd.to_numeric(df['marketprice'], errors='coerce')
    return df

data = load_data('awattar_data.json')

# Streamlit app layout
st.title('aWATTar Electricity Price Visualization')

# Display the raw data if the user wants to see it
if st.checkbox('Show raw data'):
    st.write(data[['start_datetime', 'marketprice', 'unit']])

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
