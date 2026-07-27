import pandas as pd

df = pd.read_csv("Current Year NBT Pricing Upload MIDAS.csv")

df.columns = df.columns.str.strip() # get rid of whitespace

df["DateStart"] = pd.to_datetime(df["DateStart"], errors="coerce") # convert invalid values to just NaT

start_year = df["DateStart"].dt.year.min()

df = df[df["DateStart"].dt.year < start_year + 9] # legacy pricing only applies to next 9 years, only keep those
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

summer = hourly[
    hourly["DateStart"].dt.month.isin([6,7,8])
]

winter = hourly[
    hourly["DateStart"].dt.month.isin([12,1,2])
]

# take the average export credit by hour for summer and winter
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

print(summer.groupby("hour")["Value"].agg(["min", "max", "mean", "std"]))
print(winter.groupby("hour")["Value"].agg(["min", "max", "mean", "std"]))

summer_profile.to_csv(
    "summer_export_profile.csv",
    index=False
)

winter_profile.to_csv(
    "winter_export_profile.csv",
    index=False
)

import matplotlib.pyplot as plt

summer["year"] = summer["DateStart"].dt.year

plt.figure(figsize=(10,6))

for year in sorted(summer["year"].unique()):
    profile = (
        summer[summer["year"] == year]
        .groupby("hour")["Value"]
        .mean()
    )

    plt.plot(profile.index, profile.values, label=year)

plt.xlabel("Hour")
plt.ylabel("Export Credit ($/kWh)")
plt.title("Summer Weekday Export Profiles by Year")
plt.grid(True)
plt.legend(title="Year", ncol=3)
plt.savefig("summer_profiles", dpi=300)

winter["year"] = winter["DateStart"].dt.year

plt.figure(figsize=(10,6))

for year in sorted(winter["year"].unique()):
    profile = (
        winter[winter["year"] == year]
        .groupby("hour")["Value"]
        .mean()
    )

    plt.plot(profile.index, profile.values, label=year)

plt.xlabel("Hour")
plt.ylabel("Export Credit ($/kWh)")
plt.title("Winter Weekday Export Profiles by Year")
plt.grid(True)
plt.legend(title="Year", ncol=3)
plt.savefig("winter_profiles.png", dpi=300)
