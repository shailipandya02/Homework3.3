# ============================================================================
# Kibana > Dev Tools > Console.  Paste and run each request with the green arrow.
# Create the index with an EXPLICIT mapping BEFORE running Logstash.
# (Best practice: dynamic mapping would turn money into float and every string into text+keyword.)
# ============================================================================

# 0) start clean (safe to re-run the whole lab)
DELETE ecommerce_data

# 1) explicit mapping
PUT ecommerce_data
{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
  "mappings": {
    "properties": {
      "order_id":        { "type": "keyword" },
      "order_date":      { "type": "date" },
      "customer_id":     { "type": "keyword" },
      "customer_name":   { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
      "customer_email":  { "type": "keyword" },
      "country":         { "type": "keyword" },
      "city":            { "type": "keyword" },
      "latitude":        { "type": "float" },
      "longitude":       { "type": "float" },
      "location":        { "type": "geo_point" },
      "product_id":      { "type": "keyword" },
      "product_name":    { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
      "category":        { "type": "keyword" },
      "quantity":        { "type": "integer" },
      "unit_price":      { "type": "scaled_float", "scaling_factor": 100 },
      "discount_pct":    { "type": "integer" },
      "total_amount":    { "type": "scaled_float", "scaling_factor": 100 },
      "payment_method":  { "type": "keyword" },
      "order_status":    { "type": "keyword" },
      "shipping_method": { "type": "keyword" }
    }
  }
}

# ============================================================================
# AFTER Logstash has finished: verify the load (expected: 15,796 documents - one per CSV order line)
# ============================================================================

GET ecommerce_data/_count

# Look at one document: order_date must be a real date, numbers numeric, location a {lat, lon} object
GET ecommerce_data/_search
{ "size": 1 }

# Check the analyzer used by the text field (used in the analyzer query later)
GET ecommerce_data/_analyze
{ "field": "product_name", "text": "Yoga Mat Non-Slip" }
