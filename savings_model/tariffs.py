import pandas as pd

# time-of-use tariff costs are calculated depending on the hour and month and through these rates. each pricing period is represented in rate per kWh (kilowatt-hour or 1,000 watts of power running continously for one hour). uses rates listed here: https://apps.openei.org/USURDB/rate/view/6a45822d666a6ad1d40b4d0e#3__Energy

TOU_RATES = {
    1: 0.71598,
    2: 0.38853,
    3: 0.34545,
    4: 0.50219,
    5: 0.37682,
    6: 0.33764
}

# returns the rate on a summer weekday depending on the hour. 12 am is equivalent to hour 0, and 11pm is hour 23
def get_summer_weekday_rate(hour):
    if 0 <= hour < 6:
        return TOU_RATES[3]
    elif 6 <= hour < 10:
        return TOU_RATES[2]
    elif 10 <= hour < 14:
        return TOU_RATES[3]
    elif 14 <= hour < 16:
        return TOU_RATES[2]
    elif 16 <= hour < 21:
        return TOU_RATES[1]
    else:
        return TOU_RATES[2]

# returns the rate on a winter weekday depending on the hour. 12 am is equivalent to hour 0, and 11pm is hour 23. keep in mind that spring weekdays are the exact same rate. 
def get_winter_weekday_rate(hour):
    if 0 <= hour < 6:
        return TOU_RATES[6]
    elif 6 <= hour < 10:
        return TOU_RATES[5]
    elif 10 <= hour < 14:
        return TOU_RATES[6]
    elif 14 <= hour < 16:
        return TOU_RATES[5]
    elif 16 <= hour < 21:
        return TOU_RATES[4]
    else:
        return TOU_RATES[5]

# calculates the daily cost depending on the season (profile) and rate_function, which is the type of rate being used in calculations (either winter or summer weekday)
def calculate_daily_cost(profile, rate_function):
    profile = profile.copy()

    profile["tou_rate"] = profile["hour"].apply(rate_function)
    profile["hourly_cost"] = (
        profile["smooth"] * profile["tou_rate"]
    )

    return profile

# arranges the sdge (Southern California) time-of-use utility rates and the corresponding weekday schedule into a dataframe. prints them out as well for reference
sdge_rates_df = pd.read_csv("sdge_tou_rates.csv")

print(sdge_rates_df)

sdge_schedule_df = pd.read_csv(
    "sdge_weekday.csv"
)

print(sdge_schedule_df)

