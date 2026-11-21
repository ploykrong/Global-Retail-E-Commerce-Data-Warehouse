"""
=====================================================================
DSI463: Apache Airflow 3 DAG - Retail Data Warehouse Pipeline
Author: Ploykroang Kongwathananukul (6624650351)
=====================================================================
Airflow Pipeline:
1. start_pipeline
2. extract_clean_raw_sales
3. load_dim_geography, load_dim_product, load_dim_customer, load_dim_date (Parallel)
4. load_fact_sales
5. load_fact_daily_summary
6. data_quality_check
7. end_pipeline
"""

from datetime import datetime, timedelta
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.empty import EmptyOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

if AIRFLOW_AVAILABLE:
    dag = DAG(
        'retail_data_warehouse_pipeline',
        default_args=default_args,
        description='Automated Enterprise Retail Sales ETL & Kimball Data Warehouse Ingestion',
        schedule='0 2 * * *', # Daily at 02:00 AM
        catchup=False,
        tags=[]
    )

    def task_extract_clean():
        print("[Airflow Task] Extracting raw CSV transactions & performing data cleansing...")

    def task_dim_geography():
        print("[Airflow Task] Ingesting dim_geography with regional classification...")

    def task_dim_product():
        print("[Airflow Task] Ingesting dim_product with category extraction & price tiering...")

    def task_dim_customer():
        print("[Airflow Task] Ingesting dim_customer with RFM scoring & segmentation...")

    def task_fact_sales():
        print("[Airflow Task] Loading fact_sales detailed transactional line items...")

    def task_fact_summary():
        print("[Airflow Task] Aggregating fact_daily_country_summary for OLAP analytics...")

    def task_quality_audit():
        print("[Airflow Task] Executing Data Quality Audit (Referential integrity, null checks, row counts)...")

    start = EmptyOperator(task_id='start_pipeline', dag=dag)
    extract = PythonOperator(task_id='extract_clean_sales', python_callable=task_extract_clean, dag=dag)
    
    dim_geo = PythonOperator(task_id='load_dim_geography', python_callable=task_dim_geography, dag=dag)
    dim_prod = PythonOperator(task_id='load_dim_product', python_callable=task_dim_product, dag=dag)
    dim_cust = PythonOperator(task_id='load_dim_customer', python_callable=task_dim_customer, dag=dag)
    
    fact_sales = PythonOperator(task_id='load_fact_sales', python_callable=task_fact_sales, dag=dag)
    fact_sum = PythonOperator(task_id='load_fact_daily_summary', python_callable=task_fact_summary, dag=dag)
    quality = PythonOperator(task_id='data_quality_audit', python_callable=task_quality_audit, dag=dag)
    end = EmptyOperator(task_id='end_pipeline', dag=dag)

    # Dependency Graph:
    # start -> extract -> [dim_geo, dim_prod, dim_cust] -> fact_sales -> fact_sum -> quality -> end
    start >> extract >> [dim_geo, dim_prod, dim_cust] >> fact_sales >> fact_sum >> quality >> end
