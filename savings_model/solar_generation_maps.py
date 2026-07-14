import requests
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt

# opens file and creates a GeoDataFrame. Stores the outline of each state
states = gpd.read_file(
    "cb_2025_us_all_500k/cb_2025_us_state_500k.shp"
)

print(states.head())

# four chosen states for our case study
target_states = {
    "CA",
    "NV",
    "WA",
    "MA"
}

# filters through the postal (USPS) abbreviations of states so states only contains the target states
states = states[
    states["STUSPS"].isin(target_states)
]

# list of latitude and longitude points within the four states
points = []

# loops through each row of the states GeoDataFrame
for _, row in states.iterrows():
    
    # finds the smallest rectange containing the state
    minx, miny, maxx, maxy = row.geometry.bounds

    # generates longitudes every 0.5°, np.arange() creates numbers within range
    for long in np.arange(minx, maxx, 0.5):

        # generates latitudes every 0.5°, np.arange() creates numbers within range
        for lat in np.arange(miny, maxy, 0.5):
            
            point = Point(long, lat)

            # checks if points is actually within that state, and if so, adds it to the list.
            if row.geometry.contains(point):
                points.append({
                    "state": row["STUSPS"],
                    "latitude": lat,
                    "longitude": long
                })

# turns points list into a table
points_df = pd.DataFrame(points)
    
API_KEY = "HUPJuUy6lChNXWDLtQH2szASoqsjFieVX8gt9GLZ"

def get_solar_generation(lat, lon):
    url = "https://developer.nlr.gov/api/solar/solar_resource/v1.json"

    # creates dictionary to store points
    parameters = {
        "api_key": API_KEY,
        "lat": lat,
        "lon": lon
    }
    
    response = requests.get(
        url,
        params=parameters,
        timeout=15 # if server doesn't respond within 15 seconds, timeout exception
    )

    return response.json()

results = []

# loops through every coordinate
for _, row in points_df.iterrows():

    data = get_solar_generation(
        row["latitude"],
        row["longitude"]
    )

    # skip failed API requests
    if "outputs" not in data:
        print("API failed for:", row["latitude"], row["longitude"])
        continue

    results.append({

        "state": row["state"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        
          # Annual Global Horizontal Irradiance
        "ghi":
        data["outputs"]["avg_ghi"]["annual"],

        # Annual Direct Normal Irradiance
        "dni":
        data["outputs"]["avg_dni"]["annual"],

        # Annual irradiance for panels tilted at latitude
        "lat_tilt":
        data["outputs"]["avg_lat_tilt"]["annual"]

    })


solar_df = pd.DataFrame(results)

solar_df.to_csv(
    "solar_generation_points.csv",
    index=False
)   
    
# creates heat map with darker points representing locations with higher solar resources and lighter points being locations with lower solar resources
solar_gdf = gpd.GeoDataFrame(
    solar_df,
    geometry=gpd.points_from_xy(
        solar_df.longitude,
        solar_df.latitude
    ),
    crs="EPSG:4326"
)

solar_gdf.plot(
    column="ghi",
    cmap="YlOrRd",
    legend=True,
    figsize=(10,8),
    markersize=20
)

plt.title("Solar Resource Potential (GHI)")

plt.savefig(
    "solar_map.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()
