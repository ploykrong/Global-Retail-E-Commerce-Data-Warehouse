import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Retail DW Executive Dashboard | DSI463",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive look and feel
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "retail_dw.db")

@st.cache_resource
def get_db():
    if not os.path.exists(DB_PATH):
        st.error(f"Data Warehouse file not found at: {DB_PATH}. Please run setup_database.py first!")
        st.stop()
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_db()

@st.cache_data(ttl=3600)
def run_query(sql, params=None):
    if params:
        return pd.read_sql_query(sql, conn, params=params)
    return pd.read_sql_query(sql, conn)

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/shop.png", width=64)
st.sidebar.title("🛒 DW Control Center")
st.sidebar.markdown("**DSI463 Final Project**  \n*Ploykroang Kongwathananukul*  \n*ID: 6624650351*")
st.sidebar.markdown("---")

# Global Filter Options
all_countries = run_query("SELECT DISTINCT country_name FROM dim_geography ORDER BY country_name;")['country_name'].tolist()
all_categories = run_query("SELECT DISTINCT category_name FROM dim_product ORDER BY category_name;")['category_name'].tolist()

selected_countries = st.sidebar.multiselect("🌍 Select Countries", all_countries, default=[])
selected_categories = st.sidebar.multiselect("📦 Select Product Categories", all_categories, default=[])
selected_status = st.sidebar.radio("📋 Transaction Status", ["All Transactions", "Completed Only", "Returns/Cancellations Only"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dataset:** 536,350 Sales Transactions  \n**Timeframe:** Dec 2018 – Dec 2019  \n**Architecture:** Kimball Star Schema")

# Header
st.markdown('<div class="main-title">Global Retail & E-Commerce Executive Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Data Warehouse Analytics & Competency Questions Engine | DSI463 Data Model in Digital Era</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive KPIs",
    "❓ Competency Questions Explorer",
    "👥 Customer RFM Segments",
    "🌍 Geographic Expansion",
    "📦 Product & Basket Analytics",
    "🏛️ Data Model & Architecture"
])

# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE KPIS
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Executive KPI Overview (Dec 2018 – Dec 2019)")
    
    # Filter conditions for SQL
    where_clauses = ["1=1"]
    if selected_countries:
        country_str = "', '".join(selected_countries)
        where_clauses.append(f"g.country_name IN ('{country_str}')")
    if selected_categories:
        cat_str = "', '".join(selected_categories)
        where_clauses.append(f"p.category_name IN ('{cat_str}')")
    if selected_status == "Completed Only":
        where_clauses.append("f.quantity > 0")
    elif selected_status == "Returns/Cancellations Only":
        where_clauses.append("f.quantity < 0")

    where_sql = " AND ".join(where_clauses)

    kpi_query = f"""
    SELECT 
        COUNT(DISTINCT f.transaction_no) AS total_orders,
        COUNT(DISTINCT f.customer_key) AS active_customers,
        SUM(f.quantity) AS net_units_sold,
        ROUND(SUM(f.gross_amount), 2) AS gross_revenue,
        ROUND(SUM(f.return_amount), 2) AS return_loss,
        ROUND(SUM(f.net_amount), 2) AS net_revenue
    FROM fact_sales f
    JOIN dim_geography g ON f.geography_key = g.geography_key
    JOIN dim_product p ON f.product_key = p.product_key
    WHERE {where_sql};
    """
    kpi_data = run_query(kpi_query).iloc[0]

    gross_rev = kpi_data['gross_revenue'] or 0
    return_loss = kpi_data['return_loss'] or 0
    net_rev = kpi_data['net_revenue'] or 0
    total_orders = kpi_data['total_orders'] or 0
    net_units = kpi_data['net_units_sold'] or 0
    return_rate = (return_loss / gross_rev * 100) if gross_rev > 0 else 0
    aov = (net_rev / total_orders) if total_orders > 0 else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Gross Revenue", f"£{gross_rev:,.2f}")
    col2.metric("Return Loss", f"£{return_loss:,.2f}", delta=f"-{return_rate:.2f}%", delta_color="inverse")
    col3.metric("Net Revenue", f"£{net_rev:,.2f}")
    col4.metric("Total Invoices", f"{total_orders:,}")
    col5.metric("Avg Order Value (AOV)", f"£{aov:,.2f}")
    col6.metric("Net Units Sold", f"{net_units:,}")

    st.markdown("---")

    # Visualizations: Monthly Revenue Trend & Category Breakdown
    row1_c1, row1_c2 = st.columns([7, 5])
    
    with row1_c1:
        monthly_trend = run_query(f"""
        SELECT 
            d.year || '-' || printf('%02d', d.month) AS ym,
            ROUND(SUM(f.net_amount), 2) AS net_revenue,
            ROUND(SUM(f.return_amount), 2) AS return_amount
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_geography g ON f.geography_key = g.geography_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE {where_sql}
        GROUP BY d.year, d.month
        ORDER BY ym;
        """)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly_trend['ym'], y=monthly_trend['net_revenue'],
            name='Net Revenue (£)', marker_color='#2563eb'
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_trend['ym'], y=monthly_trend['return_amount'],
            name='Return Loss (£)', marker_color='#ef4444', mode='lines+markers'
        ))
        fig_trend.update_layout(
            title="Monthly Net Revenue & Return Loss Trend",
            xaxis_title="Year-Month", yaxis_title="Amount (£)",
            template="plotly_white", hovermode="x unified", height=380
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with row1_c2:
        cat_data = run_query(f"""
        SELECT 
            p.category_name,
            ROUND(SUM(f.net_amount), 2) AS net_revenue
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_geography g ON f.geography_key = g.geography_key
        WHERE {where_sql}
        GROUP BY p.category_name
        ORDER BY net_revenue DESC;
        """)
        fig_cat = px.pie(
            cat_data, values='net_revenue', names='category_name',
            title="Revenue Contribution by Product Category",
            hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_cat.update_layout(height=380)
        st.plotly_chart(fig_cat, use_container_width=True)

    # Day of Week & Hourly Shopping Pattern
    st.markdown("### Weekly Shopping Behavior")
    dow_data = run_query(f"""
    SELECT 
        d.day_name_en AS day_name,
        d.day_of_week,
        COUNT(DISTINCT f.transaction_no) AS total_orders,
        ROUND(SUM(f.net_amount), 2) AS net_revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_geography g ON f.geography_key = g.geography_key
    JOIN dim_product p ON f.product_key = p.product_key
    WHERE {where_sql}
    GROUP BY d.day_of_week, d.day_name_en
    ORDER BY d.day_of_week;
    """)
    fig_dow = px.bar(
        dow_data, x='day_name', y='net_revenue', color='total_orders',
        labels={'day_name': 'Day of Week', 'net_revenue': 'Net Revenue (£)', 'total_orders': 'Order Count'},
        title="Revenue & Order Volume by Day of Week",
        color_continuous_scale="Blues", template="plotly_white", height=320
    )
    st.plotly_chart(fig_dow, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: COMPETENCY QUESTIONS EXPLORER (12 CQs)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Competency Questions (CQ) Interactive Analytical Engine")
    st.markdown("Select any Competency Question below to inspect the business intent, view the underlying Kimball Star Schema SQL query, execute it live, and view the interactive visualizations & strategic findings.")

    cq_catalog = {
        "CQ1: Executive Overall Performance & Net Revenue": {
            "title_th": "คำถามที่ 1: ผลประกอบการภาพรวม ยอดขายสุทธิ และอัตราการยกเลิก/คืนสินค้า",
            "desc": "ยอดขายรวมสุทธิ (Net Revenue), จำนวนคำสั่งซื้อสำเร็จ (Total Orders), จำนวนสินค้าที่ขายได้สุทธิ (Net Units Sold), และอัตราการยกเลิก/คืนสินค้า (Cancellation/Return Rate) ภาพรวมทั้งธุรกิจเป็นเท่าใด?",
            "sql": """SELECT 
    COUNT(DISTINCT transaction_no) AS total_transactions,
    COUNT(DISTINCT CASE WHEN quantity > 0 THEN transaction_no END) AS completed_orders,
    COUNT(DISTINCT CASE WHEN quantity < 0 THEN transaction_no END) AS cancelled_orders,
    ROUND(SUM(gross_amount), 2) AS gross_revenue,
    ROUND(SUM(return_amount), 2) AS return_loss,
    ROUND(SUM(net_amount), 2) AS net_revenue,
    ROUND(SUM(return_amount) * 100.0 / NULLIF(SUM(gross_amount), 0), 2) AS return_rate_pct,
    ROUND(SUM(net_amount) / NULLIF(COUNT(DISTINCT CASE WHEN quantity > 0 THEN transaction_no END), 0), 2) AS avg_order_value
FROM fact_sales;""",
            "insight": "ธุรกิจมียอดขายสุทธิรวมทั้งสิ้น **£60,280,024.26** (60.28 ล้านปอนด์) จากคำสั่งซื้อสำเร็จ 19,790 บิล โดยมีอัตราการคืนสินค้าอยู่ที่ 4.27% (มูลค่าความเสียหายจากการคืน £2.68M) และยอดใช้จ่ายเฉลี่ยต่อบิล (AOV) สูงถึง £3,045.98 สะท้อนถึงการเป็นผู้ค้าส่งและค้าปลีกขนาดใหญ่"
        },
        "CQ2: Top 10 Revenue Products & Pareto Share": {
            "title_th": "คำถามที่ 2: สินค้า 10 อันดับแรกที่สร้างรายได้สูงสุดและสัดส่วนตามกฎพาเรโต (Pareto)",
            "desc": "สินค้า 10 อันดับแรกที่สร้างรายได้สุทธิสูงสุด (Top 10 Products by Net Revenue) คือสินค้าใดบ้าง และคิดเป็นสัดส่วนเท่าใดของรายได้รวม (Pareto Principle)?",
            "sql": """WITH prod_sales AS (
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
LIMIT 10;""",
            "insight": "สินค้าขายดีอันดับ 1 คือ 'Popcorn Holder' สร้างรายได้ £583,286.51 ตามด้วย 'World War 2 Gliders Asstd Designs' (£557,170.43) และ 'Paper Craft Little Birdie' (£501,359.05) โดยสินค้าท็อป 10 คิดเป็นสัดส่วนรายได้หลักที่องค์กรต้องรักษาระดับสต็อก (Safety Stock) ไม่ให้ขาดตลาด"
        },
        "CQ3: Top 5 International Markets & AOV": {
            "title_th": "คำถามที่ 3: ตลาดต่างประเทศ 5 อันดับแรกนอกสหราชอาณาจักรและมูลค่าต่อบิล",
            "desc": "ตลาดต่างประเทศ 5 อันดับแรกที่มีมูลค่าการสั่งซื้อสุทธิสูงสุดนอกเหนือจากสหราชอาณาจักร (UK) คือประเทศใด และมีมูลค่าเฉลี่ยต่อคำสั่งซื้อ (Average Order Value: AOV) เป็นอย่างไรเมื่อเทียบกับตลาดในประเทศ?",
            "sql": """SELECT 
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
LIMIT 5;""",
            "insight": "เนเธอร์แลนด์ (Netherlands) เป็นตลาดส่งออกอันดับ 1 มียอดขายสุทธิ £2.15M โดยมีค่าเฉลี่ยต่อบิลสูงถึง **£22,142.39** ต่อออเดอร์ ตามด้วยไอร์แลนด์ (EIRE, £1.66M) เยอรมนี (Germany, £1.35M) ฝรั่งเศส (France, £1.32M) และออสเตรเลีย (£988K, AOV £13,544.61) บ่งชี้ว่าลูกค้าต่างประเทศเป็นคำสั่งซื้อแบบ B2B ล็อตใหญ่"
        },
        "CQ4: Customer Segmentation via RFM Analysis": {
            "title_th": "คำถามที่ 4: การแบ่งกลุ่มลูกค้าตามพฤติกรรมการซื้อ (RFM Segmentation)",
            "desc": "การจัดกลุ่มลูกค้าตามพฤติกรรมการซื้อ (RFM Segmentation: Champions, Loyal Customers, At Risk, Lost Customers) มีการกระจายตัวของจำนวนลูกค้าและมูลค่ารายได้ในแต่ละกลุ่มอย่างไร?",
            "sql": """SELECT 
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customer), 2) AS customer_share_pct,
    ROUND(SUM(total_spend), 2) AS total_spend,
    ROUND(AVG(total_orders), 1) AS avg_orders,
    ROUND(AVG(recency_days), 1) AS avg_recency_days
FROM dim_customer
GROUP BY customer_segment
ORDER BY total_spend DESC;""",
            "insight": "กลุ่ม **VIP Champions** มีสัดส่วน 23.23% (1,101 ราย) แต่สร้างรายได้สูงถึง **£40,028,590.51 (66.4% ของรายได้ทั้งหมด)** ซื้อเฉลี่ย 13 ครั้งต่อปีและซื้อล่าสุดภายใน 17 วัน ในขณะที่กลุ่ม At Risk มี 1,032 ราย (£5.53M) ที่ขาดการสั่งซื้อเฉลี่ย 225 วัน จำเป็นต้องใช้แคมเปญ Win-Back ด่วน"
        },
        "CQ5: Monthly Sales Trend & Seasonality Impact": {
            "title_th": "คำถามที่ 5: แนวโน้มยอดขายรายเดือนและผลกระทบของเทศกาลวันหยุด (Seasonality)",
            "desc": "แนวโน้มยอดขายสุทธิและจำนวนคำสั่งซื้อในแต่ละเดือนตลอดปี 2018 - 2019 มีทิศทางอย่างไร และช่วงไตรมาสใด (เช่น Q4 Holiday Season) มียอดขายพุ่งขึ้นสูงสุด?",
            "sql": """SELECT 
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
ORDER BY d.year, d.month;""",
            "insight": "ยอดขายพุ่งขึ้นสูงสุดอย่างชัดเจนในเดือนพฤศจิกายน 2019 (£8.01M, 2,866 บิล) ซึ่งมากกว่าช่วงเดือนกุมภาพันธ์ (£3.30M) เกินกว่า 2.4 เท่า สะท้อนถึงเทศกาล Black Friday และการสต็อกสินค้าก่อนคริสต์มาสของฝั่งยุโรป"
        },
        "CQ6: Product Category Performance & Return Rate": {
            "title_th": "คำถามที่ 6: การสร้างรายได้และอัตราการคืนสินค้าจำแนกตามหมวดหมู่สินค้า",
            "desc": "กลุ่มหมวดหมู่สินค้าใด (Product Categories) ที่สร้างรายได้หลัก และหมวดหมู่ใดมีอัตราการคืนสินค้า (Return Rate %) สูงที่สุดที่ต้องเฝ้าระวังด้านคุณภาพ?",
            "sql": """SELECT 
    p.category_name,
    COUNT(DISTINCT f.product_key) AS unique_products,
    ROUND(SUM(f.gross_amount), 2) AS gross_revenue,
    ROUND(SUM(f.return_amount), 2) AS return_loss,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(SUM(f.return_amount) * 100.0 / NULLIF(SUM(f.gross_amount), 0), 2) AS return_rate_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY net_revenue DESC;""",
            "insight": "หมวดหมู่ 'Gifts & General Merchandise' สร้างรายได้สูงสุด (£18.23M) ตามด้วย 'Home Decor & Furnishing' (£10.74M) และ 'Holiday & Seasonal' (£8.70M) ขณะที่หมวดหมู่ 'Home Storage & Containers' มีอัตราการคืนสินค้าสูงสุดที่ 10.45% (£1.11M) ซึ่งต้องตรวจสอบปัญหาความเสียหายจากการขนส่งหรือบรรจุภัณฑ์แตกหัก"
        },
        "CQ7: Peak Day of Week & Shopping Behavior": {
            "title_th": "คำถามที่ 7: พฤติกรรมการสั่งซื้อตามวันในสัปดาห์ (Day of Week)",
            "desc": "วันใดในสัปดาห์ (Day of Week) ที่ลูกค้าสั่งซื้อสินค้าหนาแน่นที่สุดทั้งในแง่ของปริมาณชิ้นและยอดขาย เพื่อวางแผนการจัดกำลังคนในคลังสินค้าและแคมเปญการตลาด?",
            "sql": """SELECT 
    d.day_name_en AS day_of_week,
    d.is_weekend,
    COUNT(DISTINCT f.transaction_no) AS total_orders,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(AVG(f.net_amount), 2) AS avg_line_item_amount
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.day_of_week, d.day_name_en, d.is_weekend
ORDER BY net_revenue DESC;""",
            "insight": "วันพฤหัสบดี (Thursday) มียอดสั่งซื้อสูงสุดที่ 3,982 บิล สร้างรายได้ £12.83M ตามด้วยวันพุธ (£11.16M) และวันอังคาร (£11.13M) ขณะที่วันเสาร์ไม่มีการบันทึกคำสั่งซื้อ แสดงถึงรอบการสั่งซื้อของธุรกิจ B2B ที่มักสั่งซื้อก่อนสุดสัปดาห์เพื่อให้จัดส่งได้ทันวันจันทร์"
        },
        "CQ8: Basket Size & Price Tier Contribution": {
            "title_th": "คำถามที่ 8: การมีส่วนร่วมของระดับราคาสินค้า (Price Tiers)",
            "desc": "การกระจายตัวของระดับราคาสินค้า (Price Tiers: Budget, Mid-range, Premium, Luxury) มีสัดส่วนรายได้และปริมาณสินค้าขายได้เป็นอย่างไร?",
            "sql": """SELECT 
    p.price_tier,
    COUNT(DISTINCT f.product_key) AS product_count,
    COUNT(f.sales_key) AS transaction_line_items,
    SUM(f.quantity) AS net_units,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(SUM(f.net_amount) * 100.0 / (SELECT SUM(net_amount) FROM fact_sales), 2) AS revenue_share_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.price_tier
ORDER BY net_revenue DESC;""",
            "insight": "สินค้ากลุ่ม **Mid-range (£10–25)** สร้างรายได้หลักอย่างถล่มทลายถึง **£48,740,790.39 (80.86% ของรายได้รวม)** จาก 3,845,958 ชิ้นที่จำหน่าย บ่งชี้ว่าสินค้าชูโรงของธุรกิจตั้งราคาอยู่ในช่วงที่ตลาดตัดสินใจซื้อง่ายและได้มาร์จิ้นสูง"
        },
        "CQ9: Top 10 High-Value VIP Customers": {
            "title_th": "คำถามที่ 9: ลูกค้า VIP 10 อันดับแรกที่มียอดใช้จ่ายสะสมสูงสุด",
            "desc": "ลูกค้า 10 อันดับแรกที่มียอดการใช้จ่ายสะสมสูงสุด (Top 10 VIP Customers) คือใคร ประเทศใด มียอดซื้อเฉลี่ยกี่บาท และความถี่ในการซื้อเป็นอย่างไร?",
            "sql": """SELECT 
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
LIMIT 10;""",
            "insight": "ลูกค้าระดับ Top 1 คือลูกค้ารหัส 14646 จากประเทศเนเธอร์แลนด์ มียอดสั่งซื้อสะสมสูงถึง £1,273,388.94 จาก 77 ออเดอร์ ตามด้วยลูกค้ารหัส 18102 (UK, £1.03M) และ 12415 (ออสเตรเลีย, £895K) ทั้ง 10 รายสร้างมูลค่ารวมเกือบ £8.5M หรือประมาณ 14% ของทั้งบริษัท"
        },
        "CQ10: Cancellation & Return Root-Cause Analysis": {
            "title_th": "คำถามที่ 10: สินค้า 10 รายการที่มีมูลค่าการยกเลิก/คืนสินค้าสูงสุด",
            "desc": "สินค้า 10 รายการที่มีมูลค่าการยกเลิกหรือคืนสินค้า (Return Loss Amount) สูงสุดคือรายการใด และมีสัดส่วนการคืนเทียบกับยอดขายของสินค้านั้นอย่างไร?",
            "sql": """SELECT 
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
LIMIT 10;""",
            "insight": "สินค้า 'Medium Ceramic Top Storage Jar' (รหัส 23166) พบการยกเลิกหรือคืนสินค้ามูลค่าสูงถึง **£843,277.96** (74,494 ชิ้น คิดเป็นอัตราส่วนการคืน 48.88%) และ 'Paper Craft Little Birdie' (รหัส 23843) สูงถึง £501,359.05 ซึ่งต้องสอบสวนกระบวนการบรรจุภัณฑ์และการขนส่งสินค้าเซรามิก/ของเปราะบางทันที"
        },
        "CQ11: Market Basket Affinity - Co-Purchased Items": {
            "title_th": "คำถามที่ 11: การวิเคราะห์คู่สินค้าที่มักถูกสั่งซื้อร่วมกัน (Market Basket Analysis)",
            "desc": "สินค้าคู่ใดที่ถูกสั่งซื้อร่วมกันบ่อยที่สุดในคำสั่งซื้อเดียวกัน (Market Basket Analysis / Frequent Itemsets) เพื่อใช้จัดชุดโปรโมชั่น Bundle หรือ Cross-selling?",
            "sql": """WITH top_transactions AS (
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
LIMIT 10;""",
            "insight": "คู่สินค้าที่มักถูกซื้อคู่กันบ่อยที่สุดคือชุดของขวัญ เช่น 'Hand Warmer Red Retrospot' คู่กับ 'Hand Warmer Union Jack' (ถูกสั่งซื้อร่วมกัน 30 ครั้งในตัวอย่าง) และสินค้าเซตขวดแยม 'Jam Making Set With Jars' คู่กับ 'Jam Making Set Printed' สามารถนำไปทำแคมเปญ Buy 1 Get Discount on Second Item ได้ทันที"
        },
        "CQ12: First-Time vs Repeat Buyer Contribution": {
            "title_th": "คำถามที่ 12: สัดส่วนรายได้จากลูกค้าใหม่เทียบกับลูกค้าซื้อซ้ำรายไตรมาส (Cohort Retention)",
            "desc": "สัดส่วนรายได้จากลูกค้าใหม่ (First-time Buyers) เทียบกับลูกค้าซื้อซ้ำ (Repeat Buyers) ในแต่ละไตรมาสเป็นอย่างไร สะท้อนความภักดีของฐานลูกค้าหรือไม่?",
            "sql": """WITH first_purchase_tbl AS (
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
ORDER BY d.year, d.quarter;""",
            "insight": "อัตราการสร้างรายได้จากลูกค้าซื้อซ้ำ (Repeat Buyer Share) เติบโตขึ้นอย่างมีนัยสำคัญจาก **26.06% ในไตรมาส 4/2018 พุ่งขึ้นเป็น 86.56% ในไตรมาส 4/2019** สะท้อนถึง Retention Rate และ Customer Lifetime Value (LTV) ที่แข็งแกร่งอย่างยิ่งของแพลตฟอร์ม"
        }
    }

    selected_cq = st.selectbox("🎯 Select a Competency Question to Explore:", list(cq_catalog.keys()))
    cq_item = cq_catalog[selected_cq]

    st.markdown(f"### {cq_item['title_th']}")
    st.info(f"**Business Question:** {cq_item['desc']}")

    with st.expander("🔍 View Kimball Star Schema SQL Query", expanded=False):
        st.code(cq_item['sql'], language="sql")

    # Run query
    cq_result = run_query(cq_item['sql'])
    
    # Display Chart and Data
    res_col1, res_col2 = st.columns([6, 6])
    with res_col1:
        st.markdown("**📊 Data Visualization**")
        if "CQ1:" in selected_cq:
            m_df = pd.DataFrame({
                "Metric": ["Completed Revenue", "Return Loss Amount"],
                "Amount": [cq_result['gross_revenue'].iloc[0], cq_result['return_loss'].iloc[0]]
            })
            fig = px.bar(m_df, x="Metric", y="Amount", color="Metric", color_discrete_map={"Completed Revenue": "#10b981", "Return Loss Amount": "#ef4444"})
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ2:" in selected_cq or "CQ10:" in selected_cq:
            col_x = "net_revenue" if "CQ2:" in selected_cq else "total_return_loss"
            fig = px.bar(cq_result.iloc[::-1], y="product_name", x=col_x, orientation='h', color=col_x, color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ3:" in selected_cq:
            fig = px.bar(cq_result, x="country_name", y="net_revenue", color="avg_order_value", color_continuous_scale="Teal")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ4:" in selected_cq:
            fig = px.pie(cq_result, values="total_spend", names="customer_segment", hole=0.4, title="Spend by Segment")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ5:" in selected_cq:
            cq_result['period'] = cq_result['year'].astype(str) + '-' + cq_result['month'].astype(str)
            fig = px.line(cq_result, x="period", y="net_revenue", markers=True, title="Monthly Net Sales")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ6:" in selected_cq:
            fig = px.bar(cq_result, x="category_name", y="net_revenue", color="return_rate_pct", title="Category Sales & Return Rate %")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ7:" in selected_cq:
            fig = px.bar(cq_result, x="day_of_week", y="net_revenue", color="total_orders")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ8:" in selected_cq:
            fig = px.pie(cq_result, values="net_revenue", names="price_tier", title="Revenue by Price Tier")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ9:" in selected_cq:
            fig = px.bar(cq_result, x="customer_no", y="lifetime_net_spend", color="country")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ11:" in selected_cq:
            cq_result['pair'] = cq_result['product_a'].str[:15] + " + " + cq_result['product_b'].str[:15]
            fig = px.bar(cq_result, x="pair", y="co_purchase_count")
            st.plotly_chart(fig, use_container_width=True)
        elif "CQ12:" in selected_cq:
            fig = px.bar(cq_result, x="quarter", y=["first_time_buyer_revenue", "repeat_buyer_revenue"], title="New vs Repeat Buyer Revenue")
            st.plotly_chart(fig, use_container_width=True)

    with res_col2:
        st.markdown("**📋 SQL Query Results Table**")
        st.dataframe(cq_result, use_container_width=True, height=350)

    st.success(f"💡 **Business Insight & Recommendation:**  \n{cq_item['insight']}")

# -----------------------------------------------------------------------------
# TAB 3: CUSTOMER RFM SEGMENTS
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Customer Behavior & RFM Segmentation Analytics")
    rfm_df = run_query("""
    SELECT 
        customer_segment,
        COUNT(*) AS customer_count,
        ROUND(SUM(total_spend), 2) AS total_spend,
        ROUND(AVG(total_orders), 1) AS avg_orders,
        ROUND(AVG(recency_days), 1) AS avg_recency_days
    FROM dim_customer
    GROUP BY customer_segment
    ORDER BY total_spend DESC;
    """)

    rfm_col1, rfm_col2 = st.columns([5, 7])
    with rfm_col1:
        fig_rfm_pie = px.pie(
            rfm_df, values='total_spend', names='customer_segment',
            title="Total Spend Contribution by Customer Segment", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_rfm_pie, use_container_width=True)

    with rfm_col2:
        st.markdown("**Segment Summary Matrix**")
        st.dataframe(rfm_df, use_container_width=True)

    st.markdown("### Top 20 VIP Champions (Highest Lifetime Value)")
    vip_df = run_query("""
    SELECT 
        customer_no, country, total_orders, 
        ROUND(total_spend, 2) AS lifetime_spend, 
        recency_days, first_purchase_date, last_purchase_date
    FROM dim_customer
    WHERE customer_segment = 'VIP Champions'
    ORDER BY total_spend DESC
    LIMIT 20;
    """)
    st.dataframe(vip_df, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: GEOGRAPHIC EXPANSION
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Global Geographic Sales Performance")
    geo_df = run_query("""
    SELECT 
        g.country_name,
        g.region,
        g.market_type,
        COUNT(DISTINCT f.transaction_no) AS total_orders,
        ROUND(SUM(f.net_amount), 2) AS net_revenue,
        ROUND(SUM(f.return_amount), 2) AS return_amount
    FROM fact_sales f
    JOIN dim_geography g ON f.geography_key = g.geography_key
    GROUP BY g.country_name, g.region, g.market_type
    ORDER BY net_revenue DESC;
    """)

    geo_map = px.choropleth(
        geo_df, locations="country_name", locationmode="country names",
        color="net_revenue", hover_name="country_name",
        hover_data=["region", "total_orders", "net_revenue"],
        color_continuous_scale="Reds", title="Global Revenue Distribution by Country"
    )
    geo_map.update_layout(height=450, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(geo_map, use_container_width=True)

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("**Domestic vs International Performance**")
        mkt_df = geo_df.groupby('market_type').agg(
            revenue=('net_revenue', 'sum'),
            orders=('total_orders', 'sum')
        ).reset_index()
        fig_mkt = px.bar(mkt_df, x='market_type', y='revenue', color='market_type', title="Revenue: UK Domestic vs International Export")
        st.plotly_chart(fig_mkt, use_container_width=True)
    with g_col2:
        st.markdown("**Top 10 Export Markets Table**")
        st.dataframe(geo_df[geo_df['country_name'] != 'United Kingdom'].head(10), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 5: PRODUCT & BASKET ANALYTICS
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("Product Performance, Pareto Analysis & Returns")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("### Top 15 Best-Selling Products by Revenue")
        top_p = run_query("""
        SELECT 
            p.product_no, p.product_name, p.category_name,
            SUM(f.quantity) AS units_sold,
            ROUND(SUM(f.net_amount), 2) AS net_revenue
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.product_no, p.product_name, p.category_name
        ORDER BY net_revenue DESC
        LIMIT 15;
        """)
        fig_tp = px.bar(top_p.iloc[::-1], y='product_name', x='net_revenue', orientation='h', color='category_name', title="Top 15 Revenue Drivers")
        st.plotly_chart(fig_tp, use_container_width=True)

    with p_col2:
        st.markdown("### Highest Return / Cancellation Loss Items")
        loss_p = run_query("""
        SELECT 
            p.product_no, p.product_name, p.category_name,
            ROUND(SUM(f.return_amount), 2) AS return_loss,
            ABS(SUM(CASE WHEN f.quantity < 0 THEN f.quantity ELSE 0 END)) AS units_returned
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.product_no, p.product_name, p.category_name
        HAVING SUM(f.return_amount) > 0
        ORDER BY return_loss DESC
        LIMIT 15;
        """)
        fig_lp = px.bar(loss_p.iloc[::-1], y='product_name', x='return_loss', orientation='h', color_discrete_sequence=['#ef4444'], title="Top 15 Return Loss Items")
        st.plotly_chart(fig_lp, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 6: DATA WAREHOUSE ARCHITECTURE & DATA DICTIONARY
# -----------------------------------------------------------------------------
with tab6:
    st.subheader("Kimball Star Schema Data Warehouse Architecture")
    st.markdown("""
    The Retail Data Warehouse is architected using **Ralph Kimball's Dimensional Modeling methodology**. 
    It features a centralized **Fact Table (`fact_sales`)** surrounded by 5 conformed dimension tables, 
    plus an aggregated summary fact table (`fact_daily_country_summary`) for rapid OLAP roll-up queries.
    """)

    st.markdown("""
```
               +-----------------------------+
               |          dim_date           |
               |-----------------------------|
               | PK  date_key (YYYYMMDD)     |
               |     full_date, day, month   |
               |     quarter, year, season   |
               |     day_of_week, is_weekend |
               +-----------------------------+
                              ^
                              |
     +------------------------+------------------------+
     |                                                 |
     |                                                 v
+-----------------------------+          +-----------------------------+
|         dim_customer        |          |    dim_transaction_status   |
|-----------------------------|          |-----------------------------|
| PK  customer_key (SK)       |          | PK  status_key              |
|     customer_no (NK)        |          |     status_code (COMP/CANC) |
|     country, customer_seg   |          |     status_name             |
|     total_orders, spend     |          |     is_return (BOOLEAN)     |
|     recency_days            |          +-----------------------------+
+-----------------------------+                         ^
     |                                                  |
     v                                                  |
+--------------------------------------------------------------+
|                          fact_sales                          |
|--------------------------------------------------------------|
| PK  sales_key (BIGINT)                                       |
| FK  date_key -------------> dim_date                         |
| FK  customer_key ---------> dim_customer                     |
| FK  product_key ----------> dim_product                      |
| FK  geography_key --------> dim_geography                    |
| FK  status_key -----------> dim_transaction_status           |
|     transaction_no                                           |
|     quantity                                                 |
|     unit_price                                               |
|     gross_amount                                             |
|     return_amount                                            |
|     net_amount                                               |
+--------------------------------------------------------------+
     ^                                                  ^
     |                                                  |
+-----------------------------+          +-----------------------------+
|         dim_product         |          |        dim_geography        |
|-----------------------------|          |-----------------------------|
| PK  product_key (SK)        |          | PK  geography_key (SK)      |
|     product_no (NK)         |          |     country_name (UNIQUE)   |
|     product_name            |          |     region, market_type     |
|     category_name           |          |     currency_code           |
|     price_tier, unit_price  |          +-----------------------------+
+-----------------------------+
```
    """)

    st.markdown("### Data Warehouse Statistics & Table Metadata")
    meta_df = pd.DataFrame([
        {"Table": "dim_date", "Type": "Dimension", "Grain": "1 Calendar Day", "Row Count": "1,461", "Primary Key": "date_key (INT)"},
        {"Table": "dim_customer", "Type": "Dimension", "Grain": "1 Unique Customer", "Row Count": "4,739", "Primary Key": "customer_key (SERIAL)"},
        {"Table": "dim_product", "Type": "Dimension", "Grain": "1 Unique Product", "Row Count": "3,768", "Primary Key": "product_key (SERIAL)"},
        {"Table": "dim_geography", "Type": "Dimension", "Grain": "1 Country/Market", "Row Count": "38", "Primary Key": "geography_key (SERIAL)"},
        {"Table": "dim_transaction_status", "Type": "Dimension", "Grain": "1 Status Flag", "Row Count": "2", "Primary Key": "status_key (SERIAL)"},
        {"Table": "fact_sales", "Type": "Fact (Transactional)", "Grain": "1 Line Item per Invoice", "Row Count": "536,350", "Primary Key": "sales_key (BIGINT)"},
        {"Table": "fact_daily_country_summary", "Type": "Fact (Aggregated OLAP)", "Grain": "1 Country per Day", "Row Count": "1,669", "Primary Key": "summary_key (INT)"}
    ])
    st.table(meta_df)

st.markdown("---")
st.markdown("<center style='color:#94a3b8;'>© 2026 DSI463 Final Project: Data Model in Digital Era | Thammasat University | Ploykroang Kongwathananukul (6624650351)</center>", unsafe_allow_html=True)
