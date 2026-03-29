import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

db_path = "warranty_kpi.db"
output_dir = "outputs/charts"
table_dir = "outputs/tables"

os.makedirs(output_dir, exist_ok=True)
os.makedirs(table_dir, exist_ok=True)

# ------------------------------------------------------------------------
conn = sqlite3.connect(db_path)

setup_sql = """
DROP VIEW IF EXISTS valid_warranty_claims;
CREATE VIEW valid_warranty_claims AS
SELECT wc.*
FROM warranty_claims wc
JOIN vehicles v
  ON wc.vehicle_id = v.vehicle_id
WHERE wc.claim_date <= v.warranty_end_date;

DROP VIEW IF EXISTS valid_service_visits;
CREATE VIEW valid_service_visits AS
SELECT sv.*
FROM service_visits sv
JOIN vehicles v
  ON sv.vehicle_id = v.vehicle_id
WHERE sv.service_date <= v.warranty_end_date;
"""
conn.executescript(setup_sql)
# ------------------------------------------------------------------------

def run_query(query, name):
    df = pd.read_sql_query(query, conn)
    df.to_csv(f"{table_dir}/{name}.csv", index=False)
    return df

dq_claims = run_query("""
SELECT COUNT(*) AS claims_outside_warranty
FROM warranty_claims wc
JOIN vehicles v
  ON wc.vehicle_id = v.vehicle_id
WHERE wc.claim_date > v.warranty_end_date;
""", "dq_claims_outside_warranty")

dq_services = run_query("""
SELECT COUNT(*) AS services_outside_warranty
FROM service_visits sv
JOIN vehicles v
  ON sv.vehicle_id = v.vehicle_id
WHERE sv.service_date > v.warranty_end_date;
""", "dq_services_outside_warranty")

print("Claims outside warranty:", dq_claims.iloc[0, 0])
print("Services outside warranty:", dq_services.iloc[0, 0])

# ------------------------------------------------------------------------
# KPI Queries
# ------------------------------------------------------------------------

kpi1 = run_query("""
select sum(claim_cost) as total_claim_cost,
sum(approved_amount) as total_approved_cost
from valid_warranty_claims;
""", "kpi1_total_claimed_vs_approved")

kpi2 = run_query("""
select vehicles.model,
count(valid_warranty_claims.claim_id) as no_of_claims,
count(distinct vehicles.vehicle_id) AS no_of_vehicles,
round(100.0 * count(valid_warranty_claims.claim_id) / count(distinct vehicles.vehicle_id), 2) AS claims_per_100_vehicles,
round(avg(valid_warranty_claims.claim_cost),2) as avg_claim_cost,
round(coalesce(sum(valid_warranty_claims.claim_cost), 0), 2) as total_claim_cost,
round(coalesce(sum(valid_warranty_claims.approved_amount), 0), 2) as total_approved_cost
from vehicles
left join valid_warranty_claims on valid_warranty_claims.vehicle_id = vehicles.vehicle_id
group by vehicles.model
order by claims_per_100_vehicles desc;
""", "kpi2_claims_by_model")

kpi3 = run_query("""
select issue_category, 
count(claim_id) as no_of_claims,
round(avg(claim_cost),2) as avg_claim_cost,
round(sum(claim_cost),2) as total_claim_cost
from valid_warranty_claims
group by issue_category
order by no_of_claims desc;
""", "kpi3_claims_by_issue_category")

kpi4 = run_query("""
select claim_status,
count(claim_id) as no_of_claims
from valid_warranty_claims
group by claim_status
order by no_of_claims desc;
""", "kpi4_claim_status_breakdown")

kpi5 = run_query("""
select issue_category, 
count(claim_id) as total_claims,
sum(case when claim_status = 'Rejected' then 1 else 0 end) as rejected_claims,
round(100.0 * sum(case when claim_status = 'Rejected' then 1 else 0 end) / count(claim_id), 2) as rejection_rate
from valid_warranty_claims
group by issue_category
order by rejection_rate desc;
""", "kpi5_rejection_rate_by_issue")

