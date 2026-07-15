import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import time

folder = "CAISO_monthly_data"

if not os.path.exists(folder):
    os.makedirs(folder)

url = "https://oasis.caiso.com/oasisapi/SingleZip"

start = datetime(2015, 1, 1)
end = datetime(2025, 12, 31)

current = start

# loops through each month and gets the respective CAISO file
while current <= end:

    next_month = current + relativedelta(months=1)

    # format dates for CAISO API
    start_date = current.strftime(
        "%Y%m%dT00:00-0000"
    )

    end_date = (next_month - relativedelta(seconds=1)).strftime(
        "%Y%m%dT23:59-0000"
    )

    # dictionary stores LMP (locational marginal price) data
    params = {
        "queryname": "PRC_LMP",
        "startdatetime": start_date,
        "enddatetime": end_date,
        "version": "1",
        "market_run_id": "DAM",
        "grp_type": "ALL_APNODES"
    }

    print(
        "Downloading:",
        current.strftime("%Y-%m")
    )

    response = requests.get(
        url,
        params=params
    )

    # Check request worked
    if response.status_code == 200:

        filename = (
            f"{folder}/CAISO_{current.year}_{current.month:02d}.zip"
        )

        with open(filename, "wb") as f:
            f.write(response.content)

        print("Saved:", filename)

    else:

        print(
            "FAILED:",
            current.strftime("%Y-%m"),
            response.status_code
        )

    time.sleep(5)
    
    # Move to next month
    current = next_month


print("All downloads complete!")
