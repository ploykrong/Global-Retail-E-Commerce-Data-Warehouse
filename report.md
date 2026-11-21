**หัวข้อโครงงาน:** ระบบคลังข้อมูลและแดชบอร์ดอัจฉริยะวิเคราะห์ธุรกรรมการค้าระดับโลก  
*(Global Retail & E-Commerce Data Warehouse and Executive Intelligence Dashboard)*  

---

## 1. โจทย์ ที่มา และแนวคิด (Business Problem & Objectives)

### 1.1 ที่มาและปัญหา (Business Problem)
ในยุคดิจิทัล ธุรกิจค้าปลีกและอีคอมเมิร์ซ (Retail & E-Commerce) ระดับข้ามชาติต้องเผชิญกับปริมาณธุรกรรม (Sales Transactions) มหาศาลในแต่ละวัน ข้อมูลการสั่งซื้อ การยกเลิก/คืนสินค้า ข้อมูลลูกค้า และข้อมูลสินค้า มักถูกจัดเก็บอยู่ในฐานข้อมูลเชิงธุรกรรม (OLTP) หรือไฟล์บันทึกประวัติการขายที่กระจัดกระจาย

จากการวิเคราะห์ชุดข้อมูลประวัติธุรกรรมการขายจริงกว่า **536,350 รายการ** ครอบคลุม **38 ประเทศทั่วโลก** พบประเด็นปัญหาทางธุรกิจที่สำคัญ 4 ประการ:
1. **การขาดระบบรวมศูนย์ข้อมูลหลายมิติ (Lack of Centralized Multi-Dimensional Model):** ระบบฐานข้อมูลเดิมไม่เอื้อต่อการวิเคราะห์เชิงลึกแบบ Cross-functional เช่น การเชื่อมโยงพฤติกรรมการซื้อซ้ำของลูกค้า เข้ากับหมวดหมู่สินค้า ฤดูกาล และประเทศคู่ค้า
2. **ปัญหาการยกเลิกและคืนสินค้า (High Return & Cancellation Losses):** มีรายการยกเลิกหรือคืนสินค้ากว่า 8,585 รายการ สร้างความเสียหายต่อกระแสเงินสดกว่า 2.68 ล้านปอนด์ (£2.68M) โดยองค์กรขาดระบบเฝ้าระวังเพื่อระบุหาสาเหตุรากเหง้า (Root Cause) ของสินค้าที่มีอัตราการคืนผิดปกติ
3. **การสูญเสียลูกค้าและขาดการแบ่งกลุ่มลูกค้าเชิงคุณค่า (Customer Churn & Ineffective Segmentation):** องค์กรไม่ทราบว่ากลุ่มลูกค้าใดคือผู้สร้างรายได้หลัก (High-Value Customers) และกลุ่มใดกำลังจะสูญหาย (At-Risk / Churn) ขาดมิติการวิเคราะห์ RFM (Recency, Frequency, Monetary)
4. **ความล่าช้าในการออกรายงานสำหรับผู้บริหาร (Slow Analytical Query Performance):** การรันคำสั่งวิเคราะห์สรุปยอดขายบนตาราง Transaction ดั้งเดิมขนาด 500,000+ แถว ใช้เวลานานและส่งผลกระทบต่อระบบปฏิบัติการหลัก

การพัฒนา **Data Warehouse** ตามระเบียบวิธี Dimensional Modeling (Kimball Star Schema) ร่วมกับ **Automated ETL Pipeline** และ **Interactive Executive Dashboard** จึงเป็นหัวใจสำคัญในการยกระดับองค์กรสู่การขับเคลื่อนด้วยข้อมูล (Data-Driven Organization)

### 1.2 วัตถุประสงค์ของโครงงาน (Project Objectives)
1. **ออกแบบและพัฒนาแบบจำลองข้อมูล (Data Model):** สร้างสถาปัตยกรรมคลังข้อมูลแบบ **Kimball Star Schema** ที่มีตารางข้อเท็จจริง (Fact Table) และตารางมิติ (Dimension Tables) ที่เชื่อมโยงกันอย่างสมบูรณ์ รองรับการขยายตัวและประสิทธิภาพการค้นคืนสูงสุด
2. **พัฒนาระบบ Automated ETL Pipeline:** ใช้ Python และ Apache Airflow 3 ในการดึง แปลง จัดการข้อมูลสูญหาย (Missing Data) จัดกลุ่มหมวดหมู่สินค้าอัตโนมัติ และโหลดเข้าสู่ Data Warehouse อย่างมีประสิทธิภาพ
3. **กำหนดและตอบคำถามเชิงวิเคราะห์ (Competency Questions) อย่างน้อย 10 ข้อ (ครอบคลุม 12 มิติ):** กำหนดคำถามทางธุรกิจและพัฒนาคำสั่ง SQL ค้นคืนฐานข้อมูล (Database Queries) ที่แม่นยำและรวดเร็ว
4. **พัฒนาต้นแบบแอปพลิเคชันและแดชบอร์ด (Data-Driven Application Prototype):** สร้าง Interactive Web Dashboard ผ่าน Streamlit พร้อม Dockerization Stack เพื่อให้ผู้บริหารและทีมนักวิเคราะห์สามารถติดตามสถานะธุรกิจและรันคำสั่งวิเคราะห์ได้แบบเรียลไทม์

