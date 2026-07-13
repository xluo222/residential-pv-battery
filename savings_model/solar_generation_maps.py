import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# opens shapefile and creates a GeoDataFrame. Stores the outline of each state
states = gpd.read_file(
    "cb_2025_us_state_500k.shp"
)

print(states.head())

# four chosen states for our case study
target_states = {
    "CA",
    "NV",
    "WA",
    "Ma"
}

# filters through the postal (UPS) abbreviations of states so states only contains the target states
states = states[
    states["STUSPS"].isin(target_states)
]

api_key = "HUPJuUy6lChNXWDLtQH2szASoqsjFieVX8gt9GLZ"