kpi6 = run_query("""
select strftime('%Y-%m', claim_date) as month,
count(claim_id) as no_of_claims,
round(sum(coalesce(approved_amount,0)),2) AS total_approved_amount
from valid_warranty_claims
group by month
order by month;
""", "kpi6_monthly_claim_trend")

kpi7 = run_query("""
select vehicles.city as city,
vehicles.region as region,
count(claim_id) as no_of_claims,
round(avg(valid_warranty_claims.claim_cost),2) as avg_claim_cost,
round(sum(valid_warranty_claims.claim_cost),2) as total_claim_cost
from valid_warranty_claims
join vehicles on vehicles.vehicle_id=valid_warranty_claims.vehicle_id
group by city,region
order by no_of_claims desc;
""", "kpi7_claims_by_region_city")

kpi8 = run_query("""
select issue_category,
round(avg(resolution_days),1) as avg_resolution_days
from valid_warranty_claims
group by issue_category
order by avg_resolution_days desc;
""", "kpi8_avg_resolution_by_issue")

kpi9 = run_query("""
select service_type,
count(service_id) as no_of_service_visits,
round(avg(service_cost),2) as avg_service_cost,
round(sum(service_cost),2) as total_service_cost
from valid_service_visits
group by service_type
order by no_of_service_visits desc;
""", "kpi9_service_type_breakdown")

kpi10 = run_query("""
select vehicles.model as model,
round(avg(valid_service_visits.service_cost),2) as avg_service_cost
from valid_service_visits
join vehicles on valid_service_visits.vehicle_id=vehicles.vehicle_id
group by model
order by avg_service_cost desc;
""", "kpi10_avg_service_cost_by_model")

kpi11 = run_query("""
WITH svc AS (
  SELECT vehicle_id, SUM(service_cost) AS total_service_cost
  FROM valid_service_visits
  GROUP BY vehicle_id
),
clm AS (
  SELECT vehicle_id, SUM(claim_cost) AS total_claim_cost
  FROM valid_warranty_claims
  GROUP BY vehicle_id
)
SELECT v.vehicle_id,
       COALESCE(svc.total_service_cost, 0) AS total_service_cost,
       COALESCE(clm.total_claim_cost, 0) AS total_claim_cost
FROM vehicles v
LEFT JOIN svc ON v.vehicle_id = svc.vehicle_id
LEFT JOIN clm ON v.vehicle_id = clm.vehicle_id
ORDER BY total_claim_cost DESC;
""", "kpi11_service_vs_claim_cost_per_vehicle")

kpi12 = run_query("""
SELECT ROUND(100.0 * SUM(CASE WHEN claim_status='Approved' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate
FROM valid_warranty_claims;
""", "kpi12_overall_approval_rate")

kpi13 = run_query("""
SELECT v.model,
       ROUND(SUM(COALESCE(w.approved_amount,0)) / COUNT(DISTINCT v.vehicle_id), 2) AS approved_cost
FROM vehicles v
LEFT JOIN valid_warranty_claims w ON v.vehicle_id = w.vehicle_id
GROUP BY v.model
ORDER BY approved_cost DESC;
""", "kpi13_warranty_cost_per_vehicle_by_model")
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
total_claim_cost = kpi1.loc[0, "total_claim_cost"]
total_approved_cost = kpi1.loc[0, "total_approved_cost"]
approval_rate = kpi12.loc[0, "approval_rate"]
print("\nExecutive KPIs")
print("Total claim cost:", total_claim_cost)
print("Total approved cost:", total_approved_cost)
print("Approval rate:", approval_rate)
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
#Charts
# ------------------------------------------------------------------------