### 1.3 คำถามเชิงวิเคราะห์ 12 ข้อ (Competency Questions: CQ1 - CQ12)
1. **CQ1 (Executive KPIs & Net Revenue):** ผลประกอบการภาพรวม ยอดขายสุทธิ (Net Revenue), จำนวนคำสั่งซื้อสำเร็จ, และอัตราการยกเลิก/คืนสินค้า (Return Rate %) มีมูลค่าเท่าใด?
2. **CQ2 (Top 10 Products & Pareto Share):** สินค้า 10 อันดับแรกที่สร้างรายได้สุทธิสูงสุดคือรายการใด และมีสัดส่วนรายได้คิดเป็นกี่เปอร์เซ็นต์ของรายได้รวม (Pareto Principle)?
3. **CQ3 (Top 5 International Markets & AOV):** ตลาดต่างประเทศ 5 อันดับแรกที่มีมูลค่าการสั่งซื้อสุทธิสูงสุดนอกสหราชอาณาจักรคือประเทศใด และมีมูลค่าเฉลี่ยต่อคำสั่งซื้อ (AOV) เป็นอย่างไร?
4. **CQ4 (Customer Segmentation via RFM):** การแบ่งกลุ่มลูกค้าตามพฤติกรรมการซื้อ (RFM: Champions, Loyal, At Risk, Lost) มีการกระจายตัวของจำนวนลูกค้าและมูลค่ารายได้ในแต่ละกลุ่มอย่างไร?
5. **CQ5 (Monthly Trend & Seasonality Impact):** แนวโน้มยอดขายสุทธิและจำนวนคำสั่งซื้อรายเดือนมีทิศทางอย่างไร และช่วงเทศกาลวันหยุดไตรมาส 4 (Q4 Holiday Season) ส่งผลต่อยอดขายอย่างไร?
6. **CQ6 (Product Category Performance & Return Rate):** กลุ่มหมวดหมู่สินค้าใดสร้างรายได้หลัก และหมวดหมู่ใดมีอัตราการคืนสินค้าสูงที่สุดที่ต้องเฝ้าระวังด้านการควบคุมคุณภาพ?
7. **CQ7 (Peak Day of Week & Shopping Behavior):** วันใดในสัปดาห์ที่ลูกค้าสั่งซื้อสินค้าหนาแน่นที่สุด เพื่อการวางแผนบริหารกำลังคนในคลังสินค้าและแคมเปญการตลาด?
8. **CQ8 (Basket Size & Price Tier Contribution):** สัดส่วนรายได้ตามระดับราคาสินค้า (Budget, Mid-range, Premium, Luxury) มีลักษณะอย่างไร?
9. **CQ9 (Top 10 High-Value VIP Customers):** ลูกค้า VIP 10 อันดับแรกที่มียอดการใช้จ่ายสะสมสูงสุดคือใคร ประเทศใด และมียอดซื้อสะสมเท่าใด?
10. **CQ10 (Cancellation & Return Root-Cause Analysis):** สินค้า 10 รายการที่มีมูลค่าความสูญเสียจากการยกเลิกหรือคืนสินค้าสูงสุดคือรายการใด และมีสัดส่วนการคืนเทียบกับยอดขายเท่าใด?
11. **CQ11 (Market Basket Affinity & Co-Purchased Pairs):** สินค้าคู่ใดที่ถูกสั่งซื้อร่วมกันบ่อยที่สุดในคำสั่งซื้อเดียวกัน เพื่อนำไปจัดโปรโมชั่น Bundle หรือ Cross-selling?
12. **CQ12 (First-Time vs Repeat Buyer Contribution):** สัดส่วนรายได้จากลูกค้าใหม่เทียบกับลูกค้าซื้อซ้ำในแต่ละไตรมาสเป็นอย่างไร สะท้อนความภักดีของฐานลูกค้า (Retention) หรือไม่?

---

## 2. แหล่งข้อมูลที่เลือกใช้ (Data Sources & Data Profiling)

โครงงานนี้ใช้ชุดข้อมูลธุรกรรมการขายปลีกระดับสากล (`Sales Transaction v.4a.csv`) ซึ่งมีขนาด 43 MB ประกอบด้วยประวัติการทำธุรกรรมจริงกว่าครึ่งล้านรายการ

