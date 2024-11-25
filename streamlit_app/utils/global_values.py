import pandas as pd


"""
SOURCES OF INFORMATION:

Cable cars: Urban cable cars: Modern cable car systems open up new options for mobility in our cities” by Heiner Monheim et al. (2010, ksv-verlag)
Rest of type of vehicles: Data source: UK Government, Department for Energy Security and Net Zero (2022)
Funicular: https://oitaf2024.com/wp-content/uploads/2024/07/The-transport-capacity-of-a-cable-car-system-in-public-transportation_DEF-1.pdf

"""

MAPPING_ATTRIBUTES = {"Richtung": "direction",
                      "Sequenz": "sequence",
                      "FZ_AB": "departure_time",
                      "Einsteiger": "passenger_in",
                      "Aussteiger": "passenger_out",
                      "Besetzung": "passenger_amount",
                      "Distanz": "distance",
                      "Tage_DTV": "factor_average",
                      "Tage_DWV": "factor_workingDays",
                      "Tage_SA": "factor_saturday",
                      "Tage_SO": "factor_sunday",
                      "Nachtnetz": "night_flag",
                      "Tage_SA_N": "factor_saturday_night",
                      "Tage_SO_N": "factor_sunday_night",
                      "VSYS": "type_transport",
                      "Linienname_Fahrgastauskunft": "line_name",
                      "SITZPLAETZE": "seat_capacity",
                      "KAP_1m2": "passenger_capacity_1",
                      "KAP_2m2": "passenger_capacity_2",
                      "KAP_3m2": "passenger_capacity_3",
                      "KAP_4m2": "passenger_capacity_4",
                      "Haltestellenlangname": "stop_current"}

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

CARBON_INTENSITY_TRANSPORT_VBZ = pd.Series({
                                        "Bus G": 0.097,
                                        "Bus L": 0.097,
                                        "Bus P": 0.097,
                                        "Bus Urban": 0.097,
                                        "Bus Z": 0.097,
                                        "Cable car": 0.044,
                                        "Funicular": 0.0245,
                                        "Night bus": 0.097,
                                        "Tram": 0.029,
                                        "Trolley Bus": 0.097*0.5+0.047*0.5}
                                        ).to_frame().rename({0:"carbon_intensity"}, axis=1).rename({value: key for key, value in VEHICLE_CLASS.items()},axis=0)

# Fleet of 35% diesel, 35% petrol, 20% electric, 10% motorbikes respectively
CARBON_INTENSITY_VEHICLE_FLEET = 0.171*0.35 + 0.170*0.35 + 0.047*0.2 + 0.114*0.1
