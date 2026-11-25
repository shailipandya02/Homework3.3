# Databricks reference results (computed with DuckDB on the generated CSV)

Your Databricks output should show the same numbers.


## typed fact table (the "net" flag is computed once and reused everywhere)

| Count |
|---|


## customer dimension (one row per customer)

| Count |
|---|


## product dimension (one row per product)

| Count |
|---|


## third table for a real join: ASSUMED gross-margin % per category (illustrative, not from the CSV)

| Count |
|---|


## sanity check: row counts must match Elasticsearch / BigQuery

| fact_rows | customers | products | as_of_date |
|---|---|---|---|
| 15796 | 1800 | 63 | 2025-12-31 00:00:00 |


## 2.1  JOIN (3 tables) + AGGREGATION + HAVING: revenue and estimated gross profit per category

| category | orders | units | revenue | est_gross_profit | avg_discount_pct |
|---|---|---|---|---|---|
| Sports & Outdoors | 1403 | 2,602.00 | 110,297.50 | 33,089.25 | 5.00 |
| Home & Kitchen | 1513 | 2,428.00 | 85,385.24 | 27,323.28 | 4.30 |
| Office Supplies | 1339 | 2,204.00 | 108,555.61 | 27,138.90 | 4.40 |
| Electronics | 1486 | 3,058.00 | 150,271.44 | 27,048.86 | 4.50 |
| Toys & Games | 1196 | 2,464.00 | 68,442.08 | 23,954.73 | 5.00 |
| Books | 1280 | 2,414.00 | 73,930.21 | 20,700.46 | 4.50 |


## 2.2  JOIN + WINDOW (DENSE_RANK per country) + FILTER on the rank: top-3 customers in every country

| country | rnk | customer_id | customer_name | orders | spend |
|---|---|---|---|---|---|
| Australia | 1 | C00679 | Nancy Baker | 30 | 2,222.74 |
| Australia | 2 | C00372 | Jeremy Johnson | 19 | 2,156.70 |
| Australia | 3 | C00469 | Joseph Wright | 22 | 1,691.95 |
| Canada | 1 | C01479 | Martha Warner | 21 | 2,275.56 |
| Canada | 2 | C00544 | Wendy Rice | 20 | 1,959.01 |
| Canada | 3 | C00307 | Cynthia Diaz | 18 | 1,615.44 |
| France | 1 | C00654 | Michel Leleu | 16 | 2,210.04 |
| France | 2 | C01160 | Guillaume Grégoire | 16 | 2,159.67 |
| France | 3 | C01182 | Frédéric Brunet | 19 | 1,535.17 |
| Germany | 1 | C00512 | Gotthold Koch II | 37 | 3,504.79 |
| Germany | 2 | C01442 | Suse Reuter | 35 | 2,392.15 |
| Germany | 3 | C00254 | Damaris Holsten | 19 | 2,032.43 |
| India | 1 | C00799 | Jeremiah Dave | 26 | 1,993.86 |
| India | 2 | C00564 | Gavin Batta | 12 | 1,848.27 |
| India | 3 | C01682 | Nicholas Goel | 19 | 1,693.99 |
| Japan | 1 | C01267 | Asuka Mori | 10 | 1,600.33 |
| Japan | 2 | C01466 | Nanami Yoshida | 12 | 1,432.05 |
| Japan | 3 | C00945 | Jun Matsumoto | 14 | 1,431.34 |
| United Kingdom | 1 | C01753 | Natasha Matthews | 23 | 2,312.90 |
| United Kingdom | 2 | C01589 | Frank Taylor | 19 | 2,084.29 |
| United Kingdom | 3 | C01702 | Katy O'Connor | 16 | 2,031.56 |
| United States | 1 | C00566 | Melissa Cannon | 29 | 2,547.45 |
| United States | 2 | C01762 | Michael Norman | 14 | 2,545.44 |
| United States | 3 | C01026 | Jennifer Ortiz | 36 | 2,253.55 |


## 2.3  WINDOW FRAME + SELF-JOIN: 3-month moving average and year-over-year growth

