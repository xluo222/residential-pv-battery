import os
import requests
import pandas as pd

# refer to https://developer.nlr.gov/docs/solar/pvwatts/v8/ for more information on API requests and their parameters

PVWATTS_URL = "https://developer.nlr.gov/api/pvwatts/v8.json"

# download one typical year of hourly PV generation from PVWatts V8
def get_hourly_solar_generation(latitude: float, longitude: float, pv_capacity_kw: float = 6.0, tilt: float = 25.0, azimuth: float = 180.0):

    # set API
    api_key = os.getenv("NREL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NREL_API_KEY is not set. Set it in your terminal first."
        )

    # parameters for the API request
    params = {
        "api_key": api_key,
        "lat": latitude,
        "lon": longitude,

        # PV system assumptions 
        "system_capacity": pv_capacity_kw,
        "tilt": tilt,
        "azimuth": azimuth,
        "array_type": 1,  # fixed roof mount
        "module_type": 0,  # standard module
        "losses": 14.0, # default assumption in PVWatts calculator is 14%

        # inverter/system assumptions
        "dc_ac_ratio": 1.2,
        "inv_eff": 95.0, # read https://www.sciencedirect.com/topics/engineering/inverter-efficiency for more information on inverter efficiency
        "gcr": 0.4,

        # Request hourly output
        "timeframe": "hourly",
        "dataset": "nsrdb",
        "radius": 100   # PVWatts searches within 100 miles
    }

    # sends the request 
    response = requests.get(
        PVWATTS_URL,
        params=params,
        timeout=60
    )

    print(response.raise_for_status()) # 200 if connection works, 4xx or 5xx if not
    data = response.json()
    
    ac_watts = data["outputs"]["ac"]

    if len(ac_watts) != 8760:
        raise ValueError(
            f"Expected 8,760 hourly values, received {len(ac_watts)}."
        )

    # creates a dataframe with the list of hourly values
    solar = pd.DataFrame({
        "solar_ac_w": ac_watts
    })

    # each value is average AC power over a one-hour interval.
    # W ÷ 1000 = kW, and kW × 1 hour = kWh.
    solar["solar_kwh"] = solar["solar_ac_w"] / 1000

    return solar

solar = get_hourly_solar_generation(
    latitude=32.87,
    longitude=-117.14,
    pv_capacity_kw=6.0
)

print(solar)
