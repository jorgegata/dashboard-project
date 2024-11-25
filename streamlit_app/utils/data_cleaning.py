import pandas as pd
import streamlit as st

def safe_decode(string):
    # Function to handle possible string errors as the Umlauts are not properly displayed
    try: 
        decoded_string = string.encode('latin1').decode('utf-8')
        return decoded_string
    
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError): # If there is any error encoding, it is already ok
        return string

def adjust_invalid_times(time_str):
    # Function to handle possible time errors as data include hours above 24h format
    hour = int(time_str[:2])
    if hour >= 24:
        return str(hour - 24) + time_str[2:]
    return time_str

@st.cache_data
def clean_data(data):
    # Decode strings
    data["stop_next"] = data["stop_next"].map(safe_decode)
    data["stop_current"] = data["stop_current"].map(safe_decode)

    # Map transport types
    data["departure_time"] = data["departure_time"].map(adjust_invalid_times)
    data["departure_time"] = pd.to_datetime(data["departure_time"], format="%H:%M:%S").dt.time

    # Convert distance to km
    data["distance"] = data["distance"] / 1000

    # Remove duplicated and return the data
    return data.drop_duplicates()