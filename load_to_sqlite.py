import sqlite3
import pandas as pd
import os

DB_PATH = "warranty_kpi.db"

TABLES = {
    "vehicles":        "data/vehicles.csv",
    "service_visits":  "data/service_visits.csv",
    "warranty_claims": "data/warranty_claims.csv",
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_sv_vehicle ON service_visits(vehicle_id);",
    "CREATE INDEX IF NOT EXISTS idx_wc_vehicle ON warranty_claims(vehicle_id);",
    "CREATE INDEX IF NOT EXISTS idx_wc_date    ON warranty_claims(claim_date);",
    "CREATE INDEX IF NOT EXISTS idx_wc_status  ON warranty_claims(claim_status);",
]

def load():
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to {DB_PATH}")

    for table_name, filepath in TABLES.items():
        df = pd.read_csv(filepath)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  ✓ Loaded {table_name} — {len(df):,} rows")

    print("\nCreating indexes...")
    for stmt in INDEXES:
        conn.execute(stmt)
    conn.commit()
    print("  ✓ Indexes created")

    print("\nRow counts via SQL:")
    for table in TABLES:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:20s} → {count:,} rows")

    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")

if __name__ == "__main__":
    load()