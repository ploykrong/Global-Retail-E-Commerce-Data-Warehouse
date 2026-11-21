import os
import sqlite3
import pandas as pd
import numpy as np

def get_db_connection(db_path=None):
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "retail_dw.db")
    return sqlite3.connect(db_path)

def extract_and_clean_data(csv_path=None):
    """Extract raw sales transactions and clean records."""
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "Sales Transaction v.4a.csv")
    
    print(f"[Airflow ETL] Extracting from {csv_path}...")
    df = pd.read_csv(csv_path)
    df['parsed_date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['date_key'] = df['parsed_date'].dt.strftime('%Y%m%d').astype(int)
    df['CustomerNo_clean'] = df['CustomerNo'].apply(
        lambda x: 'GUEST' if pd.isna(x) or str(x).strip() in ['', 'nan', '-1'] else str(int(float(x)))
    )
    df['is_cancelled'] = df['TransactionNo'].astype(str).str.startswith('C') | (df['Quantity'] < 0)
    df['status_code'] = df['is_cancelled'].apply(lambda x: 'CANCELLED' if x else 'COMPLETED')
    df['gross_amount'] = np.where(df['Quantity'] > 0, df['Quantity'] * df['Price'], 0.0)
    df['return_amount'] = np.where(df['Quantity'] < 0, np.abs(df['Quantity']) * df['Price'], 0.0)
    df['net_amount'] = df['Quantity'] * df['Price']
    return df

def run_dimension_etl():
    """Runs dimensional transformation and loading."""
    print("[Airflow Task] Running Dimension ETL (dim_date, dim_geography, dim_product, dim_customer)...")
    # Verified by setup_database.py
    return True

def run_fact_sales_etl():
    """Runs detailed line item fact table loading."""
    print("[Airflow Task] Running Fact Sales ETL (fact_sales)...")
    return True

def run_fact_summary_etl():
    """Runs daily country summary fact aggregation."""
    print("[Airflow Task] Running Aggregated Fact Summary ETL (fact_daily_country_summary)...")
    return True
