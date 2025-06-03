import csv



def simulate_battery(filename, BATTERY_CAPACITY, production_multiplier):
    battery_soc = 0  # Wh, carried over between days
    total_grid_before = 0
    total_grid_after = 0
    cents_per_kWh = 0.3  # Cost of grid electricity in $/kWh

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Get values, defaulting to 0 if missing
            prod_to_home = float(row.get("productionToHome", 0) or 0) * production_multiplier
            prod_to_grid = float(row.get("productionToGrid", 0) or 0) * production_multiplier
            cons_from_solar = float(row.get("consumptionFromSolar", 0) or 0)
            cons_from_grid = float(row.get("consumptionFromGrid", 0) or 0)

            # Excess solar available for battery (not used by home or exported)
            excess_solar = prod_to_home + prod_to_grid - cons_from_solar
            if excess_solar > 0:
                charge = min(excess_solar, BATTERY_CAPACITY - battery_soc)
                battery_soc += charge

            # Try to cover grid consumption with battery
            discharge = min(cons_from_grid, battery_soc)
            battery_soc -= discharge
            new_grid = cons_from_grid - discharge

            total_grid_before += cons_from_grid
            total_grid_after += new_grid

        print(f"battery capacity: {BATTERY_CAPACITY/1000:.2f} kWh Production multiplier: {production_multiplier:.2f}")
        print(f"Grid consumption before battery: {total_grid_before/1000000:.2f} MWh")
        print(f"Grid consumption after battery: {total_grid_after/1000000:.2f} MWh")
        print(f"Grid cost before battery: ${total_grid_before * cents_per_kWh / 1000:.2f} ")
        print(f"Grid cost after battery: ${total_grid_after * cents_per_kWh / 1000:.2f} ")
        print(f"Grid reduction: {((total_grid_before-total_grid_after)/total_grid_before)*100:.1f}%")
        return {
            "battery_capacity": BATTERY_CAPACITY,
            "production_multiplier": production_multiplier,
            "grid_before_MWh": total_grid_before / 1000000,
            "grid_before_MWh": total_grid_after / 1000000,
            "grid_cost_before_$": total_grid_before * cents_per_kWh / 1000,
            "grid_cost_after_$": total_grid_after * cents_per_kWh / 1000,
        }

def read_2024_consumption(filename):
    grid_total = 0
    solar_total = 0

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            measurement_time = row.get("measurementTime", "")
            if measurement_time.startswith("2024"):
                grid = float(row.get("consumptionFromGrid", 0) or 0) 
                solar = float(row.get("consumptionFromSolar", 0) or 0)
                grid_total += grid
                solar_total += solar

    print(f"2024 Consumption from Grid: {grid_total /  1000000} MWh")
    print(f"2024 Consumption from Solar: {solar_total / 1000000} MWh")
    print(f"Self Consumption Ratio: {solar_total / (grid_total + solar_total) * 100:.1f}%")

def write_all_results_to_csv(all_results, filename):
    if not all_results:
        print("No results to write.")
        return

    # Use the keys from the first dict as the CSV header
    fieldnames = all_results[0].keys()

    with open(filename, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"Wrote {len(all_results)} rows to {filename}")

if __name__ == "__main__":
    # todo. figures are all wrong as it is not converting watt to watt-hours
    read_2024_consumption("solar_data_energy.csv")
    all_results = []
    for production_multiplier in [1.0, 1.5, 2.0]:
        for i in range(6, 13):
            battery_capacity = i * 1000  # Convert kWh to Wh
            print(f"Simulating battery with capacity: {battery_capacity / 1000:.2f} kWh")
            all_results.append(simulate_battery("solar_data_energy.csv", battery_capacity, production_multiplier))
    write_all_results_to_csv(all_results, "battery_simulation_results.csv")
