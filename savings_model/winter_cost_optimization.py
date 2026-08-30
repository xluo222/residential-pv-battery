import numpy as np
import cvxpy as cp
import pandas as pd
import matplotlib.pyplot as plt

# reads winter tables from fourier_load.py containing the daily load, generation, and tou rates by the hour. 
winter = pd.read_csv("winter_table.csv")
winter_export = pd.read_csv("winter_export_profile.csv")

load = winter["Load (kWh)"].values
solar = winter["Solar (kWh)"].values
price = winter["TOU Rate ($/kWh)"].values
export_price = winter_export["export ($/kWh)"].values

cost_per_kwh = 800
fixed_installation_cost = 0
discount_rate=  0.07
battery_lifetime_years = 10
sgip_incentive = 200 # per kWh

# calculates the battery's original upfront cost and cost after incentives (like SGIP)
def calculate_battery_capital_cost(battery_capacity):
    original_battery_cost = (
        battery_capacity * (cost_per_kwh - sgip_incentive)
        + fixed_installation_cost
    )

    return original_battery_cost

# converts net battery cost into equivalent annual cost using the capital recovery factor
def annualize_battery_cost(battery_cost):
    r = discount_rate
    n = battery_lifetime_years

    if r == 0:
        capital_recovery_factor = 1 / n
    else:
        capital_recovery_factor = (
            r * (1 + r) ** n
            / ((1 + r) ** n - 1)
        )

    annualized_cost = (
        battery_cost
        * capital_recovery_factor
    )

    return annualized_cost

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

    electricity_cost = cp.sum(
        cp.multiply(grid_import, price)
        - cp.multiply(grid_export, export_price)
    )

    objective = cp.Minimize(
        electricity_cost
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
        "SOC End (kWh)": soc.value[1:],
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
    
    daily_operating_cost = net_cost.sum()
    
    print(
        "Daily operating cost: $",
        round(daily_operating_cost, 2),
        "per day"
    )

    return {
        "daily_operating_cost": daily_operating_cost,
    }
     
# comparing the results against the no battery case

net_load = load - solar

grid_import_no_battery = np.maximum(net_load, 0) # if net load is neg (more generated than used), no need to import, but can still export
grid_export_no_battery = np.maximum(-net_load, 0) 

cost_no_battery = np.sum(
    grid_import_no_battery * price
    - grid_export_no_battery * export_price
)

battery_sizes = [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20]

battery_results = []

for size in battery_sizes:
    result = optimize_battery_size(size)

      # battery capital costs for this specific capacity
    original_battery_cost = (
        calculate_battery_capital_cost(size)
    )

    annualized_capital_cost = annualize_battery_cost(
        original_battery_cost
    )

    # the dispatch model represents one day, so convert the annualized cost into an equivalent daily cost.
    daily_amortized_capital_cost = (
        annualized_capital_cost / 365
    )

    operational_savings = (
        cost_no_battery
        - result["daily_operating_cost"]
    )

    net_benefit = operational_savings - daily_amortized_capital_cost

    battery_results.append({
        "Battery Size (kWh)": size,

        "Daily Operating Cost ($)":
            result["daily_operating_cost"],

        "Daily Operational Savings ($)":
            operational_savings,

        "Original Battery Cost ($)":
            original_battery_cost,

        "Annualized Capital Cost ($/year)":
            annualized_capital_cost,

        "Daily Amortized Capital Cost ($)":
            daily_amortized_capital_cost,

        "Net benefit ($/day)":
            net_benefit
    })

battery_results = pd.DataFrame(battery_results)

battery_results = battery_results.round(3)

battery_results.to_csv("winter_battery_results.csv", index=False)

optimal_index = battery_results[
    "Net benefit ($/day)"
].idxmax()

optimal_battery = battery_results.loc[optimal_index]

print("\nBattery sizing results:")
print(battery_results)

print("\nOptimal battery size:")
print(optimal_battery)

# graphing the battery size vs net benefit curve
plt.figure(figsize=(7,5))

plt.plot(
    battery_results["Battery Size (kWh)"],
    battery_results["Net benefit ($/day)"],
    marker="o",
    color="steelblue"
)

plt.xlabel("Battery Capacity (kWh)")
plt.ylabel("Daily Net Benefit ($)")
plt.title("Net Benefit vs. Battery Capacity")

plt.grid(True)

plt.savefig("winter_net_benefit_vs_capacity.png", dpi=300)
