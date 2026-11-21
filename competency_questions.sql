-- ---------------------------------------------------------------------
-- CQ1: Executive Overall Performance & Net Revenue
-- คำถามที่ 1: ผลประกอบการภาพรวม ยอดขายสุทธิ และอัตราการยกเลิก/คืนสินค้า
-- ---------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT transaction_no) AS total_transactions,
    COUNT(DISTINCT CASE WHEN quantity > 0 THEN transaction_no END) AS completed_orders,
    COUNT(DISTINCT CASE WHEN quantity < 0 THEN transaction_no END) AS cancelled_orders,
    ROUND(SUM(gross_amount), 2) AS gross_revenue,
    ROUND(SUM(return_amount), 2) AS return_loss,
    ROUND(SUM(net_amount), 2) AS net_revenue,
    ROUND(SUM(return_amount) * 100.0 / NULLIF(SUM(gross_amount), 0), 2) AS return_rate_pct,
    ROUND(SUM(net_amount) / NULLIF(COUNT(DISTINCT CASE WHEN quantity > 0 THEN transaction_no END), 0), 2) AS avg_order_value
FROM fact_sales;

-- ---------------------------------------------------------------------
-- CQ2: Top 10 Revenue-Generating Products & Revenue Share (Pareto Analysis)
-- คำถามที่ 2: สินค้า 10 อันดับแรกที่สร้างรายได้สูงสุดและสัดส่วนตามกฎพาเรโต
-- ---------------------------------------------------------------------
WITH prod_sales AS (
    SELECT 
        p.product_no,
        p.product_name,
        p.category_name,
        SUM(f.quantity) AS net_units_sold,
        ROUND(SUM(f.net_amount), 2) AS net_revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.product_no, p.product_name, p.category_name
)
SELECT 
    *,
    ROUND(net_revenue * 100.0 / (SELECT SUM(net_amount) FROM fact_sales), 2) AS revenue_share_pct
FROM prod_sales
ORDER BY net_revenue DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- CQ3: Top 5 International Markets (Excluding UK) & Average Order Value (AOV)
-- คำถามที่ 3: ตลาดต่างประเทศ 5 อันดับแรกนอกสหราชอาณาจักรและมูลค่าเฉลี่ยต่อบิล
-- ---------------------------------------------------------------------
SELECT 
    g.country_name,
    g.region,
    COUNT(DISTINCT f.transaction_no) AS total_orders,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(SUM(f.net_amount) / NULLIF(COUNT(DISTINCT f.transaction_no), 0), 2) AS avg_order_value,
    ROUND(SUM(f.return_amount) * 100.0 / NULLIF(SUM(f.gross_amount), 0), 2) AS return_rate_pct
FROM fact_sales f
JOIN dim_geography g ON f.geography_key = g.geography_key
WHERE g.country_name != 'United Kingdom'
GROUP BY g.country_name, g.region
ORDER BY net_revenue DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- CQ4: Customer Segmentation Distribution via RFM (Recency, Frequency, Monetary)
-- คำถามที่ 4: การแบ่งกลุ่มลูกค้าตามพฤติกรรมการซื้อ (RFM Segmentation)
-- ---------------------------------------------------------------------
SELECT 
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customer), 2) AS customer_share_pct,
    ROUND(SUM(total_spend), 2) AS total_spend,
    ROUND(AVG(total_orders), 1) AS avg_orders,
    ROUND(AVG(recency_days), 1) AS avg_recency_days
FROM dim_customer
GROUP BY customer_segment
ORDER BY total_spend DESC;

-- ---------------------------------------------------------------------
-- CQ5: Monthly Sales Trend & Seasonality Impact
-- คำถามที่ 5: แนวโน้มยอดขายรายเดือนและผลกระทบของเทศกาลวันหยุด (Seasonality)
-- ---------------------------------------------------------------------
SELECT 
    d.year,
    d.month,
    d.month_name_en,
    COUNT(DISTINCT f.transaction_no) AS total_orders,
    SUM(f.quantity) AS net_units,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(SUM(f.return_amount), 2) AS return_amount
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name_en
ORDER BY d.year, d.month;

-- ---------------------------------------------------------------------
-- CQ6: Product Category Performance & Return Rate Analysis
-- คำถามที่ 6: การสร้างรายได้และอัตราการคืนสินค้าจำแนกตามหมวดหมู่สินค้า
-- ---------------------------------------------------------------------
SELECT 
    p.category_name,
    COUNT(DISTINCT f.product_key) AS unique_products,
    ROUND(SUM(f.gross_amount), 2) AS gross_revenue,
    ROUND(SUM(f.return_amount), 2) AS return_loss,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(SUM(f.return_amount) * 100.0 / NULLIF(SUM(f.gross_amount), 0), 2) AS return_rate_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY net_revenue DESC;

