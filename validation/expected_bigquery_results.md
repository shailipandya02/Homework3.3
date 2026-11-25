# BigQuery reference results (computed with DuckDB on the generated CSV)

Your BigQuery output should show the same numbers.


## Q1. Total sales KPIs

| orders | customers | units_sold | net_revenue | avg_order_value |
|---|---|---|---|---|
| 8715 | 1769 | 19,527.00 | 709,930.17 | 81.46 |


## Q2. How much revenue do cancellations and returns remove? (gross -> net bridge)

| order_status | orders | revenue | pct_of_gross |
|---|---|---|---|
| Delivered | 8635 | 703,857.09 | 89.00 |
| Cancelled | 508 | 41,975.18 | 5.30 |
| Returned | 492 | 39,305.08 | 5.00 |
| Shipped | 80 | 6,073.08 | 0.80 |


## Q3. Monthly sales trend with month-over-month growth and running total

| month | revenue | mom_growth_pct | cumulative_revenue |
|---|---|---|---|
| 2024-01-01 00:00:00 | 2,451.20 |  | 2,451.20 |
| 2024-02-01 00:00:00 | 4,446.17 | 81.40 | 6,897.37 |
| 2024-03-01 00:00:00 | 6,953.52 | 56.40 | 13,850.89 |
| 2024-04-01 00:00:00 | 7,287.73 | 4.80 | 21,138.62 |
| 2024-05-01 00:00:00 | 12,756.91 | 75.00 | 33,895.53 |
| 2024-06-01 00:00:00 | 14,723.78 | 15.40 | 48,619.31 |
| 2024-07-01 00:00:00 | 16,118.38 | 9.50 | 64,737.69 |
| 2024-08-01 00:00:00 | 21,255.13 | 31.90 | 85,992.82 |
| 2024-09-01 00:00:00 | 19,392.43 | -8.80 | 105,385.25 |
| 2024-10-01 00:00:00 | 26,125.46 | 34.70 | 131,510.71 |
| 2024-11-01 00:00:00 | 38,253.17 | 46.40 | 169,763.88 |
| 2024-12-01 00:00:00 | 38,987.54 | 1.90 | 208,751.42 |
| 2025-01-01 00:00:00 | 29,841.49 | -23.50 | 238,592.91 |
| 2025-02-01 00:00:00 | 26,454.03 | -11.40 | 265,046.94 |
| 2025-03-01 00:00:00 | 31,098.14 | 17.60 | 296,145.08 |
| 2025-04-01 00:00:00 | 35,685.64 | 14.80 | 331,830.72 |
| 2025-05-01 00:00:00 | 39,475.09 | 10.60 | 371,305.81 |
| 2025-06-01 00:00:00 | 43,728.26 | 10.80 | 415,034.07 |
| 2025-07-01 00:00:00 | 43,564.00 | -0.40 | 458,598.07 |
| 2025-08-01 00:00:00 | 46,688.97 | 7.20 | 505,287.04 |
| 2025-09-01 00:00:00 | 44,016.83 | -5.70 | 549,303.87 |
| 2025-10-01 00:00:00 | 47,407.10 | 7.70 | 596,710.97 |
| 2025-11-01 00:00:00 | 61,426.18 | 29.60 | 658,137.15 |
| 2025-12-01 00:00:00 | 51,793.02 | -15.70 | 709,930.17 |


## Q4. Top-10 selling products (by revenue) with category and rank

| product_name | category | units_sold | revenue | revenue_rank |
|---|---|---|---|---|
| Ergonomic Office Chair | Office Supplies | 282.00 | 51,030.00 | 1 |
| Standing Desk Converter | Office Supplies | 256.00 | 36,452.85 | 2 |
| Camping Tent 2-Person | Sports & Outdoors | 217.00 | 24,412.85 | 3 |
| Trail Running Shoes | Sports & Outdoors | 255.00 | 22,939.95 | 4 |
| Waterproof Rain Jacket | Clothing | 239.00 | 20,216.35 | 5 |
| Data Engineering Handbook | Books | 462.00 | 19,943.92 | 6 |
| Strategy Board Game | Toys & Games | 598.00 | 19,371.50 | 7 |
| Building Blocks Set 1000 Pieces | Toys & Games | 499.00 | 19,005.04 | 8 |
| Mastering SQL Analytics | Books | 466.00 | 17,724.04 | 9 |
| Adjustable Dumbbell Pair | Sports & Outdoors | 125.00 | 16,596.60 | 10 |


## Q5. Customer segmentation (RFM): recency, frequency, monetary -> named segments

| segment | customers | pct_of_customers | avg_recency_days | avg_orders | revenue | pct_of_revenue |
|---|---|---|---|---|---|---|
| Champions | 371 | 21.00 | 22.00 | 10.30 | 311,144.71 | 43.80 |
| Loyal | 417 | 23.60 | 49.00 | 4.80 | 165,633.72 | 23.30 |
| At Risk | 360 | 20.40 | 280.00 | 5.50 | 158,059.02 | 22.30 |
| Hibernating / Lost | 390 | 22.00 | 346.00 | 1.40 | 46,185.50 | 6.50 |
| New / Promising | 131 | 7.40 | 36.00 | 1.70 | 17,449.44 | 2.50 |
| Needs Attention | 100 | 5.70 | 89.00 | 1.40 | 11,457.78 | 1.60 |


## Q6. Geographic segmentation: revenue, customers and basket size by country

| country | customers | orders | revenue | avg_order_value | orders_per_customer |
|---|---|---|---|---|---|
| United States | 730 | 3474 | 284,606.14 | 81.92 | 4.76 |
| United Kingdom | 205 | 1017 | 82,636.84 | 81.26 | 4.96 |
| India | 178 | 844 | 72,470.38 | 85.87 | 4.74 |
| Germany | 165 | 887 | 70,289.82 | 79.24 | 5.38 |
| Canada | 152 | 672 | 57,241.06 | 85.18 | 4.42 |
| Australia | 134 | 742 | 56,558.64 | 76.22 | 5.54 |
| France | 112 | 595 | 47,654.97 | 80.09 | 5.31 |
| Japan | 93 | 484 | 38,472.32 | 79.49 | 5.20 |
