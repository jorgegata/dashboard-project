import pandas as pd
import streamlit as st
import zipfile
import io

def obtain_year_zipfile(string):
    start_index = string.find("20")
    end_index = start_index + 4
    return string[start_index:end_index]

def extract_csv_files(zip_file, output_directory):  
    csv_files = []

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]

        for csv_file in csv_files:
            zip_ref.extract(csv_file, output_directory)
            
    return csv_files

def aggregate_time_step(df, amount="5min"):

    df.index = pd.to_datetime(df.index, format="%H:%M:%S")
    if amount != " ":
        df = df.resample(amount).mean()
    df.index = df.index.time

    return df
