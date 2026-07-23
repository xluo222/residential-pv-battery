# residential-pv-battery
This is a model that examines the economic feasibility of colocation of residential solar pv systems and battery storage. It examines combining time-of-use tariff rates in San Diego, California with representative seasonal hourly residential load profiles to calculate the cost of electricity for a home in the United states. Then, using solar generation profiles and battery storage cost optimization, it calculates how much money battery storage would save the homeowner and how to best optimize battery storage. The goal is to determine when and how battery storage can be economically advantageous for residential solar PV systems.

# Prerequisites 
You will need to install these following packages on python in your terminal to successfully run the program
* numpy
* scipy
* matplotlib
* pandas
* geopandas
* cvxpy
  
Use this example to install each package:
```
pip install pandas
```

Additionally, this model requires access to the National Renewable Energy Laboratory (NREL) PVWatts API for the solar generation profiles. Please sign up for an API key here: https://developer.nlr.gov/signup/. Keep in mind that API keys are unique and should not be shared with others. Use this code to set the API key within your terminal: 
```
export NREL_API_KEY = "your_actual_api_key"
```

# Reproducibility 
To get this program and its necessary files, run this:
```
git clone https://github.com/xluo222/residential-pv-battery.git
cd residential-pv-battery
```

# Running code
To view results from the cost optimization model for battery storage, run this code:
```
python3 cost_optimization.py
```
To see the calculations for the Fourier-smoothed residential load profiles, run this:
```
python3 fourier_load.py
```
and to see the graphed daily load profiles, run this:
```
xdg-open san_diego_load_profiles.png
```

# Creating a virtual environment
If using Linux or MacOS, run this code:
```
bash
python3 -m venv .venv
```
To activate the environment, run this:
```
source .venv/bin/activate
```
If using Windows, run this instead:
```
powershell
python -m venv .venv
```
And to activate:
```
.venv\Scripts\activate.bat
```
