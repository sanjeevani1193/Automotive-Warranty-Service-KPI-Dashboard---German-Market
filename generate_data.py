import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

MODELS = {
    "EV6":      "Electric",
    "EV9":      "Electric",
    "Niro":     "Hybrid",
    "Sportage": "Petrol",
    "Sorento":  "Diesel",
    "Stinger":  "Petrol",
    "Ceed":     "Petrol",
}

CITY_REGION = {
    "Hamburg":    "North",
    "Hannover":   "North",
    "Berlin":     "East",
    "Leipzig":    "East",
    "Cologne":    "West",
    "Düsseldorf": "West",
    "Frankfurt":  "Central",
    "Stuttgart":  "South",
    "Munich":     "South",
    "Nuremberg":  "South",
}

SERVICE_TYPES = ["Routine Maintenance", "Repair", "Inspection", "Emergency Repair"]

ISSUE_CATEGORIES = ["Electrical", "Powertrain", "Brakes", "Infotainment", "HVAC", "Body & Exterior"]

CLAIM_STATUSES = ["Approved", "Rejected", "Pending"]

START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2025, 12, 31)



def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))



def generate_vehicles(n=1000):
    records = []
    for i in range(1, n + 1):
        model       = random.choice(list(MODELS.keys()))
        fuel_type   = MODELS[model]
        city        = random.choice(list(CITY_REGION.keys()))
        region      = CITY_REGION[city]
        purchase_date = random_date(START_DATE, END_DATE - timedelta(days=365))
        warranty_end  = purchase_date + timedelta(days=365 * 2)
        records.append({
            "vehicle_id":       f"VEH-{str(i).zfill(4)}",
            "customer_id":      f"CUST-{str(random.randint(1, 800)).zfill(4)}",
            "model":            model,
            "model_year":       random.randint(2019, 2025),
            "fuel_type":        fuel_type,
            "purchase_date":    purchase_date.date(),
            "city":             city,
            "region":           region,
            "warranty_end_date": warranty_end.date(),
        })
    return pd.DataFrame(records)



def generate_service_visits(vehicles, n=3000):
    records = []
    for i in range(1, n + 1):
        vehicle       = vehicles.sample(1).iloc[0]
        purchase_date = datetime.strptime(str(vehicle["purchase_date"]), "%Y-%m-%d")
        service_date  = random_date(purchase_date + timedelta(days=30), END_DATE)
        service_type  = random.choice(SERVICE_TYPES)
        records.append({
            "service_id":      f"SERV-{str(i).zfill(5)}",
            "vehicle_id":      vehicle["vehicle_id"],
            "service_date":    service_date.date(),
            "service_type":    service_type,
            "resolution_days": random.randint(1, 30),
            "service_cost":    round(random.uniform(50, 1500), 2),
        })
    return pd.DataFrame(records)




def generate_warranty_claims(vehicles, service_visits, n=1200):
    records = []
    attempts = 0
    while len(records) < n and attempts < n * 10:
        attempts += 1
        vehicle    = vehicles.sample(1).iloc[0]
        vid        = vehicle["vehicle_id"]
        v_services = service_visits[service_visits["vehicle_id"] == vid]
        if v_services.empty:
            continue
        earliest_service = datetime.strptime(
            str(v_services["service_date"].min()), "%Y-%m-%d"
        )
        claim_date = random_date(earliest_service, END_DATE)
        status     = random.choices(CLAIM_STATUSES, weights=[60, 20, 20])[0]
        claim_cost = round(random.uniform(100, 5000), 2)
        if status == "Approved":
            approved_amount = round(claim_cost * random.uniform(0.8, 1.0), 2)
        elif status == "Rejected":
            approved_amount = 0.0
        else:
            approved_amount = None  # pending

        records.append({
            "claim_id":         f"CLAIM-{str(len(records)+1).zfill(5)}",
            "vehicle_id":       vid,
            "claim_date":       claim_date.date(),
            "issue_category":   random.choice(ISSUE_CATEGORIES),
            "claim_status":     status,
            "claim_cost":       claim_cost,
            "approved_amount":  approved_amount,
            "resolution_days":  random.randint(1, 60) if status != "Pending" else None,
        })
    return pd.DataFrame(records)



def main():
    import os
    os.makedirs("data", exist_ok=True)

    print("Generating vehicles...")
    vehicles = generate_vehicles()
    vehicles.to_csv("data/vehicles.csv", index=False)

    print("Generating service visits...")
    service_visits = generate_service_visits(vehicles)
    service_visits.to_csv("data/service_visits.csv", index=False)

    print("Generating warranty claims...")
    warranty_claims = generate_warranty_claims(vehicles, service_visits)
    warranty_claims.to_csv("data/warranty_claims.csv", index=False)

    print(f"\nDone!")
    print(f"  vehicles:        {len(vehicles)} rows")
    print(f"  service_visits:  {len(service_visits)} rows")
    print(f"  warranty_claims: {len(warranty_claims)} rows")

if __name__ == "__main__":
    main()