| month | revenue | moving_avg_3m | yoy_growth_pct |
|---|---|---|---|
| 2024-01-01 00:00:00 | 2,451.20 | 2,451.20 |  |
| 2024-02-01 00:00:00 | 4,446.17 | 3,448.68 |  |
| 2024-03-01 00:00:00 | 6,953.52 | 4,616.96 |  |
| 2024-04-01 00:00:00 | 7,287.73 | 6,229.14 |  |
| 2024-05-01 00:00:00 | 12,756.91 | 8,999.39 |  |
| 2024-06-01 00:00:00 | 14,723.78 | 11,589.47 |  |
| 2024-07-01 00:00:00 | 16,118.38 | 14,533.02 |  |
| 2024-08-01 00:00:00 | 21,255.13 | 17,365.76 |  |
| 2024-09-01 00:00:00 | 19,392.43 | 18,921.98 |  |
| 2024-10-01 00:00:00 | 26,125.46 | 22,257.67 |  |
| 2024-11-01 00:00:00 | 38,253.17 | 27,923.69 |  |
| 2024-12-01 00:00:00 | 38,987.54 | 34,455.39 |  |
| 2025-01-01 00:00:00 | 29,841.49 | 35,694.07 | 1,117.40 |
| 2025-02-01 00:00:00 | 26,454.03 | 31,761.02 | 495.00 |
| 2025-03-01 00:00:00 | 31,098.14 | 29,131.22 | 347.20 |
| 2025-04-01 00:00:00 | 35,685.64 | 31,079.27 | 389.70 |
| 2025-05-01 00:00:00 | 39,475.09 | 35,419.62 | 209.40 |
| 2025-06-01 00:00:00 | 43,728.26 | 39,629.66 | 197.00 |
| 2025-07-01 00:00:00 | 43,564.00 | 42,255.78 | 170.30 |
| 2025-08-01 00:00:00 | 46,688.97 | 44,660.41 | 119.70 |
| 2025-09-01 00:00:00 | 44,016.83 | 44,756.60 | 127.00 |
| 2025-10-01 00:00:00 | 47,407.10 | 46,037.63 | 81.50 |
| 2025-11-01 00:00:00 | 61,426.18 | 50,950.04 | 60.60 |
| 2025-12-01 00:00:00 | 51,793.02 | 53,542.10 | 32.80 |


## 2.4  FILTERING with CASE bands: does a deeper discount sell more units per order line?

| discount_band | order_lines | units | avg_units_per_line | revenue |
|---|---|---|---|---|
| 1) full price | 8228 | 11,361.00 | 1.38 | 429,888.80 |
| 2) 1-10% | 4089 | 5,592.00 | 1.37 | 198,081.21 |
| 3) 11-20% | 1466 | 2,052.00 | 1.40 | 68,378.66 |
| 4) 21% or more | 381 | 522.00 | 1.37 | 13,581.50 |


## 2.5  CONDITIONAL AGGREGATION + JOIN: which categories lose the most orders to cancellations / returns?

| category | order_lines | cancelled | returned | lost_pct |
|---|---|---|---|---|
| Home & Kitchen | 2034 | 115.00 | 120.00 | 11.60 |
| Beauty & Personal Care | 1931 | 110.00 | 110.00 | 11.40 |
| Electronics | 2500 | 139.00 | 134.00 | 10.90 |
| Sports & Outdoors | 2237 | 111.00 | 121.00 | 10.40 |
| Clothing | 1538 | 90.00 | 60.00 | 9.80 |
| Office Supplies | 1821 | 80.00 | 95.00 | 9.60 |
| Toys & Games | 1886 | 88.00 | 87.00 | 9.30 |
| Books | 1849 | 87.00 | 85.00 | 9.30 |


## one row per customer; reused by the CLV and churn queries

| Count |
|---|


## 3.1a  Historical CLV by decile: how concentrated is revenue? (decile 1 = best 10% of customers)

| decile | customers | min_clv | max_clv | avg_clv | pct_of_revenue |
|---|---|---|---|---|---|
| 1 | 177 | 918.54 | 3,504.79 | 1,340.55 | 33.40 |
| 2 | 177 | 621.69 | 909.41 | 748.57 | 18.70 |
| 3 | 177 | 479.14 | 621.39 | 547.00 | 13.60 |
| 4 | 177 | 374.97 | 478.16 | 430.34 | 10.70 |
| 5 | 177 | 282.86 | 374.38 | 326.78 | 8.10 |
| 6 | 177 | 203.48 | 282.27 | 244.01 | 6.10 |
| 7 | 177 | 139.88 | 203.38 | 172.70 | 4.30 |
| 8 | 177 | 87.40 | 139.66 | 111.30 | 2.80 |
| 9 | 177 | 42.75 | 87.15 | 65.50 | 1.60 |
| 10 | 176 | 7.64 | 42.50 | 24.29 | 0.60 |


## 3.1b  Predictive CLV = average order value x orders per year x expected lifetime (years)

| customers | churned_customers | avg_order_value | orders_per_year | annual_churn_hazard | expected_lifetime_years | predicted_clv |
|---|---|---|---|---|---|---|
| 1769 | 865.00 | 81.46 | 8.93 | 0.89 | 1.13 | 820.73 |


## 3.1c  Who and where are the high-value customers? (JOIN to the customer dimension)

| country | customers | avg_clv | avg_orders | churn_pct |
|---|---|---|---|---|
| Germany | 165 | 426.00 | 5.40 | 47.90 |
| France | 112 | 425.49 | 5.30 | 46.40 |
| Australia | 134 | 422.08 | 5.50 | 43.30 |
| Japan | 93 | 413.68 | 5.20 | 49.50 |
| India | 178 | 407.14 | 4.70 | 47.20 |
| United Kingdom | 205 | 403.11 | 5.00 | 47.30 |
| United States | 730 | 389.87 | 4.80 | 50.00 |
| Canada | 152 | 376.59 | 4.40 | 55.30 |


## 3.2a  Overall churn rate

| mature_customers | churned | churn_rate_pct | retention_rate_pct |
|---|---|---|---|
| 1631 | 865.00 | 53.00 | 47.00 |


