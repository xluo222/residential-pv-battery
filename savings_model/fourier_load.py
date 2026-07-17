import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# reads the load data from San Diego (SDGE, Southern California)
load = pd.read_csv(
    "RESIDENTIAL_LOAD_DATA_E_PLUS_OUTPUT (2)/BASE/USA_CA_San.Diego-Miramar.NAS.722930_TMY3_BASE.csv"
)

# renames the columns for later calculations
load = load.rename(columns={
    "Date/Time": "datetime",
    "Electricity:Facility [kW](Hourly)":"load_kw"
})

# values are hourly averages, treat them as hourly energy for calculations
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

# extracts the hour
hour_part = raw_datetime.str[6:8].astype(int)

# converts text-based time and time strings into official datetime objects
load["datetime"] = date_part + pd.to_timedelta(
    hour_part,
    unit="h"
)

load["month"] = load["datetime"].dt.month
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

# average by hour and by season (summer, winter, and annual patterns)
summer = (
    load[load["season"]=="summer"]
    .groupby("hour")["load_kwh"]
    .mean()
    .reset_index()
)

winter = (
    load[load["season"]=="winter"]
    .groupby("hour")["load_kwh"]
    .mean()
    .reset_index()
)

annual = (
    load.groupby("hour")["load_kwh"]
    .mean()
    .reset_index()
)

# function for applying Fourier transform to 24-hour averages
# Fourier  breaks down time-based signals into individual sine and cosine frequency components and reveals which frequencies are present, and how strong they are. Used for finding summer, winter, and annual usage patterns by the hour here. 
def fourier_smooth(profile_df, harmonics=3):
    
    # extracts load numbers into a NumPy array
    values = profile_df["load_kwh"].values

    # finds the waves
    fft = np.fft.fft(values)

    filtered = np.zeros_like(fft)
    filtered[0] = fft[0]

    # builds the curve using three waves
    for i in range(1, harmonics + 1):
        # fourier coefficients come in pairs
        filtered[i] = fft[i]
        filtered[-i] = fft[-i]

    profile_df["smooth"] = np.fft.ifft(filtered).real

    return profile_df

summer = fourier_smooth(summer)
winter = fourier_smooth(winter)
annual = fourier_smooth(annual)

print("\nSummer profile:")
print(summer)

print("\nWinter profile:")
print(winter)

print("\nAnnual profile:")
print(annual)

# plot both the original hourly averages and the Fourier-smoothed profiles
plt.figure(figsize=(10, 6))

plt.plot(
    summer["hour"],
    summer["load_kwh"],
    marker="o",
    linestyle="--",
    label="Summer average"
)

plt.plot(
    summer["hour"],
    summer["smooth"],
    linewidth=2,
    label="Summer Fourier-smoothed"
)

plt.plot(
    winter["hour"],
    winter["load_kwh"],
    marker="o",
    linestyle="--",
    label="Winter average"
)

plt.plot(
    winter["hour"],
    winter["smooth"],
    linewidth=2,
    label="Winter Fourier-smoothed"
)

plt.plot(
    annual["hour"],
    annual["load_kwh"],
    marker="o",
    linestyle="--",
    label="Annual average"
)

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

