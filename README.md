# residential-pv-battery
This is a model that examines the economic feasibility of colocation of residential solar battery storage for homeowners in the San Diego region. It optimizes battery dispatch across a range of battery capacities and finds the battery size that minimizes the cost of electricity and balances the tradeoff between operational savings and annualized capital cost. The goal is to determine when and how battery storage can be economically advantageous for residential solar PV systems.

The repository includes pre-generated PV generation data, so an NREL API key is not required to reproduce the results in this project. Users who wish to generate new PV profiles for a different location may optionally use the NREL PVWatts API. To do so, obtain an API key from: https://developer.nrel.gov/signup/
Keep in mind that API keys are unique and should not be shared with others. Use this code to set the API key within your terminal: 
```
export NREL_API_KEY="your_actual_api_key"
```

# Reproducibility 
To get this program and its necessary files, run this:
```
git clone https://github.com/xluo222/residential-pv-battery.git
cd residential-pv-battery
```

# Creating a virtual environment
If using Linux or MacOS, run this code:
```bash
python3 -m venv .venv
```
To activate the environment, run this:
```
source .venv/bin/activate
```
If using Windows, run this instead:
```
python -m venv .venv
```
And to activate:
```
.venv\Scripts\activate.bat
```
# Installation prerequisites
Upgrade `pip`:

```
python -m pip install --upgrade pip
```

Install the required Python packages:
* numpy
* scipy
* matplotlib
* pandas
* cvxpy
* requests
  
```
python -m pip install pandas numpy scipy matplotlib requests cvxpy
```

# Running code
To view results from the cost optimization model for battery storage for each season, run this code:
```
python3 winter_cost_optimization.py
```
and this:
```
python3 summer_cost_optimization.py
```

To see the calculations for the Fourier-smoothed residential load profiles, run this:
```
python3 fourier_load.py
```
and to see the graphed daily load profiles, run this:
```
xdg-open san_diego_load_profiles.png
```