## 3.2b  Churn by acquisition quarter (cohort view) - are newer cohorts healthier or worse?

| cohort | customers | churned | churn_rate_pct | avg_orders |
|---|---|---|---|---|
| 2024-Q1 | 103 | 73.00 | 70.90 | 7.50 |
| 2024-Q2 | 204 | 147.00 | 72.10 | 7.00 |
| 2024-Q3 | 219 | 140.00 | 63.90 | 6.30 |
| 2024-Q4 | 251 | 150.00 | 59.80 | 5.50 |
| 2025-Q1 | 279 | 133.00 | 47.70 | 5.10 |
| 2025-Q2 | 290 | 126.00 | 43.40 | 4.20 |
| 2025-Q3 | 280 | 95.00 | 33.90 | 2.90 |
| 2025-Q4 | 5 | 1.00 | 20.00 | 1.80 |


## 3.2c  Churn by number of orders placed: is the first repeat purchase the key retention moment?

| order_band | customers | churn_rate_pct |
|---|---|---|
| 1 order (one-time buyer) | 265 | 99.20 |
| 2-3 orders | 486 | 63.00 |
| 4-8 orders | 603 | 39.00 |
| 9+ orders | 277 | 22.00 |


## CREATE OR REPLACE TEMP VIEW product_pairs AS

| Count |
|---|


## 3.3a  Strongest product affinities overall (the bundles are visible: desk setup, fitness, coffee ...)

| product_name | rec_product_name | together | confidence | lift |
|---|---|---|---|---|
| USB-C Charging Hub | Mechanical Gaming Keyboard | 77 | 0.37 | 20.55 |
| Wireless Ergonomic Mouse | Laptop Stand Adjustable | 87 | 0.46 | 20.15 |
| USB-C Charging Hub | Wireless Ergonomic Mouse | 89 | 0.43 | 19.63 |
| Waterproof Rain Jacket | Trail Running Shoes | 111 | 0.52 | 19.33 |
| Portable Power Bank | Bluetooth Speaker Waterproof | 75 | 0.42 | 19.12 |
| Mechanical Gaming Keyboard | Laptop Stand Adjustable | 68 | 0.43 | 19.06 |
| Programmable Coffee Maker | Ground Coffee Dark Roast | 112 | 0.61 | 18.78 |
| Wireless Bluetooth Headphones | Bluetooth Speaker Waterproof | 76 | 0.41 | 18.64 |
| USB-C Charging Hub | Laptop Stand Adjustable | 88 | 0.42 | 18.62 |
| Trail Running Shoes | Insulated Hiking Backpack | 105 | 0.45 | 18.54 |
| Programmable Coffee Maker | Insulated Travel Mug | 76 | 0.41 | 17.48 |
| Waterproof Rain Jacket | Camping Tent 2-Person | 84 | 0.39 | 17.45 |
| Portable Power Bank | Phone Case Shockproof | 95 | 0.53 | 17.39 |
| Camping Tent 2-Person | Insulated Hiking Backpack | 82 | 0.42 | 17.27 |
| Mechanical Gaming Keyboard | Wireless Ergonomic Mouse | 58 | 0.37 | 16.95 |


## 3.3b  Top-3 recommendations per product (ROW_NUMBER per product) for four example products

| product_name | rank | rec_product_name | together | confidence | lift |
|---|---|---|---|---|---|
| Ergonomic Office Chair | 1 | Smart LED Desk Lamp | 121 | 0.46 | 15.30 |
| Ergonomic Office Chair | 2 | Standing Desk Converter | 102 | 0.39 | 14.64 |
| Ergonomic Office Chair | 3 | Desk Organizer Bamboo | 120 | 0.46 | 14.25 |
| Programmable Coffee Maker | 1 | Ground Coffee Dark Roast | 112 | 0.61 | 18.78 |
| Programmable Coffee Maker | 2 | Insulated Travel Mug | 76 | 0.41 | 17.48 |
| Wireless Bluetooth Headphones | 1 | Bluetooth Speaker Waterproof | 76 | 0.41 | 18.64 |
| Wireless Bluetooth Headphones | 2 | Phone Case Shockproof | 96 | 0.52 | 16.91 |
| Wireless Bluetooth Headphones | 3 | Portable Power Bank | 61 | 0.33 | 15.97 |
| Yoga Mat Non-Slip | 1 | Foam Roller | 136 | 0.48 | 14.64 |
| Yoga Mat Non-Slip | 2 | Stainless Steel Water Bottle | 146 | 0.51 | 14.45 |
| Yoga Mat Non-Slip | 3 | Resistance Bands Set | 135 | 0.47 | 13.45 |


## 3.3c  Personalised next-best products for the highest-spending customer:

| customer_id | recommended_product | score | supporting_purchases |
|---|---|---|---|
| C00512 | Resistance Bands Set | 38.32 | 3 |
| C00512 | Trail Running Shoes | 19.33 | 1 |
| C00512 | Camping Tent 2-Person | 17.45 | 1 |
| C00512 | Insulated Hiking Backpack | 16.56 | 1 |
