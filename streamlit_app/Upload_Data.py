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

# Constants
EXTRACT_OUTPUT_DIRECTORY = "./data/"

# Set page configuration
st.set_page_config(page_title="Dashboard application",page_icon=":bar_chart:",layout="wide")
st.title("Pilot Project - v0.2")

if "final_data" not in st.session_state:
    st.session_state.final_data = None
if "years" not in st.session_state:
    st.session_state.years = None
if "uploaded_files_processed" not in st.session_state:
    st.session_state.uploaded_files_processed = False
if "csv_uploaded_processed" not in st.session_state:
    st.session_state.csv_uploaded_processed = False

@st.cache_data
def process_uploaded_files(uploaded_files):
    dataframes, years = [], []
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

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def obtain_year_period(csv_path):
        years = csv_path.split("_")[-1].split(".")[0].split("-")
        return years

st.markdown(f"Option 1: Upload ZIP files containing raw datasets")
uploaded_files = st.file_uploader("Upload ZIP file(s)", type="zip", accept_multiple_files=True)

st.markdown(f"<br>Option 2: Upload the processed data", unsafe_allow_html=True)
processed_csv_uploaded = st.file_uploader(label="Upload processed CSV file",type="csv")

# Handle Option 1: Process raw data
if uploaded_files and not st.session_state.uploaded_files_processed:
    try:
        raw_data, st.session_state.years = process_uploaded_files(uploaded_files)
        st.session_state.final_data = clean_data(raw_data)
        csv_path = os.path.join(os.getcwd(), "output", f"processed_data_{st.session_state.years[0]}-{st.session_state.years[-1]}.csv")
        st.session_state.final_data.to_csv(csv_path, index=False)
        st.download_button(
            label=f"Download CSV",
            data=st.session_state.final_data.to_csv(),
            file_name=f"processed_data_{st.session_state.years[0]}-{st.session_state.years[-1]}.csv",
            mime="text/csv"
    )
        st.session_state.uploaded_files_processed = True
    except Exception as e:
        st.error(f"An error occured while processing files: {e}")

if processed_csv_uploaded and not st.session_state.csv_uploaded_processed:
    try:
        st.session_state.years = obtain_year_period(processed_csv_uploaded.name)
        st.session_state.final_data = load_csv(processed_csv_uploaded)
        st.success("Processed CSV file loaded succesfully")
        st.session_state.csv_uploaded_processed = True
    except Exception as e:
        st.error(f"An error ocurred while loading the file: {e}")

# Calculate metrics if data is available
if st.session_state.final_data is not None:
    st.write("")
    st.write(f"Time period loaded: {st.session_state.years[0]} - {st.session_state.years[-1]}")
    st.write(st.session_state.final_data.head(5))
    with st.spinner("Calculating metrics..."):
        try:
            st.session_state.metrics = compute_metrics(st.session_state.final_data)
            st.success("Metrics calculated succesfully! Navigate to the Dashboard Display")
        except Exception as e:
            st.error(f"An error ocurred while calculating metrics: {e}")

if st.session_state.uploaded_files_processed or st.session_state.csv_uploaded_processed:
    st.session_state.uploaded_files_processed = False
    st.session_state.csv_uploaded_processed = False