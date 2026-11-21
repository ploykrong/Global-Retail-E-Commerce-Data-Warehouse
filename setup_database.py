import os
import sys
import time
import sqlite3
import datetime
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "Sales Transaction v.4a.csv")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "retail_dw.db")

# Keyword-based product categorizer
def categorize_product(name):
    if not isinstance(name, str):
        return 'Gifts & General Merchandise'
    n = name.upper()
    if any(k in n for k in ['CHRISTMAS', 'HOLIDAY', 'EASTER', 'HALLOWEEN', 'XMAS', 'DECORATION', 'WREATH', 'BUNTING', 'T-LIGHT', 'CANDLE', 'RIBBON']):
        return 'Holiday & Seasonal'
    elif any(k in n for k in ['BAG', 'TOTE', 'LUGGAGE', 'PURSE', 'BACKPACK', 'SHOPPER', 'WALLET']):
        return 'Bags & Luggage'
    elif any(k in n for k in ['BOX', 'TIN', 'STORAGE', 'DRAWER', 'BASKET', 'CHEST', 'CASE', 'JAR']):
        return 'Home Storage & Containers'
    elif any(k in n for k in ['MUG', 'CUP', 'BOWL', 'PLATE', 'TEAPOT', 'KITCHEN', 'BAKE', 'CUTLERY', 'GLASS', 'DISH', 'BOTTLE', 'SPOON', 'FORK', 'LUNCH']):
        return 'Kitchen & Dining'
    elif any(k in n for k in ['SIGN', 'CLOCK', 'FRAME', 'MIRROR', 'VINTAGE', 'HEART', 'WALL', 'HANGER', 'HOOK', 'CUSHION', 'DOORMAT']):
        return 'Home Decor & Furnishing'
    elif any(k in n for k in ['TOY', 'GAME', 'MARBLES', 'DOLL', 'CHILD', 'BABY', 'PUZZLE', 'PLAY', 'LOLA']):
        return 'Toys & Children'
    elif any(k in n for k in ['PEN', 'PENCIL', 'NOTEBOOK', 'CARD', 'STICKER', 'PAPER', 'TAPE', 'STAMP', 'WRAP', 'BOOK']):
        return 'Stationery & Papercraft'
    elif any(k in n for k in ['SOAP', 'LAVENDER', 'BATH', 'LIP', 'CREAM', 'TOWEL']):
        return 'Bath & Beauty'
    else:
        return 'Gifts & General Merchandise'

# Region classification
def map_region(country):
    if not isinstance(country, str):
        return ('Other', 'International')
    c = country.strip()
    if c == 'United Kingdom':
        return ('United Kingdom', 'Domestic')
    elif c in ['Germany', 'France', 'Belgium', 'Netherlands', 'Spain', 'Italy', 'Portugal', 'Austria', 
               'Switzerland', 'EIRE', 'Channel Islands', 'Cyprus', 'Czech Republic', 'Denmark', 
               'Finland', 'Greece', 'Iceland', 'Lithuania', 'Malta', 'Norway', 'Poland', 'Sweden', 'European Community']:
        return ('Western & Northern Europe', 'International')
    elif c in ['Australia', 'Japan', 'Singapore', 'Hong Kong']:
        return ('Asia-Pacific', 'International')
    elif c in ['USA', 'Canada', 'Brazil']:
        return ('Americas', 'International')
    elif c in ['Bahrain', 'Israel', 'Lebanon', 'Saudi Arabia', 'United Arab Emirates']:
        return ('Middle East', 'International')
    elif c in ['RSA']:
        return ('Africa', 'International')
    else:
        return ('Other / Unspecified', 'International')