### 2.1 ตารางสรุปคุณสมบัติข้อมูลดิบ (Data Profiling Summary)

| ฟิลด์ข้อมูล (Field) | ชนิดข้อมูลเดิม | ข้อมูลสูญหาย (Null) | จำนวนค่าที่ไม่ซ้ำ (Cardinality) | คำอธิบายและความหมายทางธุรกิจ |
| :--- | :--- | :--- | :--- | :--- |
| **TransactionNo** | Text / String | 0 (0%) | 23,204 รหัส | เลขที่ใบเสร็จคำสั่งซื้อ (หากขึ้นต้นด้วย 'C' หมายถึงการยกเลิก/คืนสินค้า) |
| **Date** | Text (MM/DD/YYYY) | 0 (0%) | 305 วัน | วันที่เกิดธุรกรรม (ช่วง 01/12/2018 ถึง 09/12/2019) |
| **ProductNo** | Text / Alphanumeric | 0 (0%) | 3,768 รหัส | รหัสสินค้าประจำแคตตาล็อก |
| **ProductName** | Text | 0 (0%) | 3,768 รายการ | ชื่อและคำอธิบายรายละเอียดของสินค้า |
| **Price** | Decimal (Float) | 0 (0%) | 530 ระดับราคา | ราคาต่อหน่วย (£5.13 ถึง £660.62) ค่าเฉลี่ย £12.66 |
| **Quantity** | Integer | 0 (0%) | 510 ค่า | ปริมาณสินค้า (ค่าบวก = ซื้อสำเร็จ, ค่าลบ = คืนสินค้า) |
| **CustomerNo** | Float / Numeric | 55 รายการ (<0.01%) | 4,738 รหัสลูกค้า | รหัสประจำตัวลูกค้าผู้สั่งซื้อ |
| **Country** | Text | 0 (0%) | 38 ประเทศ | ประเทศปลายทางของคำสั่งซื้อ |

### 2.2 กฎการทำความสะอาดและแปลงข้อมูล (Data Cleaning & Quality Rules)
1. **การจัดการ Missing Customer ID:** ฟิลด์ `CustomerNo` ที่เป็นค่าว่างจำนวน 55 รายการ ถูกแปลงเข้าสู่รหัส Surrogate `'GUEST'` (รหัสลูกค้าพิเศษ: Walk-in / Unregistered Guest) เพื่อป้องกันปัญหา Referential Integrity Violation ในคลังข้อมูล
2. **การระบุสถานะธุรกรรม (Transaction Status Flagging):** คัดแยกธุรกรรมที่ขึ้นต้นด้วยตัวอักษร 'C' หรือมีค่า `Quantity < 0` เป็นประเภท `'CANCELLED'` และธุรกรรมปกติเป็น `'COMPLETED'`
3. **การคำนวณตัวชี้วัดรายได้ (Revenue Metric Calculation):**
   * $\text{Gross Amount} = \text{CASE WHEN Quantity} > 0 \text{ THEN Quantity} \times \text{Price ELSE } 0 \text{ END}$
   * $\text{Return Amount} = \text{CASE WHEN Quantity} < 0 \text{ THEN } |\text{Quantity}| \times \text{Price ELSE } 0 \text{ END}$
   * $\text{Net Amount} = \text{Quantity} \times \text{Price}$
4. **การสกัดหมวดหมู่สินค้าอัตโนมัติ (Rule-Based NLP Product Categorization):** เนื่องจากข้อมูลดิบไม่มีคอลัมน์ Category จึงได้พัฒนาโมดูลสกัด Keyword จากชื่อสินค้า เช่น 'TOTE', 'BAG' $\rightarrow$ Bags & Luggage, 'CHRISTMAS', 'T-LIGHT' $\rightarrow$ Holiday & Seasonal, 'MUG', 'BOWL' $\rightarrow$ Kitchen & Dining เป็นต้น รวม 9 หมวดหมู่อย่างสมดุล
5. **การคำนวณคะแนนลูกค้า (Customer RFM Scoring):** คำนวณ Recency (จำนวนวันนับจากสั่งซื้อครั้งล่าสุด), Frequency (จำนวนคำสั่งซื้อรวม), และ Monetary (ยอดใช้จ่ายสุทธิ) เพื่อจัดกลุ่มลูกค้า 6 กลุ่ม

---

## 3. การออกแบบ Data Warehouse (Architecture & Star Schema)

### 3.1 สถาปัตยกรรมแบบจำลองข้อมูล (Kimball Star Schema Architecture)

โครงงานเลือกใช้สถาปัตยกรรม **Star Schema** ร่วมกับ **Aggregated Summary Fact Table** ตามระเบียบวิธีของ Ralph Kimball ประกอบด้วย Fact Table จำนวน 2 ตาราง และ Dimension Tables จำนวน 5 ตาราง:

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
|     country, customer_seg   |          |     status_name_th          |
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

