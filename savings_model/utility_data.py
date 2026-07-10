import requests
import pandas as pd

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

df = df.drop(columns =["price-units", "sectorid", "sectorName"]) # removes these three columns

df = df.reset_index(drop=True) # removes the old index numbers (before sorting)

print(df.sort_values(by=["stateid", "period"])) # sorts values by state and year

df.to_csv("utility_data.csv", index=False)

# would be really cool to create a model that takes inputs (for state year) and tells you if it's feasible to create a pv system + battery depending on your circumstances
Mark set