def build_data_warehouse():
    print("=" * 70)
    print("Starting Retail Data Warehouse ETL & Database Setup...")
    print("=" * 70)
    t0 = time.time()

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Source file not found at: {CSV_PATH}")

    print(f"[1/6] Extracting raw data from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    raw_count = len(df)
    print(f"      -> Successfully extracted {raw_count:,} records.")

    # -------------------------------------------------------------
    # Data Cleaning & Transformation
    # -------------------------------------------------------------
    print("[2/6] Transforming and cleaning data...")
    
    # 1. Parse Date
    df['parsed_date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['date_key'] = df['parsed_date'].dt.strftime('%Y%m%d').astype(int)
    
    # 2. Customer Cleaning
    df['CustomerNo_clean'] = df['CustomerNo'].apply(
        lambda x: 'GUEST' if pd.isna(x) or str(x).strip() in ['', 'nan', '-1'] else str(int(float(x)))
    )

    # 3. Transaction Status & Quantities
    df['is_cancelled'] = df['TransactionNo'].astype(str).str.startswith('C') | (df['Quantity'] < 0)
    df['status_code'] = df['is_cancelled'].apply(lambda x: 'CANCELLED' if x else 'COMPLETED')
    
    df['gross_amount'] = np.where(df['Quantity'] > 0, df['Quantity'] * df['Price'], 0.0)
    df['return_amount'] = np.where(df['Quantity'] < 0, np.abs(df['Quantity']) * df['Price'], 0.0)
    df['net_amount'] = df['Quantity'] * df['Price']

    # -------------------------------------------------------------
    # Dimension 1: dim_date
    # -------------------------------------------------------------
    print("[3/6] Generating Dimensions...")
    min_date = df['parsed_date'].min()
    max_date = df['parsed_date'].max()
    print(f"      -> Date range detected: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

    date_series = pd.date_range(start='2018-01-01', end='2021-12-31', freq='D')
    dim_date = pd.DataFrame({
        'date_key': date_series.strftime('%Y%m%d').astype(int),
        'full_date': date_series.strftime('%Y-%m-%d'),
        'day': date_series.day,
        'month': date_series.month,
        'month_name_en': date_series.strftime('%B'),
        'quarter': date_series.quarter,
        'year': date_series.year,
        'day_of_week': date_series.dayofweek + 1, # 1=Mon, 7=Sun
        'day_name_en': date_series.strftime('%A'),
        'is_weekend': (date_series.dayofweek >= 5).astype(int),
        'season': date_series.month.map(lambda m: 'Winter' if m in [12, 1, 2] else ('Spring' if m in [3, 4, 5] else ('Summer' if m in [6, 7, 8] else 'Autumn')))
    })

    # -------------------------------------------------------------
    # Dimension 2: dim_geography
    # -------------------------------------------------------------
    unique_countries = sorted(df['Country'].dropna().unique())
    geo_records = []
    for idx, c in enumerate(unique_countries, 1):
        region, mkt_type = map_region(c)
        geo_records.append({
            'geography_key': idx,
            'country_name': c,
            'region': region,
            'market_type': mkt_type,
            'currency_code': 'GBP'
        })
    dim_geography = pd.DataFrame(geo_records)
    geo_lookup = dict(zip(dim_geography['country_name'], dim_geography['geography_key']))

    # -------------------------------------------------------------
    # Dimension 3: dim_product
    # -------------------------------------------------------------
    prod_grouped = df.groupby('ProductNo').agg(
        product_name=('ProductName', 'first'),
        avg_unit_price=('Price', 'mean')
    ).reset_index()

    prod_grouped['product_key'] = range(1, len(prod_grouped) + 1)
    prod_grouped['category_name'] = prod_grouped['product_name'].apply(categorize_product)
    prod_grouped['price_tier'] = prod_grouped['avg_unit_price'].apply(
        lambda p: 'Budget (<£10)' if p < 10 else ('Mid-range (£10-25)' if p <= 25 else ('Premium (£25-50)' if p <= 50 else 'Luxury (>£50)'))
    )
    dim_product = prod_grouped[['product_key', 'ProductNo', 'product_name', 'category_name', 'price_tier', 'avg_unit_price']].rename(
        columns={'ProductNo': 'product_no'}
    )
    prod_lookup = dict(zip(dim_product['product_no'], dim_product['product_key']))

    # -------------------------------------------------------------
    # Dimension 4: dim_customer (with RFM Profiling)
    # -------------------------------------------------------------
    snapshot_date = df['parsed_date'].max() + pd.Timedelta(days=1)
    cust_agg = df.groupby('CustomerNo_clean').agg(
        country=('Country', 'first'),
        total_orders=('TransactionNo', 'nunique'),
        total_spend=('net_amount', 'sum'),
        first_purchase=('parsed_date', 'min'),
        last_purchase=('parsed_date', 'max')
    ).reset_index()

    cust_agg['recency_days'] = (snapshot_date - cust_agg['last_purchase']).dt.days

    # Customer Segmentation rules
    def segment_customer(row):
        if row['CustomerNo_clean'] == 'GUEST':
            return 'Guest / Unregistered'
        r = row['recency_days']
        f = row['total_orders']
        m = row['total_spend']
        if m > 5000 and f >= 5 and r <= 60:
            return 'VIP Champions'
        elif f >= 4 and r <= 90:
            return 'Loyal Customers'
        elif r <= 45 and f <= 3:
            return 'Potential Loyalists'
        elif r > 120 and m > 1000:
            return 'At Risk Customers'
        elif r > 180:
            return 'Lost Customers'
        else:
            return 'Regular Customers'

    cust_agg['customer_segment'] = cust_agg.apply(segment_customer, axis=1)
    cust_agg['customer_key'] = range(1, len(cust_agg) + 1)
    dim_customer = cust_agg[[
        'customer_key', 'CustomerNo_clean', 'country', 'total_orders', 
        'total_spend', 'first_purchase', 'last_purchase', 'recency_days', 'customer_segment'
    ]].rename(
        columns={
            'CustomerNo_clean': 'customer_no',
            'first_purchase': 'first_purchase_date',
            'last_purchase': 'last_purchase_date'
        }
    )
    dim_customer['first_purchase_date'] = dim_customer['first_purchase_date'].dt.strftime('%Y-%m-%d')
    dim_customer['last_purchase_date'] = dim_customer['last_purchase_date'].dt.strftime('%Y-%m-%d')
    cust_lookup = dict(zip(dim_customer['customer_no'], dim_customer['customer_key']))

    # -------------------------------------------------------------
    # Dimension 5: dim_transaction_status
    # -------------------------------------------------------------
    dim_transaction_status = pd.DataFrame([
        {'status_key': 1, 'status_code': 'COMPLETED', 'status_name': 'Completed', 'is_return': 0},
        {'status_key': 2, 'status_code': 'CANCELLED', 'status_name': 'Cancelled / Returned', 'is_return': 1}
    ])
    status_lookup = {'COMPLETED': 1, 'CANCELLED': 2}

    # -------------------------------------------------------------
    # Fact 1: fact_sales
    # -------------------------------------------------------------
    print("[4/6] Building Fact Table: fact_sales...")
    df['customer_key'] = df['CustomerNo_clean'].map(cust_lookup)
    df['product_key'] = df['ProductNo'].map(prod_lookup)
    df['geography_key'] = df['Country'].map(geo_lookup)
    df['status_key'] = df['status_code'].map(status_lookup)
    df['sales_key'] = range(1, len(df) + 1)

    fact_sales = df[[
        'sales_key', 'TransactionNo', 'date_key', 'customer_key', 
        'product_key', 'geography_key', 'status_key', 
        'Quantity', 'Price', 'gross_amount', 'return_amount', 'net_amount'
    ]].rename(columns={
        'TransactionNo': 'transaction_no',
        'Quantity': 'quantity',
        'Price': 'unit_price'
    })

    # -------------------------------------------------------------
    # Fact 2: fact_daily_country_summary (Aggregated OLAP)
    # -------------------------------------------------------------
    print("[5/6] Building Aggregated Fact Table: fact_daily_country_summary...")
    daily_summary = df.groupby(['date_key', 'geography_key']).agg(
        total_orders=('TransactionNo', 'nunique'),
        total_units_sold=('Quantity', lambda x: x[x > 0].sum()),
        total_units_returned=('Quantity', lambda x: np.abs(x[x < 0].sum())),
        gross_revenue=('gross_amount', 'sum'),
        return_loss=('return_amount', 'sum'),
        net_revenue=('net_amount', 'sum'),
        unique_customers=('CustomerNo_clean', 'nunique')
    ).reset_index()
    daily_summary['summary_key'] = range(1, len(daily_summary) + 1)

    # -------------------------------------------------------------
    # Loading into SQLite Database
    # -------------------------------------------------------------
    print(f"[6/6] Persisting tables to SQLite Data Warehouse at: {SQLITE_DB_PATH}")
    if os.path.exists(SQLITE_DB_PATH):
        try:
            os.remove(SQLITE_DB_PATH)
        except Exception:
            pass

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    # Create tables with explicit schema and constraints
    cur.execute("""
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT UNIQUE,
            day INTEGER,
            month INTEGER,
            month_name_en TEXT,
            quarter INTEGER,
            year INTEGER,
            day_of_week INTEGER,
            day_name_en TEXT,
            is_weekend INTEGER,
            season TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE dim_customer (
            customer_key INTEGER PRIMARY KEY,
            customer_no TEXT UNIQUE,
            country TEXT,
            total_orders INTEGER,
            total_spend REAL,
            first_purchase_date TEXT,
            last_purchase_date TEXT,
            recency_days INTEGER,
            customer_segment TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE dim_product (
            product_key INTEGER PRIMARY KEY,
            product_no TEXT UNIQUE,
            product_name TEXT,
            category_name TEXT,
            price_tier TEXT,
            avg_unit_price REAL
        );
    """)

    cur.execute("""
        CREATE TABLE dim_geography (
            geography_key INTEGER PRIMARY KEY,
            country_name TEXT UNIQUE,
            region TEXT,
            market_type TEXT,
            currency_code TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE dim_transaction_status (
            status_key INTEGER PRIMARY KEY,
            status_code TEXT UNIQUE,
            status_name TEXT,
            is_return INTEGER
        );
    """)

    cur.execute("""
        CREATE TABLE fact_sales (
            sales_key INTEGER PRIMARY KEY,
            transaction_no TEXT,
            date_key INTEGER,
            customer_key INTEGER,
            product_key INTEGER,
            geography_key INTEGER,
            status_key INTEGER,
            quantity INTEGER,
            unit_price REAL,
            gross_amount REAL,
            return_amount REAL,
            net_amount REAL,
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
            FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
            FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
            FOREIGN KEY (geography_key) REFERENCES dim_geography(geography_key),
            FOREIGN KEY (status_key) REFERENCES dim_transaction_status(status_key)
        );
    """)

    cur.execute("""
        CREATE TABLE fact_daily_country_summary (
            summary_key INTEGER PRIMARY KEY,
            date_key INTEGER,
            geography_key INTEGER,
            total_orders INTEGER,
            total_units_sold INTEGER,
            total_units_returned INTEGER,
            gross_revenue REAL,
            return_loss REAL,
            net_revenue REAL,
            unique_customers INTEGER,
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
            FOREIGN KEY (geography_key) REFERENCES dim_geography(geography_key)
        );
    """)

    # Fast bulk insert
    dim_date.to_sql('dim_date', conn, if_exists='append', index=False)
    dim_customer.to_sql('dim_customer', conn, if_exists='append', index=False)
    dim_product.to_sql('dim_product', conn, if_exists='append', index=False)
    dim_geography.to_sql('dim_geography', conn, if_exists='append', index=False)
    dim_transaction_status.to_sql('dim_transaction_status', conn, if_exists='append', index=False)
    
    print("      -> Ingesting 536,350 fact_sales records into SQLite...")
    fact_sales.to_sql('fact_sales', conn, if_exists='append', index=False, chunksize=50000)
    daily_summary.to_sql('fact_daily_country_summary', conn, if_exists='append', index=False)

    # Create Indexes
    print("      -> Building high-performance indexes...")
    cur.execute("CREATE INDEX idx_fs_date ON fact_sales(date_key);")
    cur.execute("CREATE INDEX idx_fs_cust ON fact_sales(customer_key);")
    cur.execute("CREATE INDEX idx_fs_prod ON fact_sales(product_key);")
    cur.execute("CREATE INDEX idx_fs_geo ON fact_sales(geography_key);")
    cur.execute("CREATE INDEX idx_fs_status ON fact_sales(status_key);")
    cur.execute("CREATE INDEX idx_fs_tx ON fact_sales(transaction_no);")
    cur.execute("CREATE INDEX idx_fdc_date_geo ON fact_daily_country_summary(date_key, geography_key);")

    conn.commit()
    conn.close()

    elapsed = time.time() - t0
    print("=" * 70)
    print(f"ETL Execution Successfully Completed in {elapsed:.2f} seconds!")
    print(f"Summary of Records Created:")
    print(f"  - dim_date:                   {len(dim_date):,} rows")
    print(f"  - dim_customer:               {len(dim_customer):,} rows")
    print(f"  - dim_product:                {len(dim_product):,} rows")
    print(f"  - dim_geography:              {len(dim_geography):,} rows")
    print(f"  - dim_transaction_status:     {len(dim_transaction_status):,} rows")
    print(f"  - fact_sales:                 {len(fact_sales):,} rows")
    print(f"  - fact_daily_country_summary: {len(daily_summary):,} rows")
    print(f"Database File Size: {os.path.getsize(SQLITE_DB_PATH) / (1024*1024):.2f} MB")
    print("=" * 70)

if __name__ == '__main__':
    build_data_warehouse()
