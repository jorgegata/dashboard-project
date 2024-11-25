import streamlit as st
import pandas as pd
import io
import os 
import numpy
import utils.functions as functions
import utils.global_values as global_values

OUTPUT_PATH = os.path.join(os.getcwd(), "output")
CARBON_INTENSITY_VBZ = global_values.CARBON_INTENSITY_TRANSPORT_VBZ
CARBON_INTENSITY_VEHICLE_FLEET = global_values.CARBON_INTENSITY_VEHICLE_FLEET
TOTAL_WORKING_DAYS_FACTOR = 251
TOTAL_SATURDAYS_FACTOR = 52
TOTAL_SUNDAYS_FACTOR = 62

@st.cache_data
def calculate_metrics(data):

    # Adding needed metrics
    data["passenger_line_year"] = data["passenger_in"] * data["factor_average"]
    data["occupancy_rate_0"] = data["passenger_amount"] / data["seat_capacity"]
    data["passenger_amount_WD"] = data["passenger_amount"] * data["factor_workingDays"] / TOTAL_WORKING_DAYS_FACTOR
    data["passenger_amount_NWD"] = ((data["passenger_amount"] * data["factor_saturday"] / TOTAL_SATURDAYS_FACTOR) +
                                    (data["passenger_amount"] * data["factor_sunday"] / TOTAL_SUNDAYS_FACTOR))
    data["passenger_amount_night"] = ((data["passenger_amount"] * data["factor_saturday_night"] / TOTAL_SATURDAYS_FACTOR) + 
                                    (data["passenger_amount"] * data["factor_sunday_night"]) / TOTAL_SUNDAYS_FACTOR)
    data["passenger_amount_night_saturday"] = data["passenger_amount"] * data["factor_saturday_night"] / TOTAL_SATURDAYS_FACTOR
    data["passenger_amount_night_sunday"] = data["passenger_amount"] * data["factor_sunday_night"] / TOTAL_SUNDAYS_FACTOR
    data["passenger_kilometre"] = data["passenger_amount"] * data["distance"] * data["factor_average"]
    data["passenger_kilometre_co2"] = data["passenger_kilometre"] * data["carbon_intensity"]

    ######### PASSENGER FRAMES ########

    # Calculation of auxiliary series
    distance_total = data.pivot_table(index="year", values="distance", aggfunc="sum")
    passenger_total = data.pivot_table(index="year", values="passenger_amount", aggfunc="sum")
    pkm_total = data.pivot_table(index="year", values="passenger_kilometre", aggfunc="sum")

    # Number of passengers (dim: line and year)
    number_passengers = (data.pivot_table(index="year",
                                          columns="line_name",
                                          values="passenger_line_year",
                                          aggfunc="sum")
    )

    # Occupancy (dim: type of day, year and time instant)
    occupancy_trend = data.pivot_table(index="departure_time",
                                    columns="year",
                                    values=["passenger_amount_WD", "passenger_amount_NWD","passenger_amount_night"],
                                    aggfunc="sum")

    occupancy_trend = (functions.aggregate_time_step(occupancy_trend)
                                .rename({"passenger_amount_NWD": "Non-working days",
                                        "passenger_amount_WD": "Working days",
                                        "passenger_amount_night": "Non-working nights"},
                                        axis=1))

    # Number of passengers during night (dim: year, time, vehicle class) 
    passengers_night = data.pivot_table(index="departure_time",
                                        columns="year",
                                        values="passenger_amount_night",
                                        aggfunc="sum")
    passengers_night = functions.aggregate_time_step(passengers_night)

    # Vehicle class use (dim: time of day, vehicle class, type of day, year)Passenger metrics: Type of vehicle used per time
    vehicle_use = data.pivot_table(index="departure_time",
                                columns=["year", "type_transport"],
                                values=["passenger_amount_WD",
                                        "passenger_amount_NWD",
                                        "passenger_amount_night",
                                        "passenger_amount_night_saturday",
                                        "passenger_amount_night_sunday"],
                                aggfunc="sum")
    vehicle_use = functions.aggregate_time_step(vehicle_use)

    # Passenger-kilometer (dim: vehicle class, year, time of day)
    pkm_amount = data.pivot_table(index=["departure_time"],
                                            columns=["year","type_transport"],
                                            values="passenger_kilometre",
                                            aggfunc="sum")
    pkm_amount = functions.aggregate_time_step(pkm_amount)
    pkm_amount = pkm_amount.stack(future_stack=True).stack(future_stack=True).reset_index().rename({"level_0":"time","type_transport":"vehicle_class",
                                                                  0:"pkm"}, axis=1)

    # Number of lines (dim: year, vehicle class, line name)
    number_lines = (data.groupby(["year", "type_transport"])[["line_name"]]
                        .nunique()
                        .unstack())
    number_lines.columns = number_lines.columns.droplevel(0)

    # Capacity factor of vehicle class (dim: time day, vehicle class, year)
    capacity_factor = data.pivot_table(index="departure_time",
                                        columns=["year", "type_transport"],
                                        values="occupancy_rate_0").fillna(0)

    ######### DISTANCE AND TIME METRICS #########

    # Distance travelled per vehicle and year
    distance_travelled = (data.pivot_table(index="year",
                                           columns="type_transport",
                                           values="distance",
                                           aggfunc="sum")
                            .unstack()
                            .reset_index()
                            .rename({"type_transport":"vehicle_class",
                                     0:"distance"}, axis=1))

    # Emisssions saved by public transport fleet against representative vehicle fleet (dim: year)
    pkm_co2_public_transport =  data.pivot_table(index="year",
                                                columns="type_transport",
                                                values="passenger_kilometre_co2",
                                                aggfunc="sum")
    pkm_co2_car = pkm_total * CARBON_INTENSITY_VEHICLE_FLEET
    saved_co2 = pkm_co2_car.sub(pkm_co2_public_transport.sum(axis=1), axis="rows") / 1000 # Translate to tons CO2-eq

    all_df = {"number_passengers": number_passengers,
              "occupancy_tren": occupancy_trend,
              "passenger_day" :passengers_night,
              "vehicle_use": vehicle_use,
              "pkm_amount": pkm_amount,
              "number_lines": number_lines,
              "capacity_factor": capacity_factor,
              "distance_travelled": distance_travelled,
              "saved_co2": saved_co2}

    return all_df