### 3.2 รายละเอียดตารางมิติ (Dimension Tables)
1. **`dim_date` (Conformed Calendar Dimension):**
   * **ระดับความละเอียด (Grain):** 1 วันในปฏิทิน
   * **Surrogate Key:** `date_key` รูปแบบตัวเลข `YYYYMMDD` (เช่น `20191209`)
   * **แอตทริบิวต์:** `full_date`, `day`, `month`, `month_name_en`, `month_name_th`, `quarter`, `year`, `day_of_week`, `day_name_en`, `is_weekend`, `season`
   * **จำนวนข้อมูล:** 1,461 แถว (ครอบคลุมปี 2018 ถึง 2021)
2. **`dim_customer` (Customer Profile & RFM Dimension):**
   * **ระดับความละเอียด:** 1 ลูกค้าที่ไม่ซ้ำกัน
   * **Surrogate Key:** `customer_key` (SERIAL / Auto-increment)
   * **Natural Key:** `customer_no`
   * **แอตทริบิวต์เชิงวิเคราะห์:** `customer_segment` (VIP Champions, Loyal Customers, Potential Loyalists, At Risk, Lost, Regular), `total_orders`, `total_spend`, `recency_days`, `first_purchase_date`, `last_purchase_date`
   * **จำนวนข้อมูล:** 4,739 แถว
3. **`dim_product` (Product Catalog Dimension):**
   * **ระดับความละเอียด:** 1 รหัสสินค้าในแคตตาล็อก
   * **Surrogate Key:** `product_key`
   * **Natural Key:** `product_no`
   * **แอตทริบิวต์:** `product_name`, `category_name`, `price_tier` (Budget, Mid-range, Premium, Luxury), `avg_unit_price`
   * **จำนวนข้อมูล:** 3,768 แถว
4. **`dim_geography` (Market Geography Dimension):**
   * **ระดับความละเอียด:** 1 ประเทศปลายทาง
   * **Surrogate Key:** `geography_key`
   * **แอตทริบิวต์:** `country_name` (UNIQUE), `region` (Western Europe, Asia-Pacific, Americas, Middle East, Africa), `market_type` (Domestic vs International), `currency_code`
   * **จำนวนข้อมูล:** 38 แถว
5. **`dim_transaction_status` (Status Dimension):**
   * **ระดับความละเอียด:** 1 สถานะคำสั่งซื้อ
   * **Surrogate Key:** `status_key`
   * **แอตทริบิวต์:** `status_code` ('COMPLETED', 'CANCELLED'), `status_name_th`, `is_return` (BOOLEAN)
   * **จำนวนข้อมูล:** 2 แถว

### 3.3 รายละเอียดตารางข้อเท็จจริง (Fact Tables)
1. **`fact_sales` (Detailed Transaction Line Item Fact):**
   * **Grain (ระดับความละเอียด):** 1 รายการสินค้า (Line Item) ในแต่ละใบสั่งซื้อ
   * **Primary Key:** `sales_key` (BIGSERIAL / Auto-increment)
   * **Foreign Keys:** `date_key`, `customer_key`, `product_key`, `geography_key`, `status_key`
   * **Measures (หน่วยวัด):** `quantity`, `unit_price`, `gross_amount`, `return_amount`, `net_amount`
   * **จำนวนข้อมูล:** 536,350 แถว
2. **`fact_daily_country_summary` (Aggregated OLAP Fact):**
   * **Grain:** 1 ประเทศ ณ 1 วันที่
   * **Measures:** `total_orders`, `total_units_sold`, `total_units_returned`, `gross_revenue`, `return_loss`, `net_revenue`, `unique_customers`
   * **จำนวนข้อมูล:** 1,669 แถว

---

## 4. การออกแบบและการทำงานของ ETL Pipeline

ระบบ ETL Pipeline ได้รับการออกแบบตามหลักการ **Enterprise-Grade Data Engineering**:

### 4.1 ขั้นตอนการทำงาน (ETL Process Flow)
1. **Extract:** ดึงข้อมูลดิบจาก `Sales Transaction v.4a.csv` เข้าสู่ Memory โดยใช้ Pandas Chunking Technique
2. **Cleanse & Validate:**
   * ตรวจสอบความถูกต้องของวันที่ (ISO Date Parsing)
   * เติมค่า Surrogate ให้กับลูกค้าที่ไม่ได้ลงทะเบียน (`CustomerNo` Null $\rightarrow$ `'GUEST'`)
   * คำนวณสถานะ `CANCELLED` และค่า `gross_amount`, `return_amount`, `net_amount`
