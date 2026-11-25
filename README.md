# Homework3.3
End-to-end e-commerce sales analytics: CSV → Logstash → Elasticsearch/Kibana → BigQuery → Databricks SQL. Includes a reproducible synthetic dataset, 12 Elasticsearch queries, BigQuery SQL, and Databricks SQL for customer lifetime value, churn and product recommendations. DATA 226 HW 3.3.

# E-commerce Sales Analytics with ELK, BigQuery and Databricks SQL

A DATA 226 project that follows one e-commerce dataset through three tools: Elasticsearch and
Kibana for search and dashboards, BigQuery for warehouse SQL, and Databricks SQL for customer
lifetime value, churn and product recommendations.

## Pipeline

CSV file → Logstash → Elasticsearch → Kibana
                           ↓ (scroll-API export)
                       BigQuery → Databricks (SQL notebook)

## What is inside

| Path | Purpose |
|---|---|
| `scripts/generate_data.py` | Reproducible synthetic dataset (seed 42) |
| `data/ecommerce_data.csv` | 15,796 order lines, 9,715 orders, 1,800 customers, 63 products, 2024-01-10 to 2025-12-31 |
| `docker-compose.yml` | Elasticsearch, Kibana and Logstash 8.15 (single node, security off, lab use only) |
| `logstash/pipeline/ecommerce.conf` | CSV parsing, date and type conversion, geo_point, idempotent document ids |
| `elasticsearch/01_mapping.es` | Explicit index mapping |
| `elasticsearch/02_queries.es` | 12 queries: match, operator, minimum_should_match, analyzer, fuzziness, fuzzy_transpositions, range, bool, wildcard, aggregations |
| `scripts/export_es_to_csv.py` | Exports the index to CSV with the scroll API |
| `bigquery/` | Schema, load script, and SQL for sales KPIs, monthly trend, top products, RFM segmentation, countries |
| `databricks/ecommerce_analysis.py` | Notebook: joins, window functions, CLV, churn, market-basket recommendations |
| `validation/` | Expected results calculated from the CSV (DuckDB/pandas), to compare against your runs |
| `RUN_GUIDE.md` | Step-by-step guide |

## Quick start

```bash
pip install "elasticsearch>=8,<9" elasticsearch-dsl pandas faker

docker compose up -d elasticsearch kibana        # Kibana: http://localhost:5601
# Kibana > Dev Tools: run elasticsearch/01_mapping.es
docker compose --profile ingest up logstash      # Ctrl+C when the dots stop
# Dev Tools: GET ecommerce_data/_count            # expect 15796

export PROJECT_ID=your-gcp-project-id
bash bigquery/load.sh                             # export from Elasticsearch, load into BigQuery
```

Then run the SQL in `bigquery/queries.sql` and import `databricks/ecommerce_analysis.py`
into Databricks.

## Analyses

- **Search:** relevance, typo tolerance and stemming on product names.
- **Kibana:** sales trend, revenue by category, top products, payment mix, best customers, sales map.
- **BigQuery:** net revenue, cancellation and return impact, month-over-month growth, RFM segments.
- **Databricks:** CLV (historical and predictive), churn by cohort and order count, product recommendations.

## Notes

- The data is synthetic. Findings demonstrate the techniques and say nothing about real customers.
- Category margins in the Databricks notebook are assumptions, not data.
- Churn is defined as no net purchase in the last 90 days.
- Never commit `key.json` (service-account key) or `es_export.csv`.

## Tech stack

Python, Docker Compose, Elasticsearch 8.15, Logstash, Kibana, Google BigQuery, Databricks (Spark SQL).

## Course

DATA 226, Homework 3.3. Developed with help from Claude (Anthropic).
