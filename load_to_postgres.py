import os
import time
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "retail_dw.db")

PG_HOST = os.getenv("DB_HOST", "localhost")
PG_PORT = int(os.getenv("DB_PORT", "5432"))
PG_USER = os.getenv("DB_USER", "airflow")
PG_PASS = os.getenv("DB_PASS", "airflow")
PG_DBNAME = "retail_dw"

def main():
    print("=" * 70)
    print("Connecting to PostgreSQL to initialize 'retail_dw' for pgAdmin...")
    print("=" * 70)
    t0 = time.time()

    # 1. Connect to postgres default database and create retail_dw if not exists
    conn_default = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname="postgres"
    )
    conn_default.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur_default = conn_default.cursor()

    cur_default.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (PG_DBNAME,))
    if not cur_default.fetchone():
        print(f"Creating database '{PG_DBNAME}' in PostgreSQL...")
        cur_default.execute(f"CREATE DATABASE {PG_DBNAME} OWNER {PG_USER};")
        cur_default.execute(f"GRANT ALL PRIVILEGES ON DATABASE {PG_DBNAME} TO {PG_USER};")
    else:
        print(f"Database '{PG_DBNAME}' already exists in PostgreSQL.")
    
    cur_default.close()
    conn_default.close()

    # 2. Read tables from SQLite retail_dw.db
    print(f"Reading tables from SQLite: {SQLITE_DB_PATH}...")
    conn_sqlite = sqlite3.connect(SQLITE_DB_PATH)

    tables = [
        "dim_date",
        "dim_customer",
        "dim_product",
        "dim_geography",
        "dim_transaction_status",
        "fact_sales",
        "fact_daily_country_summary"
    ]

    # Create SQLAlchemy engine for PostgreSQL
    pg_engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}")

    # Clean any partial fact rows
    conn_pg_clean = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DBNAME)
    conn_pg_clean.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn_pg_clean.cursor() as cur_clean:
        cur_clean.execute("TRUNCATE TABLE fact_daily_country_summary, fact_sales, dim_customer, dim_product, dim_geography CASCADE;")
    conn_pg_clean.close()

    # Transfer each table
    for tbl in tables:
        t_sub = time.time()
        print(f"Loading '{tbl}' into PostgreSQL {PG_DBNAME}...")
        df_tbl = pd.read_sql_query(f"SELECT * FROM {tbl};", conn_sqlite)
        if tbl in ["dim_date", "dim_transaction_status"]:
            # Already pre-seeded by DDL script
            print(f"  -> '{tbl}' already seeded by DDL.")
            continue
        df_tbl.to_sql(tbl, pg_engine, if_exists='append', index=False, chunksize=50000, method='multi')
        print(f"  -> '{tbl}' loaded ({len(df_tbl):,} rows in {time.time()-t_sub:.2f}s)")

    conn_sqlite.close()

    # 3. Create Indexes in PostgreSQL
    print("Creating B-Tree Indexes in PostgreSQL for high performance...")
    conn_pg = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DBNAME
    )
    cur_pg = conn_pg.cursor()
    cur_pg.execute("""
        CREATE INDEX IF NOT EXISTS idx_pg_fs_date ON fact_sales(date_key);
        CREATE INDEX IF NOT EXISTS idx_pg_fs_cust ON fact_sales(customer_key);
        CREATE INDEX IF NOT EXISTS idx_pg_fs_prod ON fact_sales(product_key);
        CREATE INDEX IF NOT EXISTS idx_pg_fs_geo ON fact_sales(geography_key);
        CREATE INDEX IF NOT EXISTS idx_pg_fs_status ON fact_sales(status_key);
        CREATE INDEX IF NOT EXISTS idx_pg_fs_tx ON fact_sales(transaction_no);
        CREATE INDEX IF NOT EXISTS idx_pg_fdc_date_geo ON fact_daily_country_summary(date_key, geography_key);
    """)
    conn_pg.commit()
    cur_pg.close()
    conn_pg.close()

    elapsed = time.time() - t0
    print("=" * 70)
    print(f"PostgreSQL retail_dw database loaded successfully in {elapsed:.2f} seconds!")
    print(f"You can now refresh and view 'retail_dw' in pgAdmin 4 at http://localhost:5050")
    print("=" * 70)

if __name__ == '__main__':
    main()