# 1. Monthly claim volume
plt.figure(figsize=(10, 5))
plt.plot(kpi6["month"], kpi6["no_of_claims"], marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Claim Volume")
plt.xlabel("Month")
plt.ylabel("No. of Claims")
plt.tight_layout()
plt.savefig(f"{output_dir}/01_monthly_claim_volume.png")
plt.close()

# 2. Monthly approved amount
plt.figure(figsize=(10, 5))
plt.plot(kpi6["month"], kpi6["total_approved_amount"], marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Approved Warranty Amount")
plt.xlabel("Month")
plt.ylabel("Approved Amount")
plt.tight_layout()
plt.savefig(f"{output_dir}/02_monthly_approved_amount.png")
plt.close()

# 3. Claims by issue category
plt.figure(figsize=(8, 5))
plt.bar(kpi3["issue_category"], kpi3["no_of_claims"])
plt.xticks(rotation=45)
plt.title("Claims by Issue Category")
plt.xlabel("Issue Category")
plt.ylabel("No. of Claims")
plt.tight_layout()
plt.savefig(f"{output_dir}/03_claims_by_issue_category.png")
plt.close()

# 4. Rejection rate by issue category
plt.figure(figsize=(8, 5))
plt.bar(kpi5["issue_category"], kpi5["rejection_rate"])
plt.xticks(rotation=45)
plt.title("Rejection Rate by Issue Category")
plt.xlabel("Issue Category")
plt.ylabel("Rejection Rate(%)")
plt.tight_layout()
plt.savefig(f"{output_dir}/04_rejection_rate_by_issue_category.png")
plt.close()

# 5. Average resolution days by issue category
plt.figure(figsize=(8, 5))
plt.bar(kpi8["issue_category"], kpi8["avg_resolution_days"])
plt.xticks(rotation=45)
plt.title("Average Resolution Days by Issue Category")
plt.xlabel("Issue Category")
plt.ylabel("Average Resolution Days")
plt.tight_layout()
plt.savefig(f"{output_dir}/05_avg_resolution_days_by_issue_category.png")
plt.close()

# 6. Claims per 100 vehicles by model
plt.figure(figsize=(8, 5))
plt.bar(kpi2["model"], kpi2["claims_per_100_vehicles"])
plt.xticks(rotation=45)
plt.title("Claims per 100 Vehicles by Model")
plt.xlabel("Model")
plt.ylabel("Claims per 100 Vehicles")
plt.tight_layout()
plt.savefig(f"{output_dir}/06_claims_per_100_vehicles_by_model.png")
plt.close()

# 7. Service visits by type
plt.figure(figsize=(8, 5))
plt.bar(kpi9["service_type"], kpi9["no_of_service_visits"])
plt.xticks(rotation=45)
plt.title("Service Visits by Type")
plt.xlabel("Service Type")
plt.ylabel("No. of Visits")
plt.tight_layout()
plt.savefig(f"{output_dir}/07_service_visits_by_type.png")
plt.close()

# 8. Average service cost by model
plt.figure(figsize=(8, 5))
plt.bar(kpi10["model"], kpi10["avg_service_cost"])
plt.xticks(rotation=45)
plt.title("Average Service Cost by Model")
plt.xlabel("Model")
plt.ylabel("Average Service Cost")
plt.tight_layout()
plt.savefig(f"{output_dir}/08_avg_service_cost_by_model.png")
plt.close()

# 9. Claims by region
region_df = (
    kpi7.groupby("region", as_index=False)["no_of_claims"]
    .sum()
    .sort_values("no_of_claims", ascending=False)
)

plt.figure(figsize=(8, 5))
plt.bar(region_df["region"], region_df["no_of_claims"])
plt.title("Claims by Region")
plt.xlabel("Region")
plt.ylabel("No. of Claims")
plt.tight_layout()
plt.savefig(f"{output_dir}/09_claims_by_region.png")
plt.close()

# 10. Warranty cost per vehicle by model
plt.figure(figsize=(8, 5))
plt.bar(kpi13["model"], kpi13["approved_cost"])
plt.xticks(rotation=45)
plt.title("Approved Warranty Cost per Vehicle by Model")
plt.xlabel("Model")
plt.ylabel("Approved Cost per Vehicle")
plt.tight_layout()
plt.savefig(f"{output_dir}/10_warranty_cost_per_vehicle_by_model.png")
plt.close()

conn.close()
print("\n*********************************************(****************************")
print("\n(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ all done! charts have been saved to /outputs/ ✧ﾟ･: *ヽ(◕ヮ◕ヽ)")
print("\n**************************************************************************")