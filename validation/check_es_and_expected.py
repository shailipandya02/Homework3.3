#!/usr/bin/env python3
"""
1) Syntax-check every request body in elasticsearch/*.es  (Dev Tools console format -> JSON must parse).
2) Recompute, with pandas, what the headline numbers of each Elasticsearch query SHOULD be,
   so you can reconcile your live Kibana results against the source CSV.
   (These are pandas expectations - NOT Elasticsearch output.)
"""
import json, re, sys, pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------ 1. parse console files
def parse_console(path):
    reqs, cur = [], None
    for line in path.read_text().splitlines():
        if re.match(r"^(GET|PUT|POST|DELETE)\s", line):
            if cur: reqs.append(cur)
            cur = {"head": line.strip(), "body": []}
        elif cur is not None and not line.startswith("#"):
            cur["body"].append(line)
        elif line.startswith("#") and cur is not None and "".join(cur["body"]).strip():
            reqs.append(cur); cur = None
    if cur: reqs.append(cur)
    out = []
    for r in reqs:
        body = "\n".join(r["body"]).strip()
        out.append((r["head"], json.loads(body) if body else None))
    return out

n_ok = 0
for f in sorted((ROOT / "elasticsearch").glob("*.es")):
    reqs = parse_console(f)
    n_ok += len(reqs)
    print(f"{f.name}: {len(reqs)} requests, all bodies are valid JSON")
q = parse_console(ROOT / "elasticsearch" / "02_queries.es")
print(f"search requests in 02_queries.es: {len(q)} (+1 _analyze helper)  -> rubric needs >= 9\n")

# ------------------------------------------------------------------ 2. expected values
df = pd.read_csv(ROOT / "data" / "ecommerce_data.csv", parse_dates=["order_date"])
tok = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))      # approx. of the standard analyzer
df["tokens"] = df.product_name.map(tok)
net = df[df.order_status.isin(["Delivered", "Shipped"])]
print(f"ingest check -> GET ecommerce_data/_count should be {len(df):,}\n")

def n(mask): return int(mask.sum())
exp = {}
exp["Q1 match 'wireless headphones' (OR)"] = n(df.tokens.map(lambda t: bool(t & {"wireless", "headphones"})))
exp["Q2 match ... operator AND"] = n(df.tokens.map(lambda t: {"wireless", "headphones"} <= t))
exp["Q3 minimum_should_match 75%"] = n(df.tokens.map(lambda t: len(t & {"bluetooth", "wireless", "speaker", "waterproof"}) >= 3))
exp["Q4a 'mats' standard analyzer"] = n(df.tokens.map(lambda t: "mats" in t))
exp["Q4b 'mats' english analyzer (-> mat)"] = n(df.tokens.map(lambda t: "mat" in t))
exp["Q5 fuzzy 'blutooth hedphones' AND"] = n(df.product_name.str.contains("Bluetooth Headphones"))
exp["Q6a fuzzy_transpositions=true"] = n(df.product_name.str.contains("Headphones"))
exp["Q6b fuzzy_transpositions=false"] = 0
exp["Q7 range BF-week & >=100"] = n(df.order_date.between("2025-11-24", "2025-11-30") & (df.total_amount >= 100))
exp["Q8 bool (bluetooth/Electronics/Delivered/qty>=2/no gift card)"] = n(
    df.tokens.map(lambda t: "bluetooth" in t) & (df.category == "Electronics") & (df.order_status == "Delivered")
    & (df.quantity >= 2) & (df.payment_method != "Gift Card"))
exp["Q9 wildcard *desk*"] = n(df.product_name.str.lower().str.contains("desk"))
print("Expected hit totals (hits.total.value):")
for k, v in exp.items():
    print(f"  {k:62s} {v:>6,}")

print("\nQ10 revenue by category (Delivered+Shipped), descending:")
print(net.groupby("category").agg(revenue=("total_amount", "sum"), units=("quantity", "sum"), avg_line=("total_amount", "mean"),
                                  lines=("total_amount", "size")).sort_values("revenue", ascending=False).round(2).to_string())

print("\nQ11 monthly revenue / distinct orders / distinct customers (first 6 + last 3 months):")
m = net.groupby(net.order_date.dt.strftime("%Y-%m")).agg(revenue=("total_amount", "sum"), orders=("order_id", "nunique"),
                                                         customers=("customer_id", "nunique")).round(2)
m["cumulative"] = m.revenue.cumsum().round(2)
print(pd.concat([m.head(6), m.tail(3)]).to_string())

print("\nQ12 top-5 countries by revenue:")
print(net.groupby("country").total_amount.agg(["sum", "count", "mean", "min", "max"]).sort_values("sum", ascending=False).head(5).round(2).to_string())
