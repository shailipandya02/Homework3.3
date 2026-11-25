# ============================================================================
# STEP 4 - 12 Elasticsearch searches (rubric needs >= 9)   |   Kibana > Dev Tools > Console
# Parameters exercised: operator, minimum_should_match, analyzer, fuzziness, prefix_length,
# max_expansions, fuzzy_transpositions, bool, range, wildcard, terms / sum / date_histogram /
# cardinality / stats / cumulative_sum / nested aggregations.
# ============================================================================


# ---- Q1. match (baseline, default operator OR) ----------------------------------------------
# Any product name containing "wireless" OR "headphones"; BM25 ranks docs with both terms first.
GET ecommerce_data/_search
{
  "size": 3,
  "track_total_hits": true,
  "_source": ["order_id", "product_name", "category", "total_amount"],
  "query": { "match": { "product_name": "wireless headphones" } }
}


# ---- Q2. match + operator "and" -------------------------------------------------------------
# Every term must be present -> far fewer hits than Q1.
GET ecommerce_data/_search
{
  "size": 3,
  "track_total_hits": true,
  "_source": ["order_id", "product_name", "total_amount"],
  "query": {
    "match": { "product_name": { "query": "wireless headphones", "operator": "and" } }
  }
}


# ---- Q3. match + minimum_should_match -------------------------------------------------------
# 4 query terms, 75% => at least 3 must match. Only "Bluetooth Speaker Waterproof" has 3 of the 4.
GET ecommerce_data/_search
{
  "size": 3,
  "track_total_hits": true,
  "_source": ["product_name", "total_amount"],
  "query": {
    "match": {
      "product_name": {
        "query": "bluetooth wireless speaker waterproof",
        "minimum_should_match": "75%"
      }
    }
  }
}


# ---- Q4a. analyzer - field's own (standard) analyzer: NO stemming -> 0 hits ------------------
# The index holds the token "mat" (from "Yoga Mat Non-Slip"); the query token is "mats".
GET ecommerce_data/_search
{
  "size": 0,
  "track_total_hits": true,
  "query": { "match": { "product_name": { "query": "mats" } } }
}

# ---- Q4b. analyzer - query-time "english" analyzer stems "mats" -> "mat" -> hits ------------
GET ecommerce_data/_search
{
  "size": 2,
  "track_total_hits": true,
  "_source": ["product_name", "category"],
  "query": { "match": { "product_name": { "query": "mats", "analyzer": "english" } } }
}

# (Optional) see exactly what each analyzer does to the text
GET _analyze
{ "analyzer": "english", "text": "mats" }


# ---- Q5. fuzziness: "AUTO" tolerates typos (0 edits for 1-2 chars, 1 for 3-5, 2 for 6+) -----
# "blutooth" (missing e) and "hedphones" (missing a) still find "Wireless Bluetooth Headphones".
GET ecommerce_data/_search
{
  "size": 3,
  "track_total_hits": true,
  "_source": ["product_name"],
  "query": {
    "match": {
      "product_name": { "query": "blutooth hedphones", "operator": "and", "fuzziness": "AUTO" }
    }
  }
}


# ---- Q6a. fuzzy_transpositions = true (default) + prefix_length + max_expansions -------------
# "headhpones" has two adjacent letters swapped (p<->h). A transposition counts as ONE edit,
# so fuzziness 1 is enough -> hits.
GET ecommerce_data/_search
{
  "size": 2,
  "track_total_hits": true,
  "_source": ["product_name"],
  "query": {
    "match": {
      "product_name": {
        "query": "headhpones",
        "fuzziness": 1,
        "prefix_length": 2,
        "max_expansions": 50,
        "fuzzy_transpositions": true
      }
    }
  }
}

# ---- Q6b. same query with fuzzy_transpositions = false -> a swap now costs TWO edits -> 0 hits -
GET ecommerce_data/_search
{
  "size": 2,
  "track_total_hits": true,
  "_source": ["product_name"],
  "query": {
    "match": {
      "product_name": {
        "query": "headhpones",
        "fuzziness": 1,
        "prefix_length": 2,
        "max_expansions": 50,
        "fuzzy_transpositions": false
      }
    }
  }
}


