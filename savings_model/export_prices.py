import pandas as pd

df = pd.read_csv("Current Year NBT Pricing Upload MIDAS.csv")

df.columns = df.columns.str.strip() # get rid of whitespace
print(df.columns)

df["DateStart"] = pd.to_datetime(df["DateStart"], errors="coerce") # convert invalid values to just NaT

df["month"] = df["DateStart"].dt.month

# extract hour
df["hour"] = (
    df["ValueName"].str.extract(r"HS(\d+)").astype(int)
)

summer = df[
    df["DateStart"].dt.month.isin([6,7,8])
]

winter = df[
    df["DateStart"].dt.month.isin([12,1,2])
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

summer_profile.to_csv(
    "summer_export_profile.csv",
    index=False
)

winter_profile.to_csv(
    "winter_export_profile.csv",
    index=False
)