3. **Transform Dimensions:**
   * สกัดหมวดหมู่สินค้า 9 กลุ่มด้วย Regular Expressions & Keyword Extraction
   * คำนวณโมเดล RFM และตัดเกณฑ์จัดกลุ่มลูกค้า (Customer Segmentation)
   * แมปปิ้งกลุ่มประเทศและภูมิภาคทางภูมิศาสตร์ (Region & Domestic/International)
4. **Load to Data Warehouse:**
   * โหลดตาราง Dimensions ก่อนตามลำดับความสัมพันธ์
   * สร้าง In-memory Lookup Hash Tables เพื่อแปลง Natural Keys เป็น Surrogate Keys
   * โหลดตาราง `fact_sales` แบบ Chunk-based Bulk Loading
   * คำนวณ Aggregation และโหลดเข้าสู่ `fact_daily_country_summary`
5. **Index Creation & Optimization:** สร้าง B-Tree Indexes บน Foreign Keys ทุกตัว เพื่อรองรับ High-Concurrency Star Joins

### 4.2 การควบคุมการทำงานผ่าน Apache Airflow 3 (Orchestration)
* **DAG ID:** `retail_data_warehouse_pipeline`
* **Schedule Interval:** `0 2 * * *` (ประมวลผลทุกวัน เวลา 02:00 น.)
* **Task Dependency Graph:**
  ```
  [start_pipeline] 
         |
         v
  [extract_clean_sales]
         |
         +-----------------------+-----------------------+
         |                       |                       |
         v                       v                       v
  [load_dim_geography]    [load_dim_product]      [load_dim_customer]
         |                       |                       |
         +-----------------------+-----------------------+
         |
         v
  [load_fact_sales]
         |
         v
  [load_fact_daily_summary]
         |
         v
  [data_quality_audit]
         |
         v
  [end_pipeline]
  ```

---

## 5. ผลการทำงานและการทดสอบความถูกต้องของระบบ (Data Quality & Performance)

การรันระบบ ETL บนชุดข้อมูล 536,350 รายการผ่านสคริปต์ `setup_database.py` ประสบความสำเร็จอย่างสมบูรณ์:
* **ความเร็วในการประมวลผล:** ประมวลผลและโหลดข้อมูล 536,350 รายการ พร้อมสร้างดัชนี เสร็จสิ้นภายใน **12.27 วินาที**
* **ขนาดไฟล์ฐานข้อมูล:** 66.57 MB (ประหยัดพื้นที่จัดเก็บและบีบอัดดัชนีอย่างมีประสิทธิภาพ)
* **การตรวจสอบ Referential Integrity:** ไม่พบ Foreign Key กำพร้า (Orphan Rows) ความถูกต้อง 100%
* **การตรวจสอบผลรวมตัวเลข (Reconciliation Check):**
  * Gross Revenue: **£62,965,974.34**
  * Return Loss Amount: **£2,685,950.08**
  * Net Revenue: **£60,280,024.26** (ตรงกับผลรวมยอดขายสุทธิของข้อมูลดิบทุกประการ)

---

## 6. ผลลัพธ์การตอบโจทย์ Competency Questions 12 ข้อ พร้อมคำค้นคืนฐานข้อมูล

### CQ1: ภาพรวมผลประกอบการ ยอดขายสุทธิ และอัตราการคืนสินค้า
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * ธุรกรรมทั้งหมด 23,204 คำสั่งซื้อ (สั่งซื้อสำเร็จ 19,790 บิล, ยกเลิก/คืน 3,414 บิล)
  * ยอดขายรวมสุทธิอยู่ที่ **£60,280,024.26** (60.28 ล้านปอนด์)
  * มูลค่าความเสียหายจากการคืนสินค้าอยู่ที่ **£2,685,950.08** (คิดเป็น Return Rate 4.27%)
  * มูลค่าคำสั่งซื้อเฉลี่ย (AOV) สูงถึง **£3,045.98 ต่อบิล**

---

### CQ2: สินค้า 10 อันดับแรกที่สร้างรายได้สูงสุดและสัดส่วนตามกฎพาเรโต
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  1. `Popcorn Holder` (รหัส 22197): ขายได้ 56,450 ชิ้น สร้างรายได้ **£583,286.51**
  2. `World War 2 Gliders Asstd Designs` (รหัส 84077): ขายได้ 53,847 ชิ้น สร้างรายได้ **£557,170.43**
  3. `Paper Craft Little Birdie` (รหัส 23843): สร้างรายได้ **£501,359.05**
  4. `Cream Hanging Heart T-Light Holder` (รหัส 85123A): ขายได้ 35,378 ชิ้น สร้างรายได้ **£451,401.70**
  5. `Assorted Colour Bird Ornament` (รหัส 84879): ขายได้ 36,445 ชิ้น สร้างรายได้ **£420,743.70**
  * **ข้อเสนอแนะเชิงกลยุทธ์:** สินค้ากลุ่ม Top 10 เป็นตัวขับเคลื่อนกระแสเงินสดหลัก ต้องรักษาระดับ Safety Stock เพื่อป้องกันภาวะสินค้าขาดสต็อก (Stockout)