# ---- Q7. range (date + numeric) inside a bool filter, sorted -------------------------------
# Black-Friday week 2025, order lines worth >= 100. filter context = no scoring, cacheable.
GET ecommerce_data/_search
{
  "size": 5,
  "track_total_hits": true,
  "sort": [ { "total_amount": "desc" } ],
  "_source": ["order_id", "order_date", "product_name", "quantity", "discount_pct", "total_amount"],
  "query": {
    "bool": {
      "filter": [
        { "range": { "order_date": { "gte": "2025-11-24", "lte": "2025-11-30" } } },
        { "range": { "total_amount": { "gte": 100 } } }
      ]
    }
  }
}


# ---- Q8. bool: must + filter + must_not + should ---------------------------------------------
# Delivered Electronics order lines mentioning "bluetooth", quantity >= 2, NOT paid by gift card;
# US orders get a relevance boost (should) but are not required.
GET ecommerce_data/_search
{
  "size": 3,
  "track_total_hits": true,
  "_source": ["order_id", "product_name", "quantity", "payment_method", "country"],
  "query": {
    "bool": {
      "must":     [ { "match": { "product_name": "bluetooth" } } ],
      "filter":   [
        { "term":  { "category": "Electronics" } },
        { "term":  { "order_status": "Delivered" } },
        { "range": { "quantity": { "gte": 2 } } }
      ],
      "must_not": [ { "term": { "payment_method": "Gift Card" } } ],
      "should":   [ { "term": { "country": { "value": "United States", "boost": 2 } } } ]
    }
  }
}


# ---- Q9. wildcard (+ terms aggregation to list the distinct products found) ------------------
# Case-insensitive *desk* on the keyword sub-field. NOTE: leading wildcards scan the whole term
# dictionary - fine for a lab, avoid on big indices (use ngrams / wildcard field type instead).
GET ecommerce_data/_search
{
  "size": 0,
  "track_total_hits": true,
  "query": { "wildcard": { "product_name.keyword": { "value": "*desk*", "case_insensitive": true } } },
  "aggs": { "matched_products": { "terms": { "field": "product_name.keyword", "size": 10 } } }
}


# ---- Q10. aggregation: revenue by category (terms + sum/avg sub-aggregations) ----------------
# Net revenue = Delivered + Shipped (Cancelled / Returned excluded).
GET ecommerce_data/_search
{
  "size": 0,
  "query": { "terms": { "order_status": ["Delivered", "Shipped"] } },
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 10, "order": { "revenue": "desc" } },
      "aggs": {
        "revenue":   { "sum": { "field": "total_amount" } },
        "units":     { "sum": { "field": "quantity" } },
        "avg_line":  { "avg": { "field": "total_amount" } }
      }
    }
  }
}


# ---- Q11. aggregation: monthly sales trend (date_histogram + cardinality + cumulative_sum) ----
GET ecommerce_data/_search
{
  "size": 0,
  "query": { "terms": { "order_status": ["Delivered", "Shipped"] } },
  "aggs": {
    "monthly": {
      "date_histogram": { "field": "order_date", "calendar_interval": "month", "format": "yyyy-MM" },
      "aggs": {
        "revenue":            { "sum": { "field": "total_amount" } },
        "orders":             { "cardinality": { "field": "order_id" } },
        "unique_customers":   { "cardinality": { "field": "customer_id" } },
        "cumulative_revenue": { "cumulative_sum": { "buckets_path": "revenue" } }
      }
    }
  }
}


# ---- Q12. nested aggregation: top 5 countries -> order-line stats -> top 3 products each -----
GET ecommerce_data/_search
{
  "size": 0,
  "query": { "terms": { "order_status": ["Delivered", "Shipped"] } },
  "aggs": {
    "by_country": {
      "terms": { "field": "country", "size": 5, "order": { "revenue": "desc" } },
      "aggs": {
        "revenue":     { "sum":   { "field": "total_amount" } },
        "line_stats":  { "stats": { "field": "total_amount" } },
        "top_products": {
          "terms": { "field": "product_name.keyword", "size": 3, "order": { "product_revenue": "desc" } },
          "aggs": { "product_revenue": { "sum": { "field": "total_amount" } } }
        }
      }
    }
  }
}
