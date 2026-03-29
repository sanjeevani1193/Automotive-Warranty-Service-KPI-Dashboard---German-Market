# Automotive Warranty & Service Analysis for German Market

## Project Overview

In this project, I have analyzed synthetic automotive warranty claim and service visit data for an automotive company like KIA in the German market using SQL, SQLite, Python, and Jupyter Notebook. 

I was able to identify warranty cost drivers, claim patterns, service cost behavior, and operational trends across vehicle models, issue categories, service types, and regions. This project combines multi-table automotive data into a simple end-to-end analytics workflow -> from data generation and SQL-based KPI definitions to Python-based visualizations and reporting.

## Motivation

Warranty and after-sales performance are important areas in the automotive industry since they directly affect cost, customer satisfaction, service operations, and product quality monitoring.

This project was built to simulate a realistic analytics use-case scenario in which vehicle master data, service visits, and warranty claims data are integrated to answer questions such as:

- Which issue categories drive the highest warranty cost?
- Which vehicle models show the highest relative warranty burden?
- How do claim approval and rejection patterns differ?
- Are there regional differences in claim concentration?
- Which service types and models drive higher service costs?

## Dataset

The project uses three synthetic datasets generated in Python:

- **vehicles**: vehicle master data including vehicle ID, customer ID, model, model year, fuel type, purchase date, city, region, and warranty end date
- **service_visits**: service history including service ID, vehicle ID, service date, service type, resolution days, and service cost
- **warranty_claims**: warranty claim records including claim ID, vehicle ID, claim date, issue category, claim status, claim cost, approved amount, and resolution days

This data was generated to simulate a realistic automotive after-sales scenario for KIA's German market and then loaded into SQLite for analysis.

## Methodology

The project follows this workflow: -

1. **Synthetic data generation**  
   Python was used to generate vehicle, service, and warranty claim data.

2. **Database loading**  
   The CSV files were loaded into a SQLite database, and indexes were created to support query performance. 

3. **Data quality validation**  
   Raw data records were checked for claims and service visits occurring outside the warranty period.

4. **Cleaned analytical views**  
   SQL views were created to keep only valid in-warranty claims and service visits:
   - `valid_warranty_claims`
   - `valid_service_visits`

5. **KPI analysis**  
   SQL queries were used to calculate KPIs such as:
   - total claimed vs approved warranty cost
   - claims by model
   - claims by issue category
   - claim status distribution
   - rejection rate by issue category
   - monthly claim volume and approved amount
   - regional claim concentration
   - average resolution days
   - service type cost breakdown
   - average service cost by model
   - approved warranty cost per vehicle by model

6. **Visualization and reporting**  
   Python and Matplotlib were used to generate charts, while a Jupyter notebook was used to present the step-by-step analysis.

## Key Findings and Observations

- Some raw records fell outside the warranty period, so cleaned SQL views were created to ensure that only valid in-warranty activity was analyzed.

- Warranty burden is not evenly distributed across issue categories; a limited number of categories account for a relatively large share of claims and cost.

- Claim approval and rejection patterns vary by issue category, suggesting differences in policy fit, documentation, or issue severity.

- Resolution time also differs across issue categories, indicating potential operational bottlenecks.

- Model comparisons are more informative when normalized. Metrics such as claims per 100 vehicles and approved warranty cost per vehicle provide a more realistic view than raw claim counts alone.

- Service activity varies across service types and models, highlighting the value of combining service and warranty analysis rather than treating them separately.

- Regional differences in claim concentration may point to differences in vehicle mix, usage patterns, or service processes.

## How to Reproduce

1. Clone the repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
3. Generate the synthetic datasets:
    python generate_data.py
4. Load the CSV files into SQLite:
    python load_to_sqlite.py
5. Run the main analysis script:
    python analysis.py
6. Open 'analysis.ipynb' to review the analysis interactively and step by step.


## Difference between `analysis.py` and `analysis.ipynb`
```markdown
## analysis.py vs analysis.ipynb

Both files use the same project logic, but they have different purposes:
- `analysis.py`    -> automation and reproducibility
- `analysis.ipynb` -> explanation, presentation, and portfolio display

## Author
Sanjeevani Rajpurohit