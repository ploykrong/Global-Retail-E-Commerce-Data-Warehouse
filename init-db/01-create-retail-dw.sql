
-- 1. Create Database and Assign Permissions (Run as postgres/superuser if needed)
CREATE DATABASE retail_dw OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE retail_dw TO airflow;

\connect retail_dw;

-- 2. Drop existing tables if re-initializing
DROP TABLE IF EXISTS fact_daily_country_summary CASCADE;
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_transaction_status CASCADE;
DROP TABLE IF EXISTS dim_geography CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- =====================================================================
-- 3. Dimension Tables
-- =====================================================================

-- 3.1 Date Dimension (Conformed Dimension)
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,           -- Format: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name_en VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,          -- 1 = Monday, 7 = Sunday
    day_name_en VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    season VARCHAR(20) NOT NULL
);

-- 3.2 Customer Dimension
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,        -- Surrogate Key
    customer_no VARCHAR(50) NOT NULL UNIQUE,-- Natural Key ('GUEST' for nulls)
    country VARCHAR(100),
    total_orders INTEGER DEFAULT 0,
    total_spend NUMERIC(14,2) DEFAULT 0.00,
    first_purchase_date DATE,
    last_purchase_date DATE,
    recency_days INTEGER,
    customer_segment VARCHAR(50) DEFAULT 'New Customers'
);

-- 3.3 Product Dimension
CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,         -- Surrogate Key
    product_no VARCHAR(50) NOT NULL UNIQUE, -- Natural Key
    product_name TEXT NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    price_tier VARCHAR(50) NOT NULL,
    avg_unit_price NUMERIC(10,2) NOT NULL
);

-- 3.4 Geography Dimension
CREATE TABLE dim_geography (
    geography_key SERIAL PRIMARY KEY,       -- Surrogate Key
    country_name VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(100) NOT NULL,
    market_type VARCHAR(50) NOT NULL,       -- 'Domestic' or 'International'
    currency_code VARCHAR(10) DEFAULT 'GBP'
);

-- 3.5 Transaction Status Dimension
CREATE TABLE dim_transaction_status (
    status_key SERIAL PRIMARY KEY,
    status_code VARCHAR(20) NOT NULL UNIQUE,-- 'COMPLETED', 'CANCELLED'
    status_name VARCHAR(50) NOT NULL,
    is_return BOOLEAN NOT NULL
);

-- =====================================================================
-- 4. Fact Tables
-- =====================================================================

-- 4.1 Detailed Sales Line Item Fact Table
CREATE TABLE fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    transaction_no VARCHAR(50) NOT NULL,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    geography_key INTEGER NOT NULL REFERENCES dim_geography(geography_key),
    status_key INTEGER NOT NULL REFERENCES dim_transaction_status(status_key),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    gross_amount NUMERIC(14,2) NOT NULL,    -- Quantity * Price if Quantity > 0 else 0
    return_amount NUMERIC(14,2) NOT NULL,   -- ABS(Quantity) * Price if Quantity < 0 else 0
    net_amount NUMERIC(14,2) NOT NULL       -- Quantity * Price
);

-- Create Indexes on fact_sales for high-speed queries
CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_geography ON fact_sales(geography_key);
CREATE INDEX idx_fact_sales_status ON fact_sales(status_key);
CREATE INDEX idx_fact_sales_tx ON fact_sales(transaction_no);

-- 4.2 Aggregated Daily Country Summary Fact Table (OLAP Pre-aggregation)
CREATE TABLE fact_daily_country_summary (
    summary_key SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    geography_key INTEGER NOT NULL REFERENCES dim_geography(geography_key),
    total_orders INTEGER NOT NULL,
    total_units_sold INTEGER NOT NULL,
    total_units_returned INTEGER NOT NULL,
    gross_revenue NUMERIC(14,2) NOT NULL,
    return_loss NUMERIC(14,2) NOT NULL,
    net_revenue NUMERIC(14,2) NOT NULL,
    unique_customers INTEGER NOT NULL,
    UNIQUE (date_key, geography_key)
);

-- =====================================================================
-- 5. Seed Static / Conformed Data
-- =====================================================================

-- 5.1 Seed Transaction Status
INSERT INTO dim_transaction_status (status_code, status_name, is_return) VALUES
('COMPLETED', 'Completed', FALSE),
('CANCELLED', 'Cancelled / Returned', TRUE)
ON CONFLICT (status_code) DO NOTHING;

-- 5.2 Pre-generate dim_date (2018-01-01 to 2022-12-31)
INSERT INTO dim_date (
    date_key, full_date, day, month, month_name_en, 
    quarter, year, day_of_week, day_name_en, is_weekend, season
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER AS date_key,
    d::DATE AS full_date,
    EXTRACT(DAY FROM d)::INTEGER AS day,
    EXTRACT(MONTH FROM d)::INTEGER AS month,
    TO_CHAR(d, 'FMMonth') AS month_name_en,
    EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
    EXTRACT(YEAR FROM d)::INTEGER AS year,
    EXTRACT(ISODOW FROM d)::INTEGER AS day_of_week,
    TO_CHAR(d, 'FMDay') AS day_name_en,
    CASE WHEN EXTRACT(ISODOW FROM d)::INTEGER IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend,
    CASE 
        WHEN EXTRACT(MONTH FROM d)::INTEGER IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM d)::INTEGER IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM d)::INTEGER IN (6, 7, 8) THEN 'Summer'
        ELSE 'Autumn'
    END AS season
FROM generate_series('2018-01-01'::DATE, '2022-12-31'::DATE, '1 day'::INTERVAL) d
ON CONFLICT (full_date) DO NOTHING;
