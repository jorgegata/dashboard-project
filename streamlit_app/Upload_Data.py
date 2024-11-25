import streamlit as st
import pandas as pd
import zipfile
import io
import os
import utils.functions as functions_app
import utils.data_loading as data_loading
import utils.data_cleaning as data_cleaning
import utils.metrics as metrics
import utils.global_values as global_values

EXTRACT_OUTPUT_DIRECTORY = "./data/"

st.set_page_config(
    page_title="Dashboard application",
    page_icon=":bar_chart:",
    layout="wide"

)

st.title("Pilot Project - v0.1")

# Initialization of session state variables
if "final_data" not in st.session_state:
    st.session_state.final_data = None
    st.session_state.metrics = None

@st.cache_data
def process_uploaded_files(uploaded_files):
    dataframes = []
    years = []
    for uploaded_file in uploaded_files:
        year_file = functions_app.obtain_year_zipfile(uploaded_file.name)
        years.append(year_file)
        extraction_directory = os.path.join(EXTRACT_OUTPUT_DIRECTORY, str(year_file))
        os.makedirs(extraction_directory, exist_ok=True)
        csv_files = functions_app.extract_csv_files(uploaded_file, extraction_directory)

        if csv_files:
            st.success(f"Extracted {len(csv_files)} CSV files to: {extraction_directory}")
        else:
            st.warning(f"No CSV files found in {uploaded_file.name}")
        dataframes.append(data_loading.load_and_merge_data(year_file))
    return pd.concat(dataframes, ignore_index=True), years

@st.cache_data
def clean_data(raw_data):
    raw_data = raw_data.rename(global_values.MAPPING_ATTRIBUTES, axis=1)
    return data_cleaning.clean_data(raw_data)

@st.cache_data
def compute_metrics(cleaned_data):
    return metrics.calculate_metrics(cleaned_data)

st.markdown(f"Option 1: Process the data")
uploaded_files = st.file_uploader(
    "Upload ZIP file(s) containing the datasets",
    type="zip",
    accept_multiple_files=True
)

st.markdown(f"<br>Option 2: Upload the processed data", unsafe_allow_html=True)
csv_uploaded_file = st.file_uploader(
    label="Upload the CSV file with the datasets processed",
    type="csv"
)

# Handle Option 1: Process raw data
if uploaded_files:
    with st.spinner("Processing uploaded files..."):
        raw_data, years = process_uploaded_files(uploaded_files)
        st.session_state.final_data = clean_data(raw_data)
        st.session_state.csv_path = os.path.join(os.getcwd(), "output", f"processed_data_{years[0]}-{years[-1]}.csv")
        st.session_state.final_data.to_csv(st.session_state.csv_path)
        st.download_button(
            label=f"Download CSV",
            data=st.session_state.final_data.to_csv(index=False),
            file_name=f"processed_data_{years[0]}-{years[-1]}.csv",
            mime="text/csv"
    )

# Handle Option 2: Read processed data
if csv_uploaded_file:
    st.write("")
    st.write("")
    with st.spinner("Loading CSV file..."):
        st.session_state.final_data = pd.read_csv(csv_uploaded_file)
        st.success(f"The CSV file was succesfully loaded")

# Generate metrics and display results if data is available
if st.session_state.final_data is not None:
    st.markdown("<br><br>Calculating metrics...", unsafe_allow_html=True)
    st.session_state.metrics = metrics.calculate_metrics(data=st.session_state.final_data)
    if st.session_state.metrics is not None:
        st.success("Metrics are ready! Navigate to the Dashboard Display to see the trends")
    else:
        st.warning("Error on the calculation of the metrics")