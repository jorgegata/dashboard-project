# Project DASHBOARD

The repository contains the necessary code to load, clean, transform, and display various metrics related to the VBZ transport system of Zürich.

The datasets may be given to the tool using the data scheme modelled by the Open Government Data (OGD) at the Open Data Portal (https://data.stadt-zuerich.ch/dataset/vbz_fahrgastzahlen_ogd) as zip format. There should be one zip file per year, and each compressed file contains CSV files regarding the relational tables of the data scheme.
It automatizes the processing considering all the files passed in the first part of the application, later calculating the needed metrics and displaying them in a separate page with an interactive dashboard implemented in Streamlit

## Structure of the repository
* data/zip_files: contains the raw data obtained from the Open Government Data (OGD) at the Open Data Portal (https://data.stadt-zuerich.ch/dataset/vbz_fahrgastzahlen_ogd)
* documentation: contains the metadata of the variables, with a brief explanation of them, as well as an image file containing the data scheme. 
* streamlit_app: contains the files needed to display the dashboard, implemented in the streamlit python package.
    - streamlit_app/data: temporal folder to store intermediate data
    - output: processed csv files to check the output of the transformation, as well as to export the processed data
    - pages: python files containing the logic and layout of multiple pages in the dashboard
    - utils: python files containing functions, constants, and other objects to implement the dashboard
    - main.py: python file containing the main page of the dashboard


