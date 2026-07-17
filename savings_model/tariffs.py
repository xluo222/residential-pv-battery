import pandas as pd

# arranges the sdge (Southern California) time-of-use utility rates and the corresponding weekday schedule into a dataframe
sdge_rates_df = pd.read_csv("sdge_tou_rates.csv")

print(sdge_rates_df)

sdge_schedule_df = pd.read_csv(
    "sdge_weekday.csv"
)

print(sdge_schedule_df)

# arranges the PSE (Washington) time-of-use utility rates and the corresponding weekday schedule into a dataframe
pse_rates_df = pd.read_csv("pse_tou_rates.csv")

print(pse_rates_df)

pse_schedule_df = pd.read_csv(
    "pse_weekday.csv"
)

print(pse_schedule_df)

# arranges the SPP (Nevada)time-of-use utility rates and the corresponding weekday schedule into a dataframe
spp_rates_df = pd.read_csv("spp_tou_rates.csv")

print(spp_rates_df)

spp_schedule_df = pd.read_csv(
    "spp_weekday.csv"
)

print(spp_schedule_df)

# arranges the NSTAR (Massachusetts) time-of-use utility rates and the corresponding weekday schedule into a dataframe
spp_rates_df = pd.read_csv("spp_tou_rates.csv")

print(spp_rates_df)

spp_schedule_df = pd.read_csv(
    "spp_weekday.csv"
)

print(spp_schedule_df)


