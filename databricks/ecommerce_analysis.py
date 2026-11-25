# Databricks notebook source
# MAGIC %md
# MAGIC # E-commerce analytics - Databricks SQL (HW 3.3, Step 7)
# MAGIC Import this file via **Workspace > Import** (it is already in Databricks "source" format: one `COMMAND` per cell).
# MAGIC
# MAGIC | Part | Rubric item | Cells |
# MAGIC |---|---|---|
# MAGIC | 7a | Create notebook + connect to the BigQuery dataset (2 pts) | Section 1 |
# MAGIC | 7b | Advanced SQL: aggregation, filtering, joining (4 pts) | Section 2 |
# MAGIC | 7c | Insights: customer lifetime value, churn rate, product recommendations (3 pts) | Section 3 |
# MAGIC
# MAGIC Definitions used throughout: **net sales** = `order_status IN ('Delivered','Shipped')`;
# MAGIC **as-of date** = the last order date in the data (not `current_date()`, so results are reproducible);
# MAGIC **churned** = no net purchase in the 90 days before the as-of date.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Connect to BigQuery (7a)
# MAGIC **Path A - Spark BigQuery connector** (needs a GCP service account with *BigQuery Data Viewer*, *BigQuery Read Session User* and *BigQuery Job User*, and outbound access to Google APIs).
# MAGIC Store the JSON key as a Databricks secret - never paste a key into a notebook:
# MAGIC `databricks secrets create-scope bq` then `databricks secrets put-secret bq sa_key --string-value "$(cat key.json)"`.
# MAGIC
# MAGIC **Path B - fallback** if your workspace cannot reach BigQuery (for example Databricks Free Edition restricts outbound internet access to a short list of domains):
# MAGIC export the table from BigQuery (`bq extract` / console *Export > Download CSV*, or reuse `es_export.csv`), upload it to a Unity Catalog **volume**, and read it from there.
# MAGIC Both paths end with the same temp view `sales_raw`, so every cell below is identical.

# COMMAND ----------

# --- Path A: read directly from BigQuery -------------------------------------------------
import base64

PROJECT_ID = "your-project-id"          # <- change me
USE_BIGQUERY = True                     # set False to use the CSV fallback below

if USE_BIGQUERY:
    key_json = dbutils.secrets.get(scope="bq", key="sa_key")
    creds_b64 = base64.b64encode(key_json.encode("utf-8")).decode("utf-8")
    sales_raw = (spark.read.format("bigquery")
                 .option("credentials", creds_b64)               # base64-encoded service-account JSON
                 .option("parentProject", PROJECT_ID)            # project that is billed for the read
                 .option("table", f"{PROJECT_ID}.ecommerce.sales")
                 .load())
else:
    # --- Path B: CSV uploaded to a Unity Catalog volume (Catalog > your catalog > schema > Create volume > Upload) ---
    sales_raw = (spark.read.option("header", True).option("inferSchema", True)
                 .csv("/Volumes/workspace/default/ecommerce/es_export.csv"))

sales_raw.createOrReplaceTempView("sales_raw")
print("rows read:", sales_raw.count())          # must equal the BigQuery / Elasticsearch count
display(sales_raw.limit(5))

# COMMAND ----------

# MAGIC %sql
# MAGIC -- typed fact table (the "net" flag is computed once and reused everywhere)
# MAGIC CREATE OR REPLACE TEMP VIEW fact_sales AS
# MAGIC SELECT
# MAGIC   order_id,
# MAGIC   CAST(order_date AS DATE)            AS order_date,
# MAGIC   customer_id,
# MAGIC   product_id,
# MAGIC   CAST(quantity AS INT)               AS quantity,
# MAGIC   CAST(unit_price AS DECIMAL(10,2))   AS unit_price,
# MAGIC   CAST(discount_pct AS INT)           AS discount_pct,
# MAGIC   CAST(total_amount AS DECIMAL(12,2)) AS total_amount,
# MAGIC   payment_method,
# MAGIC   order_status,
# MAGIC   shipping_method,
# MAGIC   order_status IN ('Delivered', 'Shipped') AS is_net
# MAGIC FROM sales_raw

# COMMAND ----------