---

### CQ3: ตลาดต่างประเทศ 5 อันดับแรกนอกสหราชอาณาจักรและมูลค่าเฉลี่ยต่อบิล
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  1. **Netherlands (เนเธอร์แลนด์):** ยอดขายสุทธิ **£2,147,811.39** (97 คำสั่งซื้อ) มี AOV สูงที่สุดถึง **£22,142.39 ต่อบิล** และมี Return Rate ต่ำมากเพียง 0.17%
  2. **EIRE (ไอร์แลนด์):** ยอดขายสุทธิ **£1,660,645.07** (332 คำสั่งซื้อ, AOV £5,001.94)
  3. **Germany (เยอรมนี):** ยอดขายสุทธิ **£1,350,265.40** (587 คำสั่งซื้อ, AOV £2,300.28)
  4. **France (ฝรั่งเศส):** ยอดขายสุทธิ **£1,316,880.98** (463 คำสั่งซื้อ, AOV £2,844.24)
  5. **Australia (ออสเตรเลีย):** ยอดขายสุทธิ **£988,756.35** (73 คำสั่งซื้อ, AOV £13,544.61)
  * **ข้อเสนอแนะเชิงกลยุทธ์:** ลูกค้าต่างประเทศในกลุ่มเนเธอร์แลนด์และออสเตรเลียมีพฤติกรรมการสั่งซื้อแบบ B2B ล็อตใหญ่ ควรจัดทำสัญญาสิทธิพิเศษด้านการขนส่งระหว่างประเทศและ Credit Term เพื่อรักษาฐานลูกค้านี้

---

### CQ4: การแบ่งกลุ่มลูกค้าตามพฤติกรรมการซื้อ (RFM Segmentation)
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * กลุ่ม **VIP Champions:** มีจำนวน 1,101 ราย (สัดส่วน 23.23%) แต่สร้างรายได้สูงถึง **£40,028,590.51 คิดเป็น 66.4% ของรายได้ทั้งบริษัท** มีความถี่ในการสั่งซื้อเฉลี่ย 13 ครั้งต่อปี และซื้อล่าสุดเฉลี่ย 17 วัน
  * กลุ่ม **At Risk Customers:** มี 1,032 ราย ยอดใช้จ่ายรวม £5.53M ขาดการสั่งซื้อไปแล้วเฉลี่ย 225 วัน
  * กลุ่ม **Loyal Customers:** 538 ราย มียอดใช้จ่ายรวม £5.25M สั่งซื้อเฉลี่ย 5 ครั้ง
  * **ข้อเสนอแนะเชิงกลยุทธ์:** ต้องจัดทีม Key Account Manager ดูแลกลุ่ม VIP Champions โดยตรง และเร่งทำแคมเปญ Win-Back มอบข้อเสนอพิเศษให้กลุ่ม At Risk ก่อนจะกลายเป็น Lost Customers

---

### CQ5: แนวโน้มยอดขายรายเดือนและผลกระทบของเทศกาลวันหยุด (Seasonality)
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * ยอดขายรายเดือนช่วงต้นปี (มกราคม - เมษายน 2019) ทรงตัวอยู่ในระดับ £3.3M - £4.3M
  * ยอดขายเติบโตอย่างก้าวกระโดดตั้งแต่เดือนกันยายน และแตะระดับสูงสุดใน **เดือนพฤศจิกายน 2019 สูงถึง £8,012,476.35** (2,866 คำสั่งซื้อ, 672,897 ชิ้น) สูงกว่าช่วงเดือนกุมภาพันธ์กว่า 2.4 เท่า
  * ปัจจัยขับเคลื่อนมาจากเทศกาล Black Friday, Cyber Monday และการสต็อกสินค้าก่อนวันคริสต์มาส

---

### CQ6: การสร้างรายได้และอัตราการคืนสินค้าจำแนกตามหมวดหมู่สินค้า
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * หมวดหมู่ที่สร้างรายได้สูงสุดคือ **Gifts & General Merchandise** (£18.23M, Return Rate 2.51%) และ **Home Decor & Furnishing** (£10.74M, Return Rate 2.98%)
  * หมวดหมู่ที่มีอัตราการคืนสินค้าสูงสุดคือ **Home Storage & Containers สูงถึง 10.45%** (มูลค่าคืน £1,118,655.45) รองลงมาคือ **Toys & Children (8.32%)**
  * **ข้อเสนอแนะเชิงกลยุทธ์:** สินค้ากลุ่มกล่อง ลิ้นชัก และภาชนะเก็บของ มีความเสี่ยงต่อการแตกหักระหว่างการขนส่ง ต้องทบทวนกระบวนการแพ็กเกจจิ้งเพื่อลดความสูญเสีย

