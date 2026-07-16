import pandas as pd

sdge_rates_df = pd.read_csv("sdge_tou_rates.csv")

print(sdge_rates_df)

sdge_schedule_df = pd.read_csv(
    "sdge_weekday.csv"
)

print(sdge_schedule_df)

pse_rates_df = pd.read_csv("pse_tou_rates.csv")

print(pse_rates_df)

pse_schedule_df = pd.read_csv(
    "pse_weekday.csv"
)

print(pse_schedule_df)