-- ---------------------------------------------------------------------
-- CQ7: Day of Week Shopping Behavior & Revenue Distribution
-- คำถามที่ 7: พฤติกรรมการสั่งซื้อตามวันในสัปดาห์ (Day of Week)
-- ---------------------------------------------------------------------
SELECT 
    d.day_name_en AS day_of_week,
    d.is_weekend,
    COUNT(DISTINCT f.transaction_no) AS total_orders,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(AVG(f.net_amount), 2) AS avg_line_item_amount
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.day_of_week, d.day_name_en, d.is_weekend
ORDER BY net_revenue DESC;

-- ---------------------------------------------------------------------
-- CQ8: Basket Size & Price Tier Contribution
-- คำถามที่ 8: การมีส่วนร่วมของระดับราคาสินค้า (Price Tiers)
-- ---------------------------------------------------------------------
SELECT 
    p.price_tier,
    COUNT(DISTINCT f.product_key) AS product_count,
    COUNT(f.sales_key) AS transaction_line_items,
    SUM(f.quantity) AS net_units,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(SUM(f.net_amount) * 100.0 / (SELECT SUM(net_amount) FROM fact_sales), 2) AS revenue_share_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.price_tier
ORDER BY net_revenue DESC;

-- ---------------------------------------------------------------------
-- CQ9: Top 10 High-Value VIP Customers
-- คำถามที่ 9: ลูกค้า VIP 10 อันดับแรกที่มียอดใช้จ่ายสะสมสูงสุด
-- ---------------------------------------------------------------------
SELECT 
    c.customer_no,
    c.country,
    c.customer_segment,
    c.total_orders,
    c.recency_days,
    ROUND(c.total_spend, 2) AS lifetime_net_spend,
    ROUND(c.total_spend / NULLIF(c.total_orders, 0), 2) AS avg_order_spend
FROM dim_customer c
WHERE c.customer_no != 'GUEST'
ORDER BY c.total_spend DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- CQ10: Top 10 Products with Highest Cancellation / Return Loss
-- คำถามที่ 10: สินค้า 10 รายการที่มีมูลค่าการยกเลิก/คืนสินค้าสูงสุด
-- ---------------------------------------------------------------------
SELECT 
    p.product_no,
    p.product_name,
    p.category_name,
    COUNT(CASE WHEN f.quantity < 0 THEN 1 END) AS return_incident_count,
    ABS(SUM(CASE WHEN f.quantity < 0 THEN f.quantity ELSE 0 END)) AS units_returned,
    ROUND(SUM(f.return_amount), 2) AS total_return_loss,
    ROUND(SUM(f.return_amount) * 100.0 / NULLIF(SUM(f.gross_amount) + SUM(f.return_amount), 0), 2) AS return_ratio_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_no, p.product_name, p.category_name
HAVING SUM(f.return_amount) > 0
ORDER BY total_return_loss DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- CQ11: Market Basket Affinity - Top Co-Purchased Product Pairs
-- คำถามที่ 11: การวิเคราะห์คู่สินค้าที่มักถูกสั่งซื้อร่วมกัน (Market Basket Analysis)
-- ---------------------------------------------------------------------
WITH top_transactions AS (
    SELECT transaction_no 
    FROM fact_sales 
    WHERE quantity > 0 
    GROUP BY transaction_no 
    HAVING COUNT(*) BETWEEN 2 AND 15
    LIMIT 500
)
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(DISTINCT f1.transaction_no) AS co_purchase_count
FROM fact_sales f1
JOIN fact_sales f2 ON f1.transaction_no = f2.transaction_no AND f1.product_key < f2.product_key
JOIN dim_product p1 ON f1.product_key = p1.product_key
JOIN dim_product p2 ON f2.product_key = p2.product_key
WHERE f1.transaction_no IN (SELECT transaction_no FROM top_transactions)
  AND f1.quantity > 0 AND f2.quantity > 0
GROUP BY p1.product_name, p2.product_name
ORDER BY co_purchase_count DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- CQ12: First-Time vs Repeat Buyer Contribution by Quarter
-- คำถามที่ 12: สัดส่วนรายได้จากลูกค้าใหม่เทียบกับลูกค้าซื้อซ้ำรายไตรมาส
-- ---------------------------------------------------------------------
WITH first_purchase_tbl AS (
    SELECT 
        customer_key,
        MIN(date_key) AS first_date_key
    FROM fact_sales
    WHERE quantity > 0
    GROUP BY customer_key
)
SELECT 
    d.year || '-Q' || d.quarter AS quarter,
    ROUND(SUM(CASE WHEN f.date_key = fp.first_date_key THEN f.net_amount ELSE 0 END), 2) AS first_time_buyer_revenue,
    ROUND(SUM(CASE WHEN f.date_key > fp.first_date_key THEN f.net_amount ELSE 0 END), 2) AS repeat_buyer_revenue,
    ROUND(SUM(f.net_amount), 2) AS total_net_revenue,
    ROUND(SUM(CASE WHEN f.date_key > fp.first_date_key THEN f.net_amount ELSE 0 END) * 100.0 / NULLIF(SUM(f.net_amount), 0), 2) AS repeat_buyer_share_pct
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN first_purchase_tbl fp ON f.customer_key = fp.customer_key
WHERE f.quantity > 0
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;
