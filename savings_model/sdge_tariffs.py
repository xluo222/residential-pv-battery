import pandas as pd

rates_df = pd.read_csv("sdge_tou_rates.csv")

print(rates_df)

schedule_df = pd.read_csv(
    "sdge_weekday.csv"
)

print(schedule_df)
