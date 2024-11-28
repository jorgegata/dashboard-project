# Project DASHBOARD

The repository contains the code necessary to load, clean, transform, and display various metrics related to the VBZ transport system of Zürich

## Structure of the repository
* data/zip_files: contains the raw data obtained from the Open Government Data (OGD) at the Open Data Portal (https://data.stadt-zuerich.ch/dataset/vbz_fahrgastzahlen_ogd)
* documentation: contains information about metadata, tables and data scheme used by VBZ to gather the data
* streamlit_app: contains the files needed to display the dashboard, implemented in the streamlit python package.
    - streamlit_app/data: temporal folder to store intermediate data
    - output: processed csv files to check the output of the transformation, as well as to export the processed data
    - pages: python files containing the logic and layout of multiple pages in the dashboard
    - utils: python files containing functions, constants, and other objects to implement the dashboard
    - requirements: .txt file containing the dependencies needed
    - main.py: python file containing the main page of the dashboard  


