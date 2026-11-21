import psycopg2
import pandas as pd

conn = psycopg2.connect('postgresql://airflow:airflow@localhost:5432/retail_dw')

print('--- Card 4 Query ---')
q_card4 = """
SELECT ROUND((SUM(CASE WHEN c.total_orders > 1 THEN f.net_amount ELSE 0 END) * 100.0 / NULLIF(SUM(f.net_amount), 0))::numeric, 2) AS "Repeat Buyer Share %"
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key;
"""
print(pd.read_sql_query(q_card4, conn))

print('\n--- RFM Query ---')
q_rfm = """
SELECT 
    c.customer_segment AS "RFM Segment",
    ROUND((SUM(f.net_amount) / 1000000.0)::numeric, 2) AS "Net Revenue (M)",
    COUNT(DISTINCT c.customer_key) AS "Customer Count"
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY "Net Revenue (M)" DESC;
"""
print(pd.read_sql_query(q_rfm, conn))

print('\n--- Category & Price Tier Query ---')
q_cat = """
SELECT 
    p.category_name AS "Category",
    ROUND((SUM(f.net_amount) / 1000000.0)::numeric, 2) AS "Net Revenue (M)",
    ROUND((SUM(f.return_amount) * 100.0 / NULLIF(SUM(f.gross_amount), 0))::numeric, 2) AS "Return Rate %",
    ROUND(AVG(f.unit_price)::numeric, 2) AS "Avg Price"
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY "Net Revenue (M)" DESC;
"""
print(pd.read_sql_query(q_cat, conn))

print('\n--- Market Basket Query ---')
q_mb = """
SELECT 
    product_pair AS "Product Pair",
    co_purchase_count AS "Co-Purchase Count"
FROM agg_market_basket_top10
ORDER BY co_purchase_count DESC;
"""
print(pd.read_sql_query(q_mb, conn))
