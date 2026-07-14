import requests
import time
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt

# opens file and creates a GeoDataFrame. Stores the outline of each state
states = gpd.read_file(
    "cb_2025_us_all_500k/cb_2025_us_state_500k.shp"
)

# prints geographical locations of the state boundaries and the shape of each state
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

# returns the solar resource for the point (using latitude and longitude)
def get_solar_resource(lat, lon):
    url = "https://developer.nlr.gov/api/solar/solar_resource/v1.json"

    # creates dictionary to store point
    parameters = {
        "api_key": API_KEY,
        "lat": lat,
        "lon": lon
    }

    # request to the NLR server for the solar resource at said location
    response = requests.get(
        url,
        params=parameters,
        timeout=15 # if server doesn't respond within 15 seconds, timeout exception
    )

    return response.json()

results = []

# loops through every coordinate
for _, row in points_df.iterrows():

    data = get_solar_resource(
        row["latitude"],
        row["longitude"]
    )
    
    if "outputs" not in data:
        print("API failed for:",
              row["latitude"],
              row["longitude"])
        print(data)
        continue

    results.append({

        "state": row["state"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        
          # Annual Global Horizontal Irradiance (w/m^2)
        "ghi": data["outputs"]["avg_ghi"]["annual"]
    })


solar_df = pd.DataFrame(results)

print(solar_df.head())
print("Successful points:", len(solar_df))
print("Failed points:", len(points_df) - len(solar_df))

solar_df.to_csv(
    "solar_generation_points.csv",
    index=False
)   
    
# creates heat map with darker points representing locations with higher solar resources and lighter points being locations with lower solar resources

# creates a GeoDataFrame from the solar 
solar_gdf = gpd.GeoDataFrame(
    solar_df,
    geometry=gpd.points_from_xy(
        solar_df.longitude,
        solar_df.latitude
    ),
    crs="EPSG:4326"
)

# create figure and axes
fig, ax = plt.subplots(figsize=(10,10))

# plot state boundaries
states.boundary.plot(
    ax=ax,
    color="black",
    linewidth=1
)

# plot solar resource points 
solar_gdf.plot(
    ax=ax,
    column="ghi",
    cmap="YlOrRd",
    legend=True,
    markersize=20,
    legend_kwds={
        "shrink": 0.5
    }
)

plt.title(
    "Annual Average Daily Global Horizontal Irradiance (kWh/m^2/day)\n"
    "Washington, California, Nevada, and Massachusetts"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.savefig(
    "solar_map.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# takes around two-three minutes to generate the solar resources at all cordinates and convert them into a heat map.
