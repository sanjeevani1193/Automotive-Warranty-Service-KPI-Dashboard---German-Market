-- ------------------------------------------------------------
-- Cleaned warranty claims: only claims within warranty period
DROP VIEW IF EXISTS valid_warranty_claims;
CREATE VIEW valid_warranty_claims AS
SELECT wc.*
FROM warranty_claims wc
JOIN vehicles v
  ON wc.vehicle_id = v.vehicle_id
WHERE wc.claim_date <= v.warranty_end_date;
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- Cleaned service visits: only visits within warranty period
DROP VIEW IF EXISTS valid_service_visits;
CREATE VIEW valid_service_visits AS
SELECT sv.*
FROM service_visits sv
JOIN vehicles v
  ON sv.vehicle_id = v.vehicle_id
WHERE sv.service_date <= v.warranty_end_date;
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- Data quality check: claims outside warranty
SELECT COUNT(*) AS claims_outside_warranty
FROM warranty_claims wc
JOIN vehicles v
  ON wc.vehicle_id = v.vehicle_id
WHERE wc.claim_date > v.warranty_end_date;
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- Data quality check: service visits outside warranty
SELECT COUNT(*) AS services_outside_warranty
FROM service_visits sv
JOIN vehicles v
  ON sv.vehicle_id = v.vehicle_id
WHERE sv.service_date > v.warranty_end_date;
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- KPI 1: Total claimed vs total approved cost
-- ------------------------------------------------------------
select sum(claim_cost) as total_claim_cost,
sum(approved_amount) as total_approved_cost
from valid_warranty_claims;

-- ------------------------------------------------------------
-- KPI 2: Claims by model — volume and avg cost
-- ------------------------------------------------------------
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

-- ---------------------------------------------------------------
-- KPI 3: Claims by issue category — volume, avg cost, total cost
-- ---------------------------------------------------------------
select issue_category, 
count(claim_id) as no_of_claims,
round(avg(claim_cost),2) as avg_claim_cost,
round(sum(claim_cost),2) as total_claim_cost
from valid_warranty_claims
group by issue_category
order by no_of_claims desc;

-- ------------------------------------------------------------------------
-- KPI 4: Claim  status breakdown — how many approved / rejected / pending
-- ------------------------------------------------------------------------
select claim_status,
count(claim_id) as no_of_claims
from valid_warranty_claims
group by claim_status
order by no_of_claims desc;

-- ---------------------------------------------------------------
-- KPI 5: Rejection rate by issue category
-- ---------------------------------------------------------------
select issue_category, 
count(claim_id) as total_claims,
sum(case when claim_status = 'Rejected' then 1 else 0 end) as rejected_claims,
round(100.0 * sum(case when claim_status = 'Rejected' then 1 else 0 end) / count(claim_id), 2) as rejection_rate
from valid_warranty_claims
group by issue_category
order by rejection_rate desc;

-- ---------------------------------------------------------------
-- KPI 6: monthly claim volume, total approved amount
-- ---------------------------------------------------------------
select strftime('%Y-%m', claim_date) as month,
count(claim_id) as no_of_claims,
round(sum(coalesce(approved_amount,0)),2) AS total_approved_amount
from valid_warranty_claims
group by month
order by month;

-- ---------------------------------------------------------------
-- KPI 7: claims by region and city
-- ---------------------------------------------------------------
select vehicles.city as city,
vehicles.region as region,
count(claim_id) as no_of_claims,
round(avg(valid_warranty_claims.claim_cost),2) as avg_claim_cost,
round(sum(valid_warranty_claims.claim_cost),2) as total_claim_cost
from valid_warranty_claims
join vehicles on vehicles.vehicle_id=valid_warranty_claims.vehicle_id
group by city,region
order by no_of_claims desc;

-- ---------------------------------------------------------------
-- KPI 8: avg resolution days by issue category
-- ---------------------------------------------------------------
select issue_category,
round(avg(resolution_days),1) as avg_resolution_days
from valid_warranty_claims
group by issue_category
order by avg_resolution_days desc;

-- ---------------------------------------------------------------
-- KPI 9: service type breakdown — count, avg cost, total cost
-- ---------------------------------------------------------------
select service_type,
count(service_id) as no_of_service_visits,
round(avg(service_cost),2) as avg_service_cost,
round(sum(service_cost),2) as total_service_cost
from valid_service_visits
group by service_type
order by no_of_service_visits desc;

-- ---------------------------------------------------------------
-- KPI 10: avg service cost by model
-- ---------------------------------------------------------------
select vehicles.model as model,
round(avg(valid_service_visits.service_cost),2) as avg_service_cost
from valid_service_visits
join vehicles on valid_service_visits.vehicle_id=vehicles.vehicle_id
group by model
order by avg_service_cost desc;

-- ---------------------------------------------------------------
-- KPI 11: total service cost vs total claim cost per vehicle (join all 3 tables)
-- ---------------------------------------------------------------
-- select vehicles.vehicle_id,
-- round(sum(distinct service_visits.service_cost),2) as total_service_cost,
-- round(sum(distinct warranty_claims.claim_cost),2) as total_claim_cost
-- from vehicles
-- join service_visits on service_visits.vehicle_id=vehicles.vehicle_id
-- join warranty_claims on warranty_claims.vehicle_id=vehicles.vehicle_id
-- group by vehicles.vehicle_id
-- order by total_claim_cost;
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


-- ---------------------------------------------------------------
-- KPI 12: overall approval rate
-- ---------------------------------------------------------------
SELECT 
  ROUND(100.0 * SUM(CASE WHEN claim_status='Approved' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate
FROM valid_warranty_claims;

-- ---------------------------------------------------------------
-- KPI 13: Warranty cost per vehicle by model
-- ---------------------------------------------------------------
SELECT v.model,
       ROUND(SUM(COALESCE(w.approved_amount,0)) / COUNT(DISTINCT v.vehicle_id), 2) AS approved_cost
FROM vehicles v
LEFT JOIN valid_warranty_claims w ON v.vehicle_id = w.vehicle_id
GROUP BY v.model
ORDER BY approved_cost DESC;