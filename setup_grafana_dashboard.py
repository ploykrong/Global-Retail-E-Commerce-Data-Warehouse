import requests
import json
import psycopg2

GRAFANA_URL = "http://localhost:3000"
AUTH = ("admin", "admin")
PG_HOST = "retail_postgres"
PG_PORT = 5432
PG_USER = "airflow"
PG_PASS = "airflow"
PG_DB = "retail_dw"

def ensure_preaggregated_tables():
    """Ensure fast pre-aggregated tables exist in PostgreSQL for instant dashboard queries."""
    print("Checking / creating agg_market_basket_top10 in PostgreSQL...")
    conn = psycopg2.connect("postgresql://airflow:airflow@localhost:5432/retail_dw")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agg_market_basket_top10 AS
    SELECT 
        p1.product_name || ' + ' || p2.product_name AS product_pair,
        COUNT(DISTINCT f1.transaction_no) AS co_purchase_count
    FROM fact_sales f1
    JOIN fact_sales f2 ON f1.transaction_no = f2.transaction_no AND f1.product_key < f2.product_key
    JOIN dim_product p1 ON f1.product_key = p1.product_key
    JOIN dim_product p2 ON f2.product_key = p2.product_key
    WHERE f1.quantity > 0 AND f2.quantity > 0
    GROUP BY p1.product_name, p2.product_name
    ORDER BY co_purchase_count DESC
    LIMIT 10;
    """)
    conn.commit()
    conn.close()
    print("Pre-aggregated table verified!")

def setup_grafana():
    ensure_preaggregated_tables()

    # 1. Check Grafana health
    try:
        r = requests.get(f"{GRAFANA_URL}/api/health", auth=AUTH, timeout=5)
        if r.status_code != 200:
            print("Grafana is not healthy or unreachable:", r.text)
            return
    except Exception as e:
        print("Cannot connect to Grafana:", e)
        return

    # 2. Check / Update DataSource
    ds_payload = {
        "name": "Retail DW PostgreSQL",
        "type": "grafana-postgresql-datasource",
        "access": "proxy",
        "url": f"{PG_HOST}:{PG_PORT}",
        "user": PG_USER,
        "database": PG_DB,
        "secureJsonData": {
            "password": PG_PASS
        },
        "jsonData": {
            "sslmode": "disable",
            "postgresVersion": 1800
        },
        "isDefault": True
    }

    r_list = requests.get(f"{GRAFANA_URL}/api/datasources", auth=AUTH)
    existing_ds = [d for d in r_list.json() if d["name"] == "Retail DW PostgreSQL"]
    
    if existing_ds:
        ds_id = existing_ds[0]["id"]
        ds_uid = existing_ds[0]["uid"]
        print(f"DataSource exists (ID: {ds_id}, UID: {ds_uid}). Updating...")
        requests.put(f"{GRAFANA_URL}/api/datasources/{ds_id}", json=ds_payload, auth=AUTH)
    else:
        print("Creating DataSource...")
        r_create = requests.post(f"{GRAFANA_URL}/api/datasources", json=ds_payload, auth=AUTH)
        ds_uid = r_create.json()["datasource"]["uid"]

    # 3. Create Multi-Question Executive Dashboard
    dashboard_json = {
        "dashboard": {
            "id": None,
            "uid": "retail-dw-dashboard",
            "title": "Global Retail Data Warehouse & Executive Dashboard",
            "tags": ["retail", "dsi463", "data-warehouse", "executive"],
            "timezone": "browser",
            "schemaVersion": 39,
            "version": 2,
            "refresh": "30s",
            "time": {
                "from": "2018-12-01T00:00:00.000Z",
                "to": "2019-12-31T23:59:59.000Z"
            },
            "panels": [
                # =============================================================
                # ROW 1: EXECUTIVE KPIS (Answers Q1 & Q12)
                # =============================================================
                {
                    "id": 1,
                    "title": "Total Net Revenue (£)",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": "SELECT ROUND(SUM(net_amount)::numeric, 2) AS \"Net Revenue\" FROM fact_sales;",
                        "format": "table"
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "colorMode": "value",
                        "graphMode": "none"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyGBP",
                            "color": {"mode": "fixed", "fixedColor": "green"}
                        }
                    }
                },
                {
                    "id": 2,
                    "title": "Total Completed Orders",
                    "type": "stat",
                    "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": "SELECT COUNT(DISTINCT transaction_no) AS \"Completed Orders\" FROM fact_sales WHERE quantity > 0;",
                        "format": "table"
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "colorMode": "value",
                        "graphMode": "none"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "color": {"mode": "fixed", "fixedColor": "blue"}
                        }
                    }
                },
                {
                    "id": 3,
                    "title": "Return Loss Amount (£)",
                    "type": "stat",
                    "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": "SELECT ROUND(SUM(return_amount)::numeric, 2) AS \"Return Loss\" FROM fact_sales;",
                        "format": "table"
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "colorMode": "value",
                        "graphMode": "none"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyGBP",
                            "color": {"mode": "fixed", "fixedColor": "red"}
                        }
                    }
                },
                {
                    "id": 4,
                    "title": "Repeat Buyer Revenue Share (%)",
                    "type": "stat",
                    "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    ROUND((SUM(CASE WHEN c.total_orders > 1 THEN f.net_amount ELSE 0 END) * 100.0 / NULLIF(SUM(f.net_amount), 0))::numeric, 2) AS "Repeat Buyer Share %"
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key;""",
                        "format": "table"
                    }],
                    "options": {
                        "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                        "colorMode": "value",
                        "graphMode": "none"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "color": {"mode": "fixed", "fixedColor": "purple"}
                        }
                    }
                },

                # =============================================================
                # ROW 2: TIME SERIES & TOP PRODUCTS (Answers Q5, Q1, Q2, Q10)
                # =============================================================
                {
                    "id": 9,
                    "title": "Monthly Sales Trend & Return Loss",
                    "type": "timeseries",
                    "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    DATE_TRUNC('month', d.full_date)::timestamp AS "time",
    ROUND(SUM(f.net_amount)::numeric, 2) AS "Net Revenue (£)",
    ROUND(SUM(f.return_amount)::numeric, 2) AS "Return Loss (£)"
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY 1
ORDER BY "time" ASC;""",
                        "format": "table"
                    }],
                    "options": {
                        "tooltip": {"mode": "multi", "sort": "desc"},
                        "legend": {
                            "displayMode": "table",
                            "placement": "bottom",
                            "values": ["sum", "mean", "max"]
                        }
                    },
                    "fieldConfig": {
                        "defaults": {
                            "custom": {
                                "drawStyle": "line",
                                "lineInterpolation": "smooth",
                                "lineWidth": 2,
                                "fillOpacity": 15,
                                "showPoints": "always",
                                "pointSize": 5
                            },
                            "unit": "currencyGBP"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Net Revenue (£)"},
                                "properties": [
                                    {"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}},
                                    {"id": "custom.fillOpacity", "value": 20}
                                ]
                            },
                            {
                                "matcher": {"id": "byName", "options": "Return Loss (£)"},
                                "properties": [
                                    {"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}},
                                    {"id": "custom.lineWidth", "value": 1.5}
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": 5,
                    "title": "Top 10 Products by Revenue & Return Loss",
                    "type": "barchart",
                    "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    p.product_name AS "Product",
    ROUND(SUM(f.net_amount)::numeric, 2) AS "Net Revenue (£)",
    ROUND(SUM(f.return_amount)::numeric, 2) AS "Return Loss (£)"
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY "Net Revenue (£)" DESC
LIMIT 10;""",
                        "format": "table"
                    }],
                    "options": {
                        "orientation": "horizontal",
                        "xTickLabelRotation": 0,
                        "showValue": "always"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyGBP"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Net Revenue (£)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]
                            },
                            {
                                "matcher": {"id": "byName", "options": "Return Loss (£)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}]
                            }
                        ]
                    }
                },

                # =============================================================
                # ROW 3: RFM SEGMENTS & INTERNATIONAL MARKETS (Answers Q4, Q12, Q3)
                # =============================================================
                {
                    "id": 6,
                    "title": "Customer RFM Segments: Revenue & Retention Risk",
                    "type": "barchart",
                    "gridPos": {"x": 0, "y": 12, "w": 12, "h": 8},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    c.customer_segment AS "Segment",
    ROUND((SUM(f.net_amount) / 1000000.0)::numeric, 2) AS "Net Revenue (£M)",
    COUNT(DISTINCT c.customer_key) AS "Customer Count"
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_segment != 'Guest / Unregistered'
GROUP BY c.customer_segment
ORDER BY "Net Revenue (£M)" DESC;""",
                        "format": "table"
                    }],
                    "options": {
                        "orientation": "horizontal",
                        "showValue": "always"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Net Revenue (£M)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}]
                            },
                            {
                                "matcher": {"id": "byName", "options": "Customer Count"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "purple"}}]
                            }
                        ]
                    }
                },
                {
                    "id": 7,
                    "title": "Top 5 International Markets Outside UK & Wholesale AOV",
                    "type": "barchart",
                    "gridPos": {"x": 12, "y": 12, "w": 12, "h": 8},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    g.country_name AS "Country",
    ROUND(SUM(f.net_amount)::numeric, 2) AS "Net Revenue (£)",
    ROUND((SUM(f.net_amount) / NULLIF(COUNT(DISTINCT f.transaction_no), 0))::numeric, 2) AS "AOV (£)"
FROM fact_sales f
JOIN dim_geography g ON f.geography_key = g.geography_key
WHERE g.country_name != 'United Kingdom'
GROUP BY g.country_name
ORDER BY "Net Revenue (£)" DESC
LIMIT 5;""",
                        "format": "table"
                    }],
                    "options": {
                        "orientation": "auto",
                        "showValue": "always"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyGBP"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Net Revenue (£)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]
                            },
                            {
                                "matcher": {"id": "byName", "options": "AOV (£)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}}]
                            }
                        ]
                    }
                },

                # =============================================================
                # ROW 4: CATEGORY PERFORMANCE & MARKET BASKET AFFINITY (Answers Q6, Q8, Q11)
                # =============================================================
                {
                    "id": 8,
                    "title": "Product Category Performance & Price Tier Revenue",
                    "type": "barchart",
                    "gridPos": {"x": 0, "y": 20, "w": 12, "h": 8},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    p.category_name AS "Category",
    ROUND((SUM(f.net_amount) / 1000000.0)::numeric, 2) AS "Net Revenue (£M)",
    ROUND((SUM(f.return_amount) * 100.0 / NULLIF(SUM(f.gross_amount), 0))::numeric, 2) AS "Return Rate (%)",
    ROUND(AVG(f.unit_price)::numeric, 2) AS "Avg Unit Price (£)"
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY "Net Revenue (£M)" DESC;""",
                        "format": "table"
                    }],
                    "options": {
                        "orientation": "horizontal",
                        "showValue": "always"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Net Revenue (£M)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]
                            },
                            {
                                "matcher": {"id": "byName", "options": "Return Rate (%)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}]
                            },
                            {
                                "matcher": {"id": "byName", "options": "Avg Unit Price (£)"},
                                "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}]
                            }
                        ]
                    }
                },
                {
                    "id": 10,
                    "title": "Market Basket Affinity: Top Cross-Selling Product Pairs",
                    "type": "barchart",
                    "gridPos": {"x": 12, "y": 20, "w": 12, "h": 8},
                    "datasource": {"type": "grafana-postgresql-datasource", "uid": ds_uid},
                    "targets": [{
                        "rawSql": """SELECT 
    product_pair AS "Product Pair",
    co_purchase_count AS "Co-Purchase Count"
FROM agg_market_basket_top10
ORDER BY co_purchase_count ASC;""",
                        "format": "table"
                    }],
                    "options": {
                        "orientation": "horizontal",
                        "showValue": "always"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "color": {"mode": "fixed", "fixedColor": "purple"}
                        }
                    }
                }
            ]
        },
        "overwrite": True
    }

    print("Deploying Multi-Question Executive Dashboard to Grafana...")
    r_dash = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        json=dashboard_json,
        auth=AUTH
    )

    if r_dash.status_code == 200:
        dash_url = r_dash.json().get("url", "/d/retail-dw-dashboard")
        full_url = f"{GRAFANA_URL}{dash_url}"
        print("=" * 70)
        print("Grafana Multi-Question Dashboard Successfully Deployed!")
        print(f"Direct URL: {full_url}")
        print("=" * 70)
        return full_url
    else:
        print("Failed to deploy dashboard:", r_dash.text)
        return None

if __name__ == '__main__':
    setup_grafana()
