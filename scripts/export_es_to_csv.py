#!/usr/bin/env python3
"""
Export the documents indexed in Elasticsearch to a CSV that `bq load` can read.

Why this step exists: `bq load` can read local files, Cloud Storage and a few other sources,
but it CANNOT read from Elasticsearch directly. So the path is
        Elasticsearch  --(this script, scroll API)-->  es_export.csv  --(bq load)-->  BigQuery

Usage:
    pip install "elasticsearch>=8,<9"          # client major version must match the server (8.x)
    python3 export_es_to_csv.py                 # defaults: http://localhost:9200, index ecommerce_data
    ES_URL=http://localhost:9200 ES_INDEX=ecommerce_data python3 export_es_to_csv.py out.csv
"""
import csv
import os
import sys

from elasticsearch import Elasticsearch, helpers

ES_URL = os.getenv("ES_URL", "http://localhost:9200")
INDEX = os.getenv("ES_INDEX", "ecommerce_data")
OUT = sys.argv[1] if len(sys.argv) > 1 else "es_export.csv"

# same column order as bigquery/schema.json
FIELDS = ["order_id", "order_date", "customer_id", "customer_name", "customer_email",
          "country", "city", "latitude", "longitude", "product_id", "product_name", "category",
          "quantity", "unit_price", "discount_pct", "total_amount",
          "payment_method", "order_status", "shipping_method"]

es = Elasticsearch(ES_URL)
expected = es.count(index=INDEX)["count"]

rows = 0
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    writer.writeheader()
    # helpers.scan uses the scroll API, so it streams every document (a plain search stops at 10,000)
    for hit in helpers.scan(es, index=INDEX, query={"query": {"match_all": {}}}, _source=FIELDS, size=2000):
        doc = hit["_source"]
        doc["order_date"] = str(doc["order_date"])[:10]      # "2025-03-14T00:00:00.000Z" -> "2025-03-14"
        writer.writerow({f: doc.get(f) for f in FIELDS})
        rows += 1

print(f"exported {rows:,} documents from '{INDEX}' to {OUT} (index reports {expected:,})")
if rows != expected:
    sys.exit("row count mismatch - do not load this file")