---

### CQ7: พฤติกรรมการสั่งซื้อตามวันในสัปดาห์ (Day of Week)
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * วันที่มีการสั่งซื้อและยอดขายสูงสุดคือ **วันพฤหัสบดี (Thursday)** 3,982 คำสั่งซื้อ สร้างรายได้ **£12,830,517.20** ตามด้วยวันพุธ (£11.16M) และวันอังคาร (£11.13M)
  * ข้อมูลไม่มีการสั่งซื้อในวันเสาร์ บ่งบอกถึงพฤติกรรมการสั่งซื้อของกลุ่มลูกค้าธุรกิจและร้านค้าปลีกย่อยที่บริหารงานในวันทำการ

---

### CQ8: การมีส่วนร่วมของระดับราคาสินค้า (Price Tiers)
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * สินค้าระดับ **Mid-range (£10–25)** สร้างรายได้มหาศาลถึง **£48,740,790.39 หรือคิดเป็น 80.86% ของรายได้รวม** จากปริมาณสินค้ากว่า 3.84 ล้านชิ้น
  * สินค้าระดับ Budget (<£10) มีสัดส่วน 12.38% (£7.46M) ขณะที่กลุ่ม Luxury (>£50) มีสัดส่วน 2.50% (£1.51M)

---

### CQ9: ลูกค้า VIP 10 อันดับแรกที่มียอดใช้จ่ายสะสมสูงสุด
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  1. ลูกค้ารหัส **14646 (Netherlands):** ยอดซื้อสะสม **£1,273,388.94** (77 ออเดอร์, ซื้อเฉลี่ยครั้งละ £16,537.52)
  2. ลูกค้ารหัส **18102 (United Kingdom):** ยอดซื้อสะสม **£1,032,154.51** (62 ออเดอร์)
  3. ลูกค้ารหัส **12415 (Australia):** ยอดซื้อสะสม **£895,267.24** (24 ออเดอร์)
  * กลุ่มท็อป 10 สร้างมูลค่ารวมกันกว่า **£8.49M หรือประมาณ 14.1% ของรายได้ทั้งบริษัท**

---

### CQ10: สินค้า 10 รายการที่มีมูลค่าการยกเลิก/คืนสินค้าสูงสุด
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  1. `Medium Ceramic Top Storage Jar` (รหัส 23166): มีการคืนสินค้าสูงถึง **74,494 ชิ้น คิดเป็นมูลค่าสูญเสีย £843,277.96** (อัตราการคืน 48.88%)
  2. `Paper Craft Little Birdie` (รหัส 23843): การยกเลิกล็อตใหญ่ **80,995 ชิ้น มูลค่าสูญเสีย £501,359.05**
  3. `Rotating Silver Angels T-Light Hldr` (รหัส 84347): คืน 9,367 ชิ้น มูลค่าสูญเสีย £96,310.82
  * **ข้อเสนอแนะเชิงกลยุทธ์:** ต้องตรวจสอบสัญญาการสั่งซื้อแบบ B2B ล็อตใหญ่ของสินค้าทั้งสองรายการเพื่อกำหนดเงื่อนไขเงินมัดจำ (Non-refundable Deposit) ป้องกันการยกเลิกออเดอร์ขนาดมหึมา

---

### CQ11: การวิเคราะห์คู่สินค้าที่มักถูกสั่งซื้อร่วมกัน (Market Basket Analysis)
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * สินค้าที่มักซื้อร่วมกันสูงสุด: `Hand Warmer Red Retrospot` กับ `Hand Warmer Union Jack`
  * ชุดทำแยม: `Jam Making Set With Jars` กับ `Jam Making Set Printed`
  * นาฬิกาปลุกเรโทร: `Alarm Clock Bakelike Green` กับ `Alarm Clock Bakelike Red`
  * **ข้อเสนอแนะเชิงกลยุทธ์:** สามารถนำไปตั้งค่าระบบ Recommendation บนหน้าเว็บไซต์ หรือจัดโปรโมชั่นซื้อคู่ในราคาพิเศษ

---

### CQ12: สัดส่วนรายได้จากลูกค้าใหม่เทียบกับลูกค้าซื้อซ้ำรายไตรมาส (Cohort Retention)
* **คำค้นคืนฐานข้อมูล (SQL Query):**
```sql
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
```
* **ผลลัพธ์เชิงวิเคราะห์:**
  * ไตรมาส 4/2018: รายได้จากลูกค้าซื้อซ้ำอยู่ที่ 26.06% (£1.15M)
  * ไตรมาส 1/2019: รายได้จากลูกค้าซื้อซ้ำเพิ่มเป็น 57.77% (£7.10M)
  * ไตรมาส 2/2019: รายได้จากลูกค้าซื้อซ้ำเพิ่มเป็น 80.33% (£10.17M)
  * ไตรมาส 4/2019: รายได้จากลูกค้าซื้อซ้ำพุ่งสูงถึง **86.56% (£15.25M)**
  * **ข้อสรุปเชิงกลยุทธ์:** ธุรกิจมีอัตรา Customer Retention ที่แข็งแกร่งอย่างยิ่ง รายได้กว่า 86% มาจากฐานลูกค้าประจำที่กลับมาซื้อซ้ำอย่างต่อเนื่อง

