import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import utils.visualizations as visualizations

VEHICLE_CLASS = {'TR': "Trolley Bus",
                 'T': "Tram",
                 'B': "Bus Urban",
                 'BP': "Bus P",
                 'BL': "Bus L",
                 'BZ': "Bus Z",
                 'FB': "Funicular",
                 'N': "Night Bus",
                 'BG': "Bus G",
                 'SB': "Cable car"}

# Definition of functions

# Configuration of page
st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

def pkm_metric(df):
    pkm = df.groupby("year")["pkm"].sum()
    value_actual = pkm.iloc[-1]
    value_previous = pkm.iloc[-2]
    absolute_increase = value_actual - value_previous
    percentage_increase = (absolute_increase / value_previous) * 100
    st.metric(
        label=f"Passenger-kilometre in {pkm.index[-1]}",
        value= f"{value_actual:,.0f} pkm",
        delta=f"{absolute_increase:,.1f} ({percentage_increase:,.1f} %)"
    )

def distance_metric(df):
    distance = df.groupby("year")["distance"].sum()
    value_actual = distance.iloc[-1]
    value_previous = distance.iloc[-2]
    absolute_increase = value_actual - value_previous
    percentage_increase = (absolute_increase / value_previous) * 100
    st.metric(
        label=f"Distance Travelled in {distance.index[-1]}",
        value=f"{value_actual:,.0f} km",
        delta=f"{absolute_increase:,.1f} ({percentage_increase:,.1f} %)"
    )

def co2_metric(df):
    value_actual = df.iloc[-1][0]
    value_previous = df.iloc[-2][0]
    absolute_increase = value_actual - value_previous
    percentage_increase = (absolute_increase / value_previous) * 100
    st.metric(
        label=f"CO2 emissions avoided {df.index[-1]}",
        value=f"{value_actual:,.0f} tons CO2",
        delta=f"{absolute_increase:,.1f} ({percentage_increase:,.1f} %)"
    )

def breakdown_lines_metric(df):
    df = df.stack().reset_index().rename({0:"passenger_in"}, axis=1)

    selected_years = st.multiselect("Select Years to Display", options=df["year"].unique(), default=df["year"].unique())
    top_n = st.slider("Select Number of Top Lines", min_value=2, max_value=10, value=3)

    df = df[df["year"].isin(selected_years)]
    top_lines = df.groupby(["line_name"])["passenger_in"].sum().nlargest(top_n).index
    df = df[df["line_name"].isin(top_lines)]

    fig = go.Figure()
    for line in df["line_name"].unique():
        line_data = df[df["line_name"] == line]
        fig.add_trace(go.Bar(
            y=line_data["year"],
            x=line_data["passenger_in"],
            name=line,
            orientation="h"
        ))
        fig.update_layout(
            barmode="group",
            title="Flow of Passengers Entering by Line and Year",
            xaxis_title="Passengers In",
            yaxis_title="Year",
            legend_title="Line",
            height=400,
        )
    return fig

def number_lines_metric(df):
    df = df.stack().reset_index().rename({0:"number_lines"}, axis=1)
    df["type_transport"] = df["type_transport"].map(VEHICLE_CLASS)
    selected_year = st.selectbox("Select Year", options=df["year"].unique())
    df = df[df["year"] == selected_year]

    fig = px.bar(
        df,
        x="type_transport",
        y="number_lines",
        color="type_transport",
        height=500
    )
    fig.update_layout(
        xaxis_title="Vehicle Type",
        yaxis_title="Number of Lines",
        showlegend=False,
    )
    return fig

def change_lines_metric(df):
    filter_years = st.multiselect("Select year", options=df.index[1:], default=df.index[1:])
    df = df.apply(lambda x: x - x.iloc[0]).loc[filter_years]
    df.columns = df.columns.map(VEHICLE_CLASS)

    fig = go.Figure()

    for type_transport in df.columns:
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df[type_transport],
                name=type_transport,
            )
        )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of lines added",
        height=500,
    )
    return fig

def donought_km_travelled(df):
    unique_years = df["year"].unique()
    df = df.pivot_table(index="year", columns="vehicle_class", values="pkm", aggfunc="sum")
    filtered_year = st.selectbox("Select year",options=unique_years)
    df = df.loc[filtered_year]
    label_years = df.index
    values = df.values

    fig = go.Figure(
        data=[
            go.Pie(
                labels=label_years,
                values=values,
                hole=0.4,
                textinfo="label+percent",
                texttemplate="%{label}: %{percent:.1%}"
            )
        ]
    )
    fig.update_layout(
        title=f"Vehicle class shares for {filtered_year}",
        annotations=[{'text':f'{filtered_year}', 'x':0.5, 'y':0.5, 'font_size':20, 'showarrow':False}]
    )
    return fig


# Logic
if "metrics" not in st.session_state or st.session_state.metrics is None:
    st.warning("Metrics are not available. Please, calculate them on the main page")
else:
    st.title("Dashboard")
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pkm_metric(st.session_state.metrics["pkm_amount"])
    with col2:
        distance_metric(st.session_state.metrics["distance_travelled"])
    with col3:
        co2_metric(st.session_state.metrics["saved_co2"])

    st.markdown("<br><br> <h1 style='font-size:26px'>Flow of Passengers Entering by Line and Year</h1>", unsafe_allow_html=True)
    fig = breakdown_lines_metric(st.session_state.metrics["number_passengers"])
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, = st.columns(2)
    with col1:
        st.markdown("<h1 style='font-size:26px'>Number of Lines per Vehicle </h1>", unsafe_allow_html=True)
        st.plotly_chart(number_lines_metric(st.session_state.metrics["number_lines"]))
    with col2:
        st.markdown(f"<h1 style='font-size:26px'>Lines added relative to {st.session_state.metrics["number_lines"].index[0]}", unsafe_allow_html=True)
        st.write(change_lines_metric(st.session_state.metrics["number_lines"]))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h1 style='font-size:26px'>Number of km per vehicle </h1>", unsafe_allow_html=True)
        fig = donought_km_travelled(df=st.session_state.metrics["pkm_amount"])
        st.plotly_chart(fig)

    with col2:
        st.markdown("<h1 style='font-size:26px'>Distribution of pkm", unsafe_allow_html=True)