# MAGIC %sql
# MAGIC -- customer dimension (one row per customer)
# MAGIC CREATE OR REPLACE TEMP VIEW dim_customers AS
# MAGIC SELECT customer_id,
# MAGIC        MAX(customer_name)                 AS customer_name,
# MAGIC        MAX(country)                       AS country,
# MAGIC        MAX(city)                          AS city,
# MAGIC        MIN(CAST(order_date AS DATE))      AS first_order_date
# MAGIC FROM sales_raw
# MAGIC GROUP BY customer_id

# COMMAND ----------

# MAGIC %sql
# MAGIC -- product dimension (one row per product)
# MAGIC CREATE OR REPLACE TEMP VIEW dim_products AS
# MAGIC SELECT product_id,
# MAGIC        MAX(product_name)                           AS product_name,
# MAGIC        MAX(category)                               AS category,
# MAGIC        MAX(CAST(unit_price AS DECIMAL(10,2)))      AS list_price
# MAGIC FROM sales_raw
# MAGIC GROUP BY product_id

# COMMAND ----------

# MAGIC %sql
# MAGIC -- third table for a real join: ASSUMED gross-margin % per category (illustrative, not from the CSV)
# MAGIC CREATE OR REPLACE TEMP VIEW category_margin AS
# MAGIC SELECT * FROM (VALUES
# MAGIC   ('Electronics', 0.18), ('Home & Kitchen', 0.32), ('Clothing', 0.45), ('Sports & Outdoors', 0.30),
# MAGIC   ('Beauty & Personal Care', 0.55), ('Books', 0.28), ('Toys & Games', 0.35), ('Office Supplies', 0.25)
# MAGIC ) AS t(category, margin_pct)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- sanity check: row counts must match Elasticsearch / BigQuery
# MAGIC SELECT (SELECT COUNT(*) FROM fact_sales)    AS fact_rows,
# MAGIC        (SELECT COUNT(*) FROM dim_customers) AS customers,
# MAGIC        (SELECT COUNT(*) FROM dim_products)  AS products,
# MAGIC        (SELECT MAX(order_date) FROM fact_sales) AS as_of_date

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Advanced SQL - aggregation, filtering, joining (7b)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2.1  JOIN (3 tables) + AGGREGATION + HAVING: revenue and estimated gross profit per category
# MAGIC SELECT p.category,
# MAGIC        COUNT(DISTINCT f.order_id)                    AS orders,
# MAGIC        SUM(f.quantity)                               AS units,
# MAGIC        ROUND(SUM(f.total_amount), 2)                 AS revenue,
# MAGIC        ROUND(SUM(f.total_amount) * m.margin_pct, 2)  AS est_gross_profit,
# MAGIC        ROUND(AVG(f.discount_pct), 1)                 AS avg_discount_pct
# MAGIC FROM fact_sales f
# MAGIC JOIN dim_products   p ON f.product_id = p.product_id
# MAGIC JOIN category_margin m ON p.category   = m.category
# MAGIC WHERE f.is_net
# MAGIC GROUP BY p.category, m.margin_pct
# MAGIC HAVING SUM(f.total_amount) > 60000
# MAGIC ORDER BY est_gross_profit DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2.2  JOIN + WINDOW (DENSE_RANK per country) + FILTER on the rank: top-3 customers in every country
# MAGIC WITH cust AS (
# MAGIC   SELECT c.country, c.customer_id, c.customer_name,
# MAGIC          COUNT(DISTINCT f.order_id) AS orders,
# MAGIC          SUM(f.total_amount)        AS spend
# MAGIC   FROM fact_sales f
# MAGIC   JOIN dim_customers c ON f.customer_id = c.customer_id
# MAGIC   WHERE f.is_net
# MAGIC   GROUP BY c.country, c.customer_id, c.customer_name
# MAGIC ),
# MAGIC ranked AS (
# MAGIC   SELECT *, DENSE_RANK() OVER (PARTITION BY country ORDER BY spend DESC) AS rnk
# MAGIC   FROM cust
# MAGIC )
# MAGIC SELECT country, rnk, customer_id, customer_name, orders, ROUND(spend, 2) AS spend
# MAGIC FROM ranked
# MAGIC WHERE rnk <= 3
# MAGIC ORDER BY country, rnk

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2.3  WINDOW FRAME + SELF-JOIN: 3-month moving average and year-over-year growth
# MAGIC WITH m AS (
# MAGIC   SELECT CAST(DATE_TRUNC('MONTH', order_date) AS DATE) AS month,
# MAGIC          SUM(total_amount)                             AS revenue
# MAGIC   FROM fact_sales
# MAGIC   WHERE is_net
# MAGIC   GROUP BY 1
# MAGIC )
# MAGIC SELECT cur.month,
# MAGIC        ROUND(cur.revenue, 2)                                                                  AS revenue,
# MAGIC        ROUND(AVG(cur.revenue) OVER (ORDER BY cur.month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3m,
# MAGIC        ROUND(100 * (cur.revenue - prev.revenue) / NULLIF(prev.revenue, 0), 1)                 AS yoy_growth_pct
# MAGIC FROM m cur
# MAGIC LEFT JOIN m prev ON prev.month = ADD_MONTHS(cur.month, -12)
# MAGIC ORDER BY cur.month

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2.4  FILTERING with CASE bands: does a deeper discount sell more units per order line?
# MAGIC SELECT CASE WHEN discount_pct = 0  THEN '1) full price'
# MAGIC             WHEN discount_pct <= 10 THEN '2) 1-10%'
# MAGIC             WHEN discount_pct <= 20 THEN '3) 11-20%'
# MAGIC             ELSE '4) 21% or more' END       AS discount_band,
# MAGIC        COUNT(*)                              AS order_lines,
# MAGIC        SUM(quantity)                         AS units,
# MAGIC        ROUND(AVG(quantity), 2)               AS avg_units_per_line,
# MAGIC        ROUND(SUM(total_amount), 2)           AS revenue
# MAGIC FROM fact_sales
# MAGIC WHERE is_net
# MAGIC GROUP BY 1
# MAGIC ORDER BY 1

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2.5  CONDITIONAL AGGREGATION + JOIN: which categories lose the most orders to cancellations / returns?
# MAGIC SELECT p.category,
# MAGIC        COUNT(*)                                                           AS order_lines,
# MAGIC        SUM(CASE WHEN f.order_status = 'Cancelled' THEN 1 ELSE 0 END)      AS cancelled,
# MAGIC        SUM(CASE WHEN f.order_status = 'Returned'  THEN 1 ELSE 0 END)      AS returned,
# MAGIC        ROUND(100.0 * SUM(CASE WHEN f.order_status IN ('Cancelled', 'Returned') THEN 1 ELSE 0 END) / COUNT(*), 1) AS lost_pct
# MAGIC FROM fact_sales f
# MAGIC JOIN dim_products p ON f.product_id = p.product_id
# MAGIC GROUP BY p.category
# MAGIC ORDER BY lost_pct DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Data insights - customer lifetime value, churn rate, product recommendations (7c)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- one row per customer; reused by the CLV and churn queries
# MAGIC CREATE OR REPLACE TEMP VIEW customer_metrics AS
# MAGIC WITH ref AS (SELECT MAX(order_date) AS as_of FROM fact_sales),
# MAGIC c AS (
# MAGIC   SELECT customer_id,
# MAGIC          MIN(order_date)            AS first_order,
# MAGIC          MAX(order_date)            AS last_order,
# MAGIC          COUNT(DISTINCT order_id)   AS orders,
# MAGIC          SUM(total_amount)          AS revenue
# MAGIC   FROM fact_sales
# MAGIC   WHERE is_net
# MAGIC   GROUP BY customer_id
# MAGIC )
# MAGIC SELECT c.customer_id, c.first_order, c.last_order, c.orders, c.revenue, r.as_of,
# MAGIC        DATEDIFF(r.as_of, c.last_order)  AS days_since_last_order,
# MAGIC        DATEDIFF(r.as_of, c.first_order) AS tenure_days,
# MAGIC        CASE WHEN DATEDIFF(r.as_of, c.last_order) > 90 THEN 1 ELSE 0 END AS churned
# MAGIC FROM c CROSS JOIN ref r

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1 Customer lifetime value (CLV)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.1a  Historical CLV by decile: how concentrated is revenue? (decile 1 = best 10% of customers)
# MAGIC SELECT decile,
# MAGIC        COUNT(*)                                             AS customers,
# MAGIC        ROUND(MIN(revenue), 2)                               AS min_clv,
# MAGIC        ROUND(MAX(revenue), 2)                               AS max_clv,
# MAGIC        ROUND(AVG(revenue), 2)                               AS avg_clv,
# MAGIC        ROUND(100 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_revenue
# MAGIC FROM (SELECT *, NTILE(10) OVER (ORDER BY revenue DESC) AS decile FROM customer_metrics) t
# MAGIC GROUP BY decile
# MAGIC ORDER BY decile

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.1b  Predictive CLV = average order value x orders per year x expected lifetime (years)
# MAGIC --        expected lifetime = 1 / annual churn hazard  (hazard = churned customers / customer-years observed)
# MAGIC WITH expo AS (
# MAGIC   SELECT customer_id, orders, revenue, churned,
# MAGIC          GREATEST(CASE WHEN churned = 1 THEN DATEDIFF(last_order, first_order)
# MAGIC                        ELSE DATEDIFF(as_of, first_order) END, 1) / 365.0 AS exposure_years
# MAGIC   FROM customer_metrics
# MAGIC ),
# MAGIC agg AS (
# MAGIC   SELECT COUNT(*)                    AS customers,
# MAGIC          SUM(churned)                AS churned_customers,
# MAGIC          SUM(revenue)                AS revenue,
# MAGIC          SUM(orders)                 AS orders,
# MAGIC          SUM(exposure_years)         AS customer_years
# MAGIC   FROM expo
# MAGIC )
# MAGIC SELECT customers, churned_customers,
# MAGIC        ROUND(revenue / orders, 2)                                  AS avg_order_value,
# MAGIC        ROUND(orders / customer_years, 2)                           AS orders_per_year,
# MAGIC        ROUND(churned_customers / customer_years, 3)                AS annual_churn_hazard,
# MAGIC        ROUND(customer_years / churned_customers, 2)                AS expected_lifetime_years,
# MAGIC        ROUND((revenue / orders) * (orders / customer_years) * (customer_years / churned_customers), 2) AS predicted_clv
# MAGIC FROM agg

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.1c  Who and where are the high-value customers? (JOIN to the customer dimension)
# MAGIC SELECT c.country,
# MAGIC        COUNT(*)                        AS customers,
# MAGIC        ROUND(AVG(m.revenue), 2)        AS avg_clv,
# MAGIC        ROUND(AVG(m.orders), 1)         AS avg_orders,
# MAGIC        ROUND(100.0 * SUM(m.churned) / COUNT(*), 1) AS churn_pct
# MAGIC FROM customer_metrics m
# MAGIC JOIN dim_customers c ON m.customer_id = c.customer_id
# MAGIC GROUP BY c.country
# MAGIC ORDER BY avg_clv DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.2 Churn rate
# MAGIC Only customers whose **first purchase is at least 90 days before the as-of date** are counted - a customer who joined last week cannot have been inactive for 90 days yet.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.2a  Overall churn rate
# MAGIC SELECT COUNT(*)                                   AS mature_customers,
# MAGIC        SUM(churned)                               AS churned,
# MAGIC        ROUND(100.0 * SUM(churned) / COUNT(*), 1)  AS churn_rate_pct,
# MAGIC        ROUND(100.0 - 100.0 * SUM(churned) / COUNT(*), 1) AS retention_rate_pct
# MAGIC FROM customer_metrics
# MAGIC WHERE tenure_days >= 90

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.2b  Churn by acquisition quarter (cohort view) - are newer cohorts healthier or worse?
# MAGIC SELECT CONCAT(CAST(YEAR(first_order) AS STRING), '-Q', CAST(QUARTER(first_order) AS STRING)) AS cohort,
# MAGIC        COUNT(*)                                   AS customers,
# MAGIC        SUM(churned)                               AS churned,
# MAGIC        ROUND(100.0 * SUM(churned) / COUNT(*), 1)  AS churn_rate_pct,
# MAGIC        ROUND(AVG(orders), 1)                      AS avg_orders
# MAGIC FROM customer_metrics
# MAGIC WHERE tenure_days >= 90
# MAGIC GROUP BY 1
# MAGIC ORDER BY 1

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.2c  Churn by number of orders placed: is the first repeat purchase the key retention moment?
# MAGIC SELECT CASE WHEN orders = 1 THEN '1 order (one-time buyer)'
# MAGIC             WHEN orders <= 3 THEN '2-3 orders'
# MAGIC             WHEN orders <= 8 THEN '4-8 orders'
# MAGIC             ELSE '9+ orders' END                    AS order_band,
# MAGIC        COUNT(*)                                     AS customers,
# MAGIC        ROUND(100.0 * SUM(churned) / COUNT(*), 1)    AS churn_rate_pct
# MAGIC FROM customer_metrics
# MAGIC WHERE tenure_days >= 90
# MAGIC GROUP BY 1
# MAGIC ORDER BY MIN(orders)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.3 Product recommendations - "customers who bought X also bought Y"
# MAGIC Market-basket analysis on net orders. For a pair (X, Y):
# MAGIC **support** = share of all orders containing both; **confidence** = P(Y in order | X in order); **lift** = confidence / P(Y) - above 1 means the products are bought together more often than chance.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW product_pairs AS
# MAGIC WITH basket AS (
# MAGIC   SELECT DISTINCT f.order_id, f.product_id, p.product_name
# MAGIC   FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id
# MAGIC   WHERE f.is_net
# MAGIC ),
# MAGIC tot  AS (SELECT COUNT(DISTINCT order_id) AS n_orders FROM basket),
# MAGIC prod AS (SELECT product_id, COUNT(*) AS n_with FROM basket GROUP BY product_id),
# MAGIC pairs AS (
# MAGIC   SELECT a.product_id AS product_id, a.product_name AS product_name,
# MAGIC          b.product_id AS rec_product_id, b.product_name AS rec_product_name,
# MAGIC          COUNT(*) AS together
# MAGIC   FROM basket a
# MAGIC   JOIN basket b ON a.order_id = b.order_id AND a.product_id <> b.product_id
# MAGIC   GROUP BY a.product_id, a.product_name, b.product_id, b.product_name
# MAGIC )
# MAGIC SELECT p.product_id, p.product_name, p.rec_product_id, p.rec_product_name, p.together,
# MAGIC        ROUND(p.together / t.n_orders, 4)                                    AS support,
# MAGIC        ROUND(p.together / pa.n_with, 3)                                     AS confidence,
# MAGIC        ROUND((p.together / pa.n_with) / (pb.n_with / t.n_orders), 2)        AS lift
# MAGIC FROM pairs p
# MAGIC CROSS JOIN tot t
# MAGIC JOIN prod pa ON p.product_id     = pa.product_id
# MAGIC JOIN prod pb ON p.rec_product_id = pb.product_id
# MAGIC WHERE p.together >= 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.3a  Strongest product affinities overall (the bundles are visible: desk setup, fitness, coffee ...)
# MAGIC SELECT product_name, rec_product_name, together, confidence, lift
# MAGIC FROM product_pairs
# MAGIC WHERE product_id < rec_product_id          -- show each pair once
# MAGIC ORDER BY lift DESC, together DESC
# MAGIC LIMIT 15

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.3b  Top-3 recommendations per product (ROW_NUMBER per product) for four example products
# MAGIC SELECT product_name, rn AS rank, rec_product_name, together, confidence, lift
# MAGIC FROM (
# MAGIC   SELECT *, ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY lift DESC, together DESC) AS rn
# MAGIC   FROM product_pairs
# MAGIC ) t
# MAGIC WHERE rn <= 3
# MAGIC   AND product_name IN ('Wireless Bluetooth Headphones', 'Yoga Mat Non-Slip', 'Programmable Coffee Maker', 'Ergonomic Office Chair')
# MAGIC ORDER BY product_name, rn

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3.3c  Personalised next-best products for the highest-spending customer:
# MAGIC --       sum the lift of partners of everything they already bought, drop items they already own
# MAGIC WITH bought AS (SELECT DISTINCT customer_id, product_id FROM fact_sales WHERE is_net),
# MAGIC top_customer AS (SELECT customer_id FROM customer_metrics ORDER BY revenue DESC LIMIT 1)
# MAGIC SELECT b.customer_id,
# MAGIC        r.rec_product_name                  AS recommended_product,
# MAGIC        ROUND(SUM(r.lift), 2)               AS score,
# MAGIC        COUNT(*)                            AS supporting_purchases
# MAGIC FROM bought b
# MAGIC JOIN top_customer tc ON b.customer_id = tc.customer_id
# MAGIC JOIN product_pairs r ON b.product_id = r.product_id
# MAGIC LEFT JOIN bought owned ON owned.customer_id = b.customer_id AND owned.product_id = r.rec_product_id
# MAGIC WHERE owned.product_id IS NULL
# MAGIC GROUP BY b.customer_id, r.rec_product_name
# MAGIC ORDER BY score DESC
# MAGIC LIMIT 5

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key learnings (fill in with YOUR observations after running the cells)
# MAGIC *
