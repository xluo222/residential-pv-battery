import requests
import pandas as pd
import matplotlib.pyplot as plt 
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

API_KEY = "xMm34KQDGuPoeSFb32txXesPxUJnngi47VnobkdZ" # remember to remove this!

url = (
    "https://api.eia.gov/v2/electricity/retail-sales/data/"
    f"?api_key={API_KEY}"
    "&frequency=annual"
    "&data[0]=price"
    "&facets[sectorid][]=RES"
    "&start=2010"
    "&end=2026"
)

states = [
    "AK","AL","AR","AZ","CA","CO",
    "CT","DC","DE","FL","GA","HI",
    "IA","ID","IL","IN","KS","KY",
    "LA","MA","MD","ME","MI","MN",
    "MO","MS","MT","NC","ND","NE",
    "NH","NJ","NM","NV","NY","OH",
    "OK","OR","PA","RI","SC","SD",
    "TN","TX","UT","VA","VT","WA",
    "WI","WV","WY"
]

# adds all the states above to the url
for state in states:
    url += f"&facets[stateid][]={state}"

response = requests.get(url)

print(response.status_code) # HTTP status code: 200 if request is successful, 4xx if there's an error

data = response.json()

df = pd.DataFrame(data["response"]["data"])

df = df.sort_values(by=["stateid", "period"]) # sorts values by state and year

df = df.reset_index(drop=True) # removes the old index numbers)

df = df.drop(columns =["price-units", "sectorid", "sectorName"]) # removes these three columns

# converts strings in price column to numbers
df["price"] = pd.to_numeric(df["price"])

# calculates year-to-year growth rate, returns decimal
df["growth_rate (%)"] = (
    df.groupby("stateid")["price"]
      .pct_change() * 100
)

print (df)

df.to_csv("utility_data.csv", index=False)

forecast_results = []

# Run the ARIMA forecasting model for each state
for state in df["stateid"].unique():
    try: 
        state_df = df[df["stateid"] == state].copy()

        model = ARIMA(
            state_df["price"],
            order=(1,1,1)
        )

        results = model.fit()

        forecast = results.forecast(steps=25)

        future_years = range(2026, 2051)
    
        temp = pd.DataFrame({
            "stateid": state,
            "year": future_years,
            "forecast_price": forecast
        })

        forecast_results.append(temp)

    except Exception as e:
        print(state, "failed:", e)


forecast_df = pd.concat(
    forecast_results,
    ignore_index=True
)

print (forecast_df)

forecast_df.to_csv("forecast_prices.csv", index=False)

#plt.plot(ca["period"], ca["price"], label="Historical Prices")
#plt.plot(future_years, forecast, label="Forecast", linestyle='--')

#plt.title("California Residential Electricity Prices")
#plt.xlabel("Year")
#plt.ylabel("price(cents/kWh)")
#plt.legend()

#plt.show()


# would be really cool to create a model that takes inputs (for state year) and tells you if it's feasible to create a pv system + battery depending on your circumstances
