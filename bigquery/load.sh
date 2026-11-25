#!/usr/bin/env bash
# Step 6a - load the data that is indexed in Elasticsearch into a BigQuery table.
#
# Prereqs:  Google Cloud SDK installed  (gcloud + bq),  `gcloud auth login`,  a GCP project.
# A free BigQuery *sandbox* project is enough (batch loads are allowed; tables expire after 60 days).
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?export PROJECT_ID=your-gcp-project-id first}"
DATASET="ecommerce"
TABLE="sales"
LOCATION="US"

# 1) export Elasticsearch -> CSV   (bq load cannot read Elasticsearch directly)
python3 scripts/export_es_to_csv.py es_export.csv

# 2) create the dataset (ignore the error if it already exists)
bq --project_id="$PROJECT_ID" --location="$LOCATION" mk --dataset "${PROJECT_ID}:${DATASET}" || true

# 3) load the CSV with an explicit schema (positional args: table, source file, schema file)
bq --project_id="$PROJECT_ID" --location="$LOCATION" load \
   --source_format=CSV --skip_leading_rows=1 --replace \
   "${DATASET}.${TABLE}" ./es_export.csv ./bigquery/schema.json

# 4) verify: row count must equal the Elasticsearch _count (15,796 for the generated dataset)
bq --project_id="$PROJECT_ID" --location="$LOCATION" query --use_legacy_sql=false \
   "SELECT COUNT(*) AS rows_loaded, MIN(order_date) AS first_day, MAX(order_date) AS last_day FROM \`${PROJECT_ID}.${DATASET}.${TABLE}\`"
bq --project_id="$PROJECT_ID" show --schema --format=prettyjson "${DATASET}.${TABLE}" | head -20
