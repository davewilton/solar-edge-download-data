import requests
import datetime
import time
import csv
from secret import cookie  # Ensure you have a secret.py with your cookie

site_id = "446327"  # SolarEdge site ID
url = f"https://monitoring.solaredge.com/services/dashboard/energy/sites/{site_id}"
cookies = {
    "SPRING_SECURITY_REMEMBER_ME_COOKIE": cookie,
}


start_date = datetime.date(2017, 4, 11)
end_date = datetime.date.today()

with open("solar_data_energyt.csv", "w", newline="") as csvfile:
    writer = None
    current = start_date
    while current <= end_date:

        print(f"Processing date: {current}")
        params = {
            "start-date": current.isoformat(),
            "end-date": current.isoformat(),
            "chart-time-unit": "quarter-hours",
            "measurement-types": "production,consumption,consumption-distribution-without-storage,production-distribution-without-storage,yield"
        }
        response = requests.get(url, params=params, cookies=cookies)
        if response.status_code == 200:
            data = response.json()
            for m in data.get("chart", {}).get("measurements", []):
                # get the productionDistribution
                production_distribution = m.get("productionDistribution", {})
                production_to_home = production_distribution.get("productionToHome", 0)
                production_to_grid = production_distribution.get("productionToGrid", 0)
                # get the consumptionDistribution
                consumption_distribution = m.get("consumptionDistribution", {})
                consumption_from_solar = consumption_distribution.get("consumptionFromSolar", 0)
                consumption_from_grid = consumption_distribution.get("consumptionFromGrid", 0)
                # combine the data 
                values = {
                    'measurementTime': m.get("measurementTime", ""),
                    'productionToHome': production_to_home,
                    'productionToGrid': production_to_grid,
                    'consumptionFromSolar': consumption_from_solar,
                    'consumptionFromGrid': consumption_from_grid,
                }
       
                # if any of the values are None, replace them with 0
                values = {k: (v if v is not None else 0) for k, v in values.items()}
                if writer is None:
                    # Write header on first row
                    writer = csv.DictWriter(csvfile, fieldnames=values.keys())
                    # writer.writeheader()
                writer.writerow(values)
        else:
            print(f"Failed for {current}: {response.status_code}")
        current += datetime.timedelta(days=1)
        time.sleep(1)  # Be polite to the server

print("Done.")