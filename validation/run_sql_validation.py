#!/usr/bin/env python3
"""
Dry-run every BigQuery query and every Databricks %sql cell against the same CSV using DuckDB,
after transpiling the dialect with sqlglot (bigquery -> duckdb, databricks -> duckdb).

What this proves : the SQL parses in the target dialect and the LOGIC runs on the data.
What it does not : it is not BigQuery or Databricks itself. Tiny differences (float rounding, tie-breaks
                   on equal values) can occur - compare your cloud results with the reference files
                   it writes, expecting the same figures.
"""
import pathlib, re, sys
import duckdb, sqlglot
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "ecommerce_data.csv"
pd.set_option("display.width", 220, "display.max_columns", 30, "display.max_colwidth", 40)


def fresh_con():
    con = duckdb.connect()
    con.execute(f"CREATE TABLE sales_raw AS SELECT * FROM read_csv_auto('{CSV}', header=true)")
    con.execute("CREATE VIEW sales AS SELECT * FROM sales_raw")
    return con


def run(con, sql, dialect):
    out = sqlglot.transpile(sql, read=dialect, write="duckdb")
    last = None
    for stmt in out:
        res = con.execute(stmt)
        last = res.df() if res.description else None
    return last


def md_table(df, max_rows=20):
    df = df.head(max_rows).copy()
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in df.astype(object).itertuples(index=False):
        lines.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,.2f}" if isinstance(v, float) else str(v)) for v in r) + " |")
    return "\n".join(lines)


failures = 0

# ------------------------------------------------------------------ BigQuery
print("=== BigQuery queries ===")
bq_text = (ROOT / "bigquery" / "queries.sql").read_text().replace("`your-project-id.ecommerce.sales`", "sales")
blocks = [b for b in re.split(r";\s*\n", bq_text) if "SELECT" in b.upper()]
con = fresh_con()
report = ["# BigQuery reference results (computed with DuckDB on the generated CSV)\n",
          "Your BigQuery output should show the same numbers.\n"]
for b in blocks:
    title = re.search(r"--\s*(Q\d+\..*?)(?:-{3,}|$)", b, re.M).group(1).strip()
    try:
        df = run(con, b, "bigquery")
        print(f"OK   {title[:80]:80s} -> {len(df)} rows")
        report += [f"\n## {title}\n", md_table(df, 24), ""]
    except Exception as e:
        failures += 1
        print(f"FAIL {title[:80]}\n     {str(e)[:400]}")
(ROOT / "validation" / "expected_bigquery_results.md").write_text("\n".join(report))

# ------------------------------------------------------------------ Databricks
print("\n=== Databricks notebook %sql cells ===")
nb = (ROOT / "databricks" / "ecommerce_analysis.py").read_text()
cells = nb.split("# COMMAND ----------")
con = fresh_con()
report = ["# Databricks reference results (computed with DuckDB on the generated CSV)\n",
          "Your Databricks output should show the same numbers.\n"]
n = 0
for cell in cells:
    lines = [l for l in cell.strip().splitlines()]
    if not lines or not lines[0].startswith("# MAGIC %sql"):
        continue
    sql = "\n".join(l[len("# MAGIC "):] if l.startswith("# MAGIC ") else "" for l in lines[1:])
    n += 1
    m = re.search(r"--\s*(\d\.\d\w?|one row|typed|customer|product|third|sanity)[^\n]*", sql)
    title = (m.group(0) if m else sql.strip().splitlines()[0])[:110].lstrip("- ").strip()
    try:
        df = run(con, sql, "databricks")
        shown = f"{len(df)} rows" if df is not None else "view created"
        print(f"OK   {title[:85]:85s} -> {shown}")
        if df is not None:
            report += [f"\n## {title}\n", md_table(df, 24), ""]
    except Exception as e:
        failures += 1
        print(f"FAIL {title}\n     {str(e)[:500]}")
(ROOT / "validation" / "expected_databricks_results.md").write_text("\n".join(report))
print(f"\n{n} Databricks SQL cells checked; failures in total: {failures}")
sys.exit(1 if failures else 0)