---

## 7. ต้นแบบแอปพลิเคชันและการแสดงผลบนแดชบอร์ด (Interactive Dashboard Prototype)

ต้นแบบแดชบอร์ดพัฒนาด้วย **Streamlit** และ **Plotly** เชื่อมต่อโดยตรงกับฐานข้อมูล Data Warehouse รองรับการทำงานทั้งแบบ Local และ Dockerized Container:

### คุณสมบัติเด่นของต้นแบบแอปพลิเคชัน:
1. **Control Center & Interactive Filters:** แถบควบคุมด้านข้างสามารถเลือกช่วงวันที่, ประเทศคู่ค้า (Multiselect), หมวดหมู่สินค้า และสถานะคำสั่งซื้อ
2. **Executive KPI Scorecard:** แสดงตัวชี้วัดหลัก 6 ด้าน พร้อม Delta แสดงอัตราการคืนสินค้า
3. **Competency Questions Explorer:** แท็บเฉพาะที่ให้ผู้ใช้เลือกคำถาม CQ1 ถึง CQ12 ได้จาก Dropdown เพื่อรันคำสั่ง SQL สด ดูผลลัพธ์เป็นตาราง กราฟ Plotly และอ่านบทวิเคราะห์เชิงกลยุทธ์
4. **RFM Segmentation Matrix:** แผนภาพ Treemap และ Scatter Plot วิเคราะห์พฤติกรรมลูกค้าเชิงลึก
5. **Interactive Global Choropleth Map:** แผนที่โลกแสดงการกระจายตัวของรายได้ในแต่ละประเทศ

---

## 8. สรุปผลและประโยชน์ที่ได้รับ (Conclusions & Business Impact)

### 8.1 ทักษะและความรู้ที่ได้รับ (Technical Learnings)
1. **Data Warehouse & Dimensional Modeling:** การออกแบบ Star Schema ตามมาตรฐาน Kimball, การกำหนด Fact Granularity, การใช้งาน Surrogate Keys แทน Natural Keys และการสร้าง Aggregated Fact Tables
2. **Data Pipeline Engineering:** การทำ Data Profiling, การจัดการ Missing Data/Outliers, การสกัดหมวดหมู่สินค้าอัตโนมัติด้วย NLP Rules, และการประมวลผลข้อมูลระดับ 500,000+ แถวได้อย่างรวดเร็วใน 12 วินาที
3. **Advanced Analytical SQL:** การเขียนคำสั่ง SQL ขั้นสูงด้วย Common Table Expressions (CTEs), Window Functions, Conditional Aggregation, และ Self-Joins สำหรับ Market Basket Analysis
4. **Containerization & Airflow Orchestration:** การใช้งาน Docker Compose เชื่อมโยง PostgreSQL, Apache Airflow 3, Streamlit Dashboard, และ pgAdmin

### 8.2 ประโยชน์ต่อการนำไปใช้งานจริง (Real-World Business Impact)
* **การลดต้นทุนจากสินค้าคืน (Return Loss Mitigation):** ระบบแจ้งเตือนสินค้าที่มีอัตราการคืนสูง เช่น รหัส 23166 ช่วยให้ฝ่ายปฏิบัติการและคลังสินค้าปรับปรุงบรรจุภัณฑ์และเจรจาสัญญากับคู่ค้าได้ทันท่วงที ประหยัดต้นทุนได้หลายแสนปอนด์ต่อปี
* **การเพิ่ม Customer Lifetime Value (LTV):** การระบุกลุ่ม VIP Champions และ At-Risk ผ่านโมเดล RFM ช่วยให้ฝ่ายการตลาดจัดแคมเปญรักษาฐานลูกค้าที่สร้างรายได้กว่า 66% ได้อย่างตรงเป้าหมาย
* **การขยายตลาดต่างประเทศ (Export Market Strategy):** ข้อมูลเชิงลึกชี้ชัดว่าตลาดเนเธอร์แลนด์และออสเตรเลียมียอดสั่งซื้อเฉลี่ยสูงกว่า UK ถึง 5-7 เท่า เป็นโอกาสสำคัญในการขยายศูนย์กระจายสินค้าในยุโรปและเอเชียแปซิฟิก
