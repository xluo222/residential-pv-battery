import numpy as np
import cvxpy as cp
import pandas as pd

# reads winter tables from fourier_load.py containing the daily load, generation, and tou rates by the hour. 
winter = pd.read_csv("winter_table.csv")

load = winter["Load-Smoothed (kWh)"].values
solar = winter["Solar (kWh)"].values
price = winter["TOU Rate ($/kWh)"].values
export_price = 0.06

# runs through the list of different battery sizes to test out how much they would save
def optimize_battery_size(battery_capacity):
    n = 24
    power_limit = battery_capacity/2 # represents how much the battery can charge/discharge in an hour
    eta_c = 0.95 # efficiency charging/discharging
    eta_d = 0.95

    # optimization variables
    charge = cp.Variable(n, nonneg=True)
    discharge = cp.Variable(n, nonneg=True)
    soc = cp.Variable(n + 1) # state of charge, remaining capacity available in a battery
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

    constraints += [
        charge[0] == 0,
        discharge[0] == 0
    ]

    # initial battery capacity (starts at the same place no matter battery size)
    constraints += [
        soc[0] == battery_capacity/2
    ]
    
    for t in range(n):
        constraints += [
            soc[t+1] == soc[t] + eta_c * charge[t] - discharge[t]/eta_d
        ]

    # ensures the model doesn't empty the battery completely at night to reduce the day's bill and leaves it empty the next day
    constraints += [
        soc[n] == soc[0]
    ]
        
    for t in range(0,n):
        constraints += [
            solar[t] + grid_import[t] + discharge[t]  == load[t] + charge[t] + grid_export[t],

            charge[t] + grid_export[t] <= solar[t]
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
        "SOC (kWh)": soc.value[:-1],
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

    results.to_csv('results.csv', index=False)
    
    print("Total import cost: $", round(import_cost.sum(), 2))
    print("Total export credit: $", round(export_credit.sum(), 2))
    print("Net daily cost: $", round(net_cost.sum(), 2))
    
    cost_with_battery = net_cost.sum()
    
    return cost_with_battery
            
# comparing the results against the no battery case

net_load = load - solar

grid_import_no_battery = np.maximum(net_load, 0) # if net load is neg (more generated than used), no need to import, but can still export
grid_export_no_battery = np.maximum(-net_load, 0) 

cost_no_battery = np.sum(
    grid_import_no_battery * price
    - grid_export_no_battery * export_price
)

battery_sizes = [2, 6, 10, 12, 14, 18, 20]

battery_results = []

for size in battery_sizes:
    cost_with_battery = optimize_battery_size(size)

    battery_results.append({
        "Battery Size (kWh)": size,
        "Daily Cost ($)": cost_with_battery,
        "Daily Savings ($)": cost_no_battery - cost_with_battery
    })

battery_results = pd.DataFrame(battery_results)

print(battery_results)




