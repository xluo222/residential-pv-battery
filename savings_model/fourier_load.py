import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# reads the load data from San Diego (SDGE, Southern California)
load = pd.read_csv(
    "USA_CA_San.Diego-Miramar.NAS.722930_TMY3_BASE.csv"
)

# renames the columns for later calculations
load = load.rename(columns={
    "Date/Time": "datetime",
    "Electricity:Facility [kW](Hourly)":"load_kw"
})

load["load_kwh"] = load ["load_kw"]

# cleans up the spaces in the timestamp strings
raw_datetime = (
    load["datetime"]
    .astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

date_part = pd.to_datetime(
    "2025/" + raw_datetime.str[:5], 
    format="%Y/%m/%d"
)

# extracts the hour and casts to integer
hour_part = raw_datetime.str[6:8].astype(int)

# converts text-based time and time strings into official datetime objects
load["datetime"] = date_part + pd.to_timedelta(
    hour_part,
    unit="h"
)

load["month"] = date_part.dt.month
load["hour"] = (hour_part - 1) % 24

# organize by seasons
def season(month):
    if month in [12,1,2]:
        return "winter"
    elif month in [3,4,5]:
        return "spring"
    elif month in [6,7,8]:
        return "summer"
    else:
        return "fall"

load["season"] = load["month"].apply(season)

# function for applying Fourier transform to 24-hour averages
# Fourier breaks down time-based signals into individual sine and cosine frequency components and reveals which frequencies are present, and how strong they are. Used for finding summer, winter, and annual usage patterns by smoothing out the load profile
def fourier_smooth(profile_df, harmonics): # harmonics represents how many Fourier frequency components to keep

    profile_df = profile_df.copy()
    
    # extracts all hourly load values and into NumPy array
    values = profile_df["load_kwh"].to_numpy()

    # fourier transform
    fft = np.fft.fft(values)

    # empty spectrum
    filtered = np.zeros_like(fft)

    # keep the mean load
    filtered[0] = fft[0]

    # keeps the lowest-frequency harmonics (low-frequency -> patterns in signal)
    for i in range(1, harmonics + 1):
        # remember fourier coefficients come in pairs!
        filtered[i] = fft[i]
        filtered[-i] = fft[-i]
        
    # reconstruct the smoothed signal, converts from spectrum to an hourly load signal 
    profile_df["smooth"] = np.fft.ifft(filtered).real

    return profile_df

load = fourier_smooth(load, 500)

# create summer profile (using averaged smoothed out Fourier values)
summer = (
    load.loc[load["season"] == "summer"]
    .groupby("hour", as_index=False)
    .agg({
        "load_kwh": "mean",
        "smooth": "mean"
    })
)

# create winter profile
winter = (
    load.loc[load["season"] == "winter"]
    .groupby("hour", as_index=False)
    .agg({
        "load_kwh": "mean",
        "smooth": "mean"
    })
)

# create annual profile
annual = (
    load
    .groupby("hour", as_index=False)
    .agg({
        "load_kwh": "mean",
        "smooth": "mean"
    })
)

# prints the summer, winter, and annual Fourier-smoothed profiles
print("\nSummer profile:")
print(summer)

print("\nWinter profile:")
print(winter)

print("\nAnnual profile:")
print(annual)

# read the summer and winter solar profiles from solar_generation_profiles.py. summer and winter daily solar generation profiles measured in terms of AC system output (
summer_solar = pd.read_csv("summer_solar_profile.csv")
winter_solar = pd.read_csv("winter_solar_profile.csv")

# merge the summer + winter solar PV generation profiles with the load profiles
summer_combined = summer.merge(
    summer_solar,
    on="hour",
    how="inner" # only keeps rows where the key exists in both dataframes
)

winter_combined = winter.merge(
    winter_solar,
    on="hour",
    how="inner",
)

# functions used to calculate daily costs of electricity according to the Fourier-smoothed residential load values from above
from tariffs import (
    calculate_daily_cost,
    get_summer_weekday_rate,
    get_winter_weekday_rate,
)

summer_combined= calculate_daily_cost(
    summer_combined,
    get_summer_weekday_rate
)

winter_combined = calculate_daily_cost(
    winter_combined,
    get_winter_weekday_rate
)

# while we have the annual Fourier-smoothed load profiles, there isn't a consistent time-of-use rate to apply them to, since there are variety weekday usage charge schedules depending on the time of the year.

summer_daily_cost = summer_combined["hourly_cost"].sum()
winter_daily_cost = winter_combined["hourly_cost"].sum()

# creates a summary DataFrame with the two seasons, their daily load based on Fourier-smoothed representative profiles,  their estimated daily TOU cost, and their daily solar generation (kWh)
summary = pd.DataFrame({
    "Season": ["Summer", "Winter"],
    "Daily Load (kWh)": [
        summer_combined["load_kwh"].sum(),
        winter_combined["load_kwh"].sum()
    ],
    "Daily Solar Generation (kWh)": [
        summer_combined["solar_kwh"].sum(),
        winter_combined["solar_kwh"].sum()
    ],
    "Daily Cost ($)": [
        summer_daily_cost,
        winter_daily_cost
    ]
})

print(summary)

# plot the Fourier-smoothed average profiles (commented out the averages of profiles, used originally to compare against the Fourier-smoothed values). loads as a png file. 

plt.figure(figsize=(10, 6))

#plt.plot(
    #summer["hour"],
    #summer["load_kwh"],
    #marker="o",
    #linestyle="--",
    #label="Summer average"
#)

plt.plot(
    summer["hour"],
    summer["smooth"],
    linewidth=2,
    label="Summer Fourier-smoothed"
)

#plt.plot(
    #winter["hour"],
    #winter["load_kwh"],
    #marker="o",
    #linestyle="--",
    #label="Winter average"
#)

plt.plot(
    winter["hour"],
    winter["smooth"],
    linewidth=2,
    label="Winter Fourier-smoothed"
)

#plt.plot(
    #annual["hour"],
    #annual["load_kwh"],
    #marker="o",
    #linestyle="--",
    #label="Annual average"
#)

plt.plot(
    annual["hour"],
    annual["smooth"],
    linewidth=2,
    label="Annual Fourier-smoothed"
)

plt.xlabel("Hour of day")
plt.ylabel("Average electricity use (kWh)")
plt.title("San Diego residential electricity load profiles")
plt.xticks(range(24))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig("san_diego_load_profiles.png", dpi=300)
print("Plot saved as san_diego_load_profiles.png")
 
# creates a dataframe organized by the hour with the Fourier-smoothed residential load profile, solar generation profile (AC system output), and the time-of-use tariff rate. Divided between summer and winter. All values rounded to the nearest thousandth!
summer_table = pd.DataFrame({
    "Hour": summer_combined["hour"],
    "Load-Smoothed (kWh)": summer_combined["smooth"],
    "Solar (kWh)": summer_combined["solar_kwh"],
    "TOU Rate ($/kWh)": summer_combined["tou_rate"]
})

# saves it as a csv for usage in cost optimization model
summer_table.to_csv("summer_table.csv", index=False)

winter_table = pd.DataFrame({
    "Hour": winter_combined["hour"],
    "Load-Smoothed (kWh)": winter_combined["smooth"],
    "Solar (kWh)": winter_combined["solar_kwh"],
    "TOU Rate ($/kWh)": winter_combined["tou_rate"]
})

winter_table.to_csv("winter_table.csv",index=False)

# graph the two tables above (one for winter, one for summer)
fig, ax = plt.subplots(figsize=(8, 8))

ax.axis("off")

table = ax.table(
    cellText=summer_table.round(3).values,
    colLabels=summer_table.columns,
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.4)

plt.title("Representative Summer Profile (Weekday)")
plt.savefig("summer_profile_table.png", dpi=300, bbox_inches="tight")
print("Plot saved as summer_profile_table.png")

fig, ax = plt.subplots(figsize=(8, 8))

ax.axis("off")

table = ax.table(
    cellText=winter_table.round(3).values,
    colLabels=winter_table.columns,
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.4)

plt.title("Representative Winter Profile (Weekday)")
plt.savefig("winter_profile_table.png", dpi=300, bbox_inches="tight")
print("Plot saved as winter_profile_table.png")
