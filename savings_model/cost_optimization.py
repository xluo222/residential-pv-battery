import numpy as np
import cvxpy as cp
import pandas as pd

# reads summer and winter tables from fourier_load.py containing the daily load, generation, and tou rates by the hour. 
summer = pd.read_csv("summer_table.csv")

load = summer["Load-Smoothed (kWh)"].values
solar = summer["Solar (kWh)"].values
price = summer["TOU Rate ($/kWh)"].values
export_price = 0.06

n = 24 # 24 hours, unknown charging amounts
battery_capacity = 6
# implement this later with the variety of sizes!!
#battery_capacity = size
#power_limit = battery_capacity/2
power_limit = 3 # represents how much the battery can charge/discharge in an hour
eta_c = 0.95 # efficiency charging/discharging
eta_d = 0.95

# optimization variables
charge = cp.Variable(n, nonneg=True)
charge[0] == 0
discharge = cp.Variable(n, nonneg=True)
discharge[0] == 0
soc = cp.Variable(n) # state of charge, remaining capacity available in a battery
grid_import = cp.Variable(n, nonneg=True)
grid_export = cp.Variable(n, nonneg=True)

constraints = []

# battery capacity limits 
constraints += [
    soc >= 0, 
    soc <= battery_capacity 
]

# power limits
constraints += [
    charge <= power_limit, # limit is generally around half of the battery capacity 
    discharge <= power_limit
]

# initial battery capacity (starts at the same place no matter battery size)
constraints += [
    soc[0] == battery_capacity/2
]

for t in range(1,n):
    constraints += [
    soc[t] == soc[t-1] + eta_c * charge[t] - discharge[t]/eta_d
    ]

# ensures the model doesn't empty the battery completely at night to reduce the day's bill and leaves it empty the next day
constraints += [
    soc[-1] == soc[0]
]

for t in range(0,n):
    constraints += [
        load[t] == solar[t] + grid_import[t] + discharge[t] - charge[t] - grid_export[t],
        grid_export[t] <= solar[t]
    ]

objective = cp.Minimize(
    cp.sum(
        cp.multiply(grid_import, price) - cp.multiply(grid_export, export_price)
    )
)

problem = cp.Problem(objective, constraints)

problem.solve()

import_cost = grid_import.value * price
export_credit = grid_export.value * export_price
net_cost = import_cost - export_credit

results = pd.DataFrame({
    "Hour": np.arange(n),
    "Load (kWh)": load,
    "Solar (kWh)": solar,
    "Charge (kWh)": charge.value,
    "Discharge (kWh)": discharge.value,
    "SOC (kWh)": soc.value,
    "Grid Import (kWh)": grid_import.value,
    "Grid Export (kWh)": grid_export.value,
    "Import Cost ($)": import_cost,
    "Export Credit ($)": export_credit,
    "Net Cost ($)": net_cost
})

# CVXPY produces tiny nonzero values because of numerical precision, treating values below 1e-6 as zero. 
numeric_cols = results.columns.drop("Hour") # leave hour column out of this
results[numeric_cols] = results[numeric_cols].mask(
    results[numeric_cols].abs() < 1e-6, 0
)

# Round to 3 decimal places
results = results.round(3)

print(results)

print("Total import cost: $", round(import_cost.sum(), 2))
print("Total export credit: $", round(export_credit.sum(), 2))
print("Net daily cost: $", round(net_cost.sum(), 2))


# comparing the results against the no battery case

net_load = load - solar

grid_import_no_battery = np.maximum(net_load, 0) # if net load is neg, no need to import, but can export
grid_export_no_battery = np.maximum(-net_load, 0) 

cost_no_battery = np.sum(
    grid_import_no_battery * price
    - grid_export_no_battery * export_price
)

cost_with_battery = net_cost.sum()

daily_savings = cost_no_battery - cost_with_battery

print(f"No battery: ${cost_no_battery:.2f}")
print(f"With battery: ${cost_with_battery:.2f}")
print(f"Daily savings: ${daily_savings:.2f}")

