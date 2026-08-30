import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Current Year NBT Pricing Upload MIDAS.csv")

df.columns = df.columns.str.strip() # get rid of whitespace

df["DateStart"] = pd.to_datetime(df["DateStart"], errors="coerce") # convert invalid values to just NaT

df = df[df["DateStart"].dt.year.isin([2026, 2027, 2028])]
df["month"] = df["DateStart"].dt.month

# extract hour
df["hour"] = (
    df["ValueName"].str.extract(r"HS(\d+)").astype(int)
)

# sum of both generation and delivery components for a bundled customer
hourly = (
    df.groupby(["DateStart", "hour"])["Value"]
      .sum()
      .reset_index()
)

hourly["weekday"] = hourly["DateStart"].dt.weekday
hourly = hourly[hourly["weekday"] >= 5]

summer = hourly[
    hourly["DateStart"].dt.month.isin([6,7,8])
]

winter = hourly[
    hourly["DateStart"].dt.month.isin([12,1,2])
]

# take the average export credit by hour for summer and winter weekends (since the rates are different weekend vs weekday)
summer_profile = (
    summer.groupby("hour")["Value"]
          .mean()
          .reset_index()
)

winter_profile = (
    winter.groupby("hour")["Value"]
          .mean()
          .reset_index()
)

summer_profile.rename(
    columns={"Value":"export ($/kWh)"},
    inplace=True
)

winter_profile.rename(
    columns={"Value":"export ($/kWh)"},
    inplace=True
)

summer_profile.to_csv(
    "summer_export_weekend_profile.csv",
    index=False
)

winter_profile.to_csv(
    "winter_export_weekend_profile.csv",
    index=False
)

summer["year"] = summer["DateStart"].dt.year

plt.figure(figsize=(8,5))

plt.plot(
    summer_profile["hour"],
    summer_profile["export ($/kWh)"],
    linewidth=2,
    label="Summer",
    color="salmon"
)

plt.plot(
    winter_profile["hour"],
    winter_profile["export ($/kWh)"],
    linewidth=2,
    label="Winter",
    color="mediumseagreen"
)

plt.xlabel("Hour")
plt.ylabel("Export Credit ($/kWh)")
plt.title("Average Hourly Export Credit Rate (2026–2028)")
plt.xticks(range(0, 24))
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig("export_profile_2026_2028.png", dpi=300)
