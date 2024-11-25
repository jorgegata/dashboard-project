import streamlit as st
import pandas as pd
import os
import utils.global_values as global_values

CARBON_INTENSITY_TRANSPORT_VBZ = global_values.CARBON_INTENSITY_TRANSPORT_VBZ

@st.cache_data
def load_and_merge_data(year):
    folder = f'{os.getcwd()}/data/{year}'
    
    # Load tables
    REISENDE = pd.read_csv(f'{folder}/REISENDE.csv', sep=";").drop(["ID_Abschnitt", "Tagtyp_Id", "Anzahl_Messungen"], axis=1)
    LINIE = pd.read_csv(f'{folder}/LINIE.csv', sep=";")
    HALTESTELLEN = pd.read_csv(f'{folder}/HALTESTELLEN.csv', sep=";")
    GEFAESSGROESSE = pd.read_csv(f'{folder}/GEFAESSGROESSE.csv', sep=";")

    # Merge tables
    merged_df = pd.merge(REISENDE, LINIE, how="left", on=["Linien_Id", "Linienname"]).drop("Linienname", axis=1)
    merged_df = pd.merge(merged_df, HALTESTELLEN, how="left", on="Haltestellen_Id").drop(["Haltestellennummer", "Haltestellenkurzname"], axis=1)
    merged_df = pd.merge(merged_df, CARBON_INTENSITY_TRANSPORT_VBZ, how="left", left_on="VSYS", right_index=True)
    final_df = pd.merge(merged_df, GEFAESSGROESSE, how="left", on="Plan_Fahrt_Id").drop(["Linien_Id", "Plan_Fahrt_Id"], axis=1)

    # Add year column
    final_df["year"] = year

    # Map the next_stop variable to the actual name of the stops
    next_stop_mapped = pd.merge(REISENDE, HALTESTELLEN, how="left", left_on="Nach_Hst_Id", right_on="Haltestellen_Id")["Haltestellenlangname"]
    final_df["stop_next"] = next_stop_mapped

    return final_df



