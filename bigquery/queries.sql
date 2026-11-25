-- =====================================================================================
-- STEP 6b - BigQuery analysis      (Standard SQL)
-- Replace  your-project-id  with your GCP project id (Find/Replace in the console editor).
-- "Net" sales = order_status IN ('Delivered','Shipped')  -> Cancelled and Returned are excluded.
-- =====================================================================================


-- Q1. Total sales KPIs --------------------------------------------------------------------
SELECT
  COUNT(DISTINCT order_id)                                            AS orders,
  COUNT(DISTINCT customer_id)                                         AS customers,
  SUM(quantity)                                                       AS units_sold,
  ROUND(SUM(total_amount), 2)                                         AS net_revenue,
  ROUND(SAFE_DIVIDE(SUM(total_amount), COUNT(DISTINCT order_id)), 2)  AS avg_order_value
FROM `your-project-id.ecommerce.sales`
WHERE order_status IN ('Delivered', 'Shipped');


-- Q2. How much revenue do cancellations and returns remove? (gross -> net bridge) ----------
SELECT
  order_status,
  COUNT(DISTINCT order_id)                                            AS orders,
  ROUND(SUM(total_amount), 2)                                         AS revenue,
  ROUND(100 * SUM(total_amount) / SUM(SUM(total_amount)) OVER (), 1)  AS pct_of_gross
FROM `your-project-id.ecommerce.sales`
GROUP BY order_status
ORDER BY revenue DESC;


-- Q3. Monthly sales trend with month-over-month growth and running total ---------------------
WITH monthly AS (
  SELECT DATE_TRUNC(order_date, MONTH) AS month,
         SUM(total_amount)             AS revenue
  FROM `your-project-id.ecommerce.sales`
  WHERE order_status IN ('Delivered', 'Shipped')
  GROUP BY month
)
SELECT
  month,
  ROUND(revenue, 2)                                                                     AS revenue,
  ROUND(SAFE_DIVIDE(revenue - LAG(revenue) OVER (ORDER BY month),
                    LAG(revenue) OVER (ORDER BY month)) * 100, 1)                       AS mom_growth_pct,
  ROUND(SUM(revenue) OVER (ORDER BY month), 2)                                          AS cumulative_revenue
FROM monthly
ORDER BY month;


-- Q4. Top-10 selling products (by revenue) with category and rank --------------------------
SELECT
  product_name,
  category,
  SUM(quantity)                                         AS units_sold,
  ROUND(SUM(total_amount), 2)                           AS revenue,
  RANK() OVER (ORDER BY SUM(total_amount) DESC)         AS revenue_rank
FROM `your-project-id.ecommerce.sales`
WHERE order_status IN ('Delivered', 'Shipped')
GROUP BY product_id, product_name, category
ORDER BY revenue DESC
LIMIT 10;


-- Q5. Customer segmentation (RFM): recency, frequency, monetary -> named segments -----------
--   R = days since last purchase (as of the last date in the data), F = number of orders, M = net spend.
--   R and F use fixed business thresholds (deterministic); M uses quintiles (NTILE).
WITH ref AS (
  SELECT MAX(order_date) AS as_of FROM `your-project-id.ecommerce.sales`
),
rfm_raw AS (
  SELECT s.customer_id,
         DATE_DIFF(r.as_of, MAX(s.order_date), DAY) AS recency_days,
         COUNT(DISTINCT s.order_id)                  AS frequency,
         SUM(s.total_amount)                         AS monetary
  FROM `your-project-id.ecommerce.sales` AS s
  CROSS JOIN ref AS r
  WHERE s.order_status IN ('Delivered', 'Shipped')
  GROUP BY s.customer_id, r.as_of
),
scored AS (
  SELECT *,
    CASE WHEN recency_days <= 30 THEN 5 WHEN recency_days <= 60 THEN 4
         WHEN recency_days <= 120 THEN 3 WHEN recency_days <= 240 THEN 2 ELSE 1 END AS r_score,
    CASE WHEN frequency >= 10 THEN 5 WHEN frequency >= 6 THEN 4
         WHEN frequency >= 3 THEN 3 WHEN frequency >= 2 THEN 2 ELSE 1 END            AS f_score,
    NTILE(5) OVER (ORDER BY monetary)                                                AS m_score
  FROM rfm_raw
),
segmented AS (
  SELECT *,
    CASE WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
         WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
         WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
         WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
         WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating / Lost'
         ELSE 'Needs Attention' END AS segment
  FROM scored
)
SELECT
  segment,
  COUNT(*)                                                   AS customers,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)           AS pct_of_customers,
  ROUND(AVG(recency_days), 0)                                AS avg_recency_days,
  ROUND(AVG(frequency), 1)                                   AS avg_orders,
  ROUND(SUM(monetary), 2)                                    AS revenue,
  ROUND(100 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS pct_of_revenue
FROM segmented
GROUP BY segment
ORDER BY revenue DESC;


-- Q6. Geographic segmentation: revenue, customers and basket size by country ----------------
SELECT
  country,
  COUNT(DISTINCT customer_id)                                          AS customers,
  COUNT(DISTINCT order_id)                                             AS orders,
  ROUND(SUM(total_amount), 2)                                          AS revenue,
  ROUND(SAFE_DIVIDE(SUM(total_amount), COUNT(DISTINCT order_id)), 2)   AS avg_order_value,
  ROUND(SAFE_DIVIDE(COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id)), 2) AS orders_per_customer
FROM `your-project-id.ecommerce.sales`
WHERE order_status IN ('Delivered', 'Shipped')
GROUP BY country
ORDER BY revenue DESC;
