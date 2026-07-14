import requests
import pandas as pd
import matplotlib.pyplot as plt 
from statsmodels.tsa.arima.model import ARIMA
import warnings

# ignores the additional warnings from the ARIMA model 
warnings.filterwarnings("ignore")

API_KEY = "xMm34KQDGuPoeSFb32txXesPxUJnngi47VnobkdZ" # remember to remove this!

url = (
    "https://api.eia.gov/v2/electricity/retail-sales/data/"
    f"?api_key={API_KEY}"
    "&frequency=annual"
    "&data[0]=price"
    "&facets[sectorid][]=RES"
    "&start=2001"
    "&end=2026"
)

states = ["CA",
          "NV",
          "WA",
          "MA"
]


# adds all the states above to the url
for state in states:
    url += f"&facets[stateid][]={state}"

# result of get request from api
response = requests.get(url)

print(response.status_code) # HTTP status code: 200 if request is successful, 4xx if there's an error

data = response.json()

df = pd.DataFrame(data["response"]["data"])

df = df.sort_values(by=["stateid", "period"]) # sorts values by state and year

df = df.reset_index(drop=True) # removes the old index numbers)

df = df.drop(columns =["price-units", "sectorid", "sectorName"]) # removes these three columns

# converts strings in price column to numbers
df["price"] = pd.to_numeric(df["price"])

# calculates year-to-year growth rate, returns percentage
df["growth_rate (%)"] = (
    df.groupby("stateid")["price"]
      .pct_change() * 100
)

print (df)

# saves the dataframe to utility_data.csv without index numbers
df.to_csv("utility_data.csv", index=False)

forecast_results = []

# Run the ARIMA time series  model for each state to forecast future utility rates (next 25 years). Goes through each state alphabetically
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

# creates a graph with california's rates from 2010-2051 using its historical data and forecasted prices
state = "CA"
history = df[df["stateid"] == state]
history["period"] = pd.to_numeric(history["period"]) # converts years from strings to numbers
forecast = forecast_df[forecast_df["stateid"] == state]

plt.figure(figsize=(10,6))

# draws the historical prices line
plt.plot(
    history["period"],
    history["price"],
    label="Historical Prices",
    linewidth=2
)

# draws forecasted prices as a dashed line
plt.plot(
    forecast["year"],
    forecast["forecast_price"],
    label="Forecast",
    linestyle="--",
    linewidth=2
)

plt.title("California Residential Electricity Prices")
plt.xlabel("Year")
plt.ylabel("price(cents/kWh)")
plt.legend()

plt.grid(True)

plt.savefig("CA_forecast_graph.png", dpi=300)
plt.show()
plt.close() 
