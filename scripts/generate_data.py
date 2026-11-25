#!/usr/bin/env python3
"""
Generate a reproducible synthetic e-commerce dataset (one row per order line).

Why synthetic?  The assignment allows "create your own (explain how you created it)".
Public retail datasets rarely contain what Steps 4-7 need (repeat customers over
2 years for churn/CLV, product bundles for recommendations, geo coordinates for
Kibana Maps, a mix of order statuses), so the generator builds those in on purpose.

Run:  python3 generate_data.py [output.csv]
Seed is fixed (42) so everyone who runs it gets byte-identical output.
"""
import sys
import unicodedata
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
N_CUSTOMERS = 1800
START, END = date(2024, 1, 1), date(2025, 12, 31)
OUT = sys.argv[1] if len(sys.argv) > 1 else "ecommerce_data.csv"

rng = np.random.default_rng(SEED)

# --------------------------------------------------------------------------- geography
CITIES = {
    "United States": [("New York", 40.7128, -74.0060), ("Los Angeles", 34.0522, -118.2437),
                      ("Chicago", 41.8781, -87.6298), ("Houston", 29.7604, -95.3698),
                      ("San Francisco", 37.7749, -122.4194), ("Seattle", 47.6062, -122.3321)],
    "Canada": [("Toronto", 43.6532, -79.3832), ("Vancouver", 49.2827, -123.1207), ("Montreal", 45.5017, -73.5673)],
    "United Kingdom": [("London", 51.5074, -0.1278), ("Manchester", 53.4808, -2.2426), ("Edinburgh", 55.9533, -3.1883)],
    "Germany": [("Berlin", 52.5200, 13.4050), ("Munich", 48.1351, 11.5820), ("Hamburg", 53.5511, 9.9937)],
    "India": [("Mumbai", 19.0760, 72.8777), ("Bengaluru", 12.9716, 77.5946), ("Delhi", 28.6139, 77.2090)],
    "Australia": [("Sydney", -33.8688, 151.2093), ("Melbourne", -37.8136, 144.9631)],
    "France": [("Paris", 48.8566, 2.3522), ("Lyon", 45.7640, 4.8357)],
    "Japan": [("Tokyo", 35.6762, 139.6503), ("Osaka", 34.6937, 135.5023)],
}
COUNTRY_W = {"United States": .42, "Canada": .09, "United Kingdom": .12, "Germany": .09,
             "India": .10, "Australia": .07, "France": .06, "Japan": .05}
LOCALE = {"United States": "en_US", "Canada": "en_CA", "United Kingdom": "en_GB", "Germany": "de_DE",
          "India": "en_IN", "Australia": "en_AU", "France": "fr_FR", "Japan": "ja_JP"}
fakers = {}
for c, loc in LOCALE.items():
    f = Faker(loc)
    f.seed_instance(SEED)
    fakers[c] = f

# --------------------------------------------------------------------------- catalogue
# (product_id, name, category, price)
PRODUCTS = [
    ("P1001", "Wireless Bluetooth Headphones", "Electronics", 79.99),
    ("P1002", "Noise Cancelling Earbuds", "Electronics", 129.00),
    ("P1003", "Smart LED Desk Lamp", "Electronics", 34.50),
    ("P1004", "USB-C Charging Hub", "Electronics", 45.00),
    ("P1005", "Portable Power Bank", "Electronics", 25.99),
    ("P1006", "Mechanical Gaming Keyboard", "Electronics", 89.95),
    ("P1007", "Wireless Ergonomic Mouse", "Electronics", 39.99),
    ("P1008", "4K Action Camera", "Electronics", 199.00),
    ("P1009", "Smart Fitness Tracker", "Electronics", 59.90),
    ("P1010", "Bluetooth Speaker Waterproof", "Electronics", 49.99),
    ("P1011", "Laptop Stand Adjustable", "Electronics", 29.99),
    ("P1012", "Phone Case Shockproof", "Electronics", 14.99),
    ("P1013", "Android Tablet 10 Inch", "Electronics", 219.00),
    ("P1014", "Webcam Full HD 1080p", "Electronics", 54.99),
    ("P2001", "Stainless Steel Water Bottle", "Home & Kitchen", 24.95),
    ("P2002", "Programmable Coffee Maker", "Home & Kitchen", 69.00),
    ("P2003", "Ground Coffee Dark Roast", "Home & Kitchen", 12.99),
    ("P2004", "Insulated Travel Mug", "Home & Kitchen", 18.50),
    ("P2005", "Non-Stick Frying Pan", "Home & Kitchen", 32.00),
    ("P2006", "Chef Knife Set", "Home & Kitchen", 74.99),
    ("P2007", "Digital Air Fryer", "Home & Kitchen", 99.00),
    ("P2008", "Memory Foam Pillow", "Home & Kitchen", 28.00),
    ("P2009", "Scented Soy Candle", "Home & Kitchen", 16.50),
    ("P2010", "Robot Vacuum Cleaner", "Home & Kitchen", 249.00),
    ("P3001", "Organic Cotton T-Shirt", "Clothing", 19.99),
    ("P3002", "Slim Fit Denim Jeans", "Clothing", 49.50),
    ("P3003", "Waterproof Rain Jacket", "Clothing", 89.00),
    ("P3004", "Merino Wool Socks", "Clothing", 14.00),
    ("P3005", "Lightweight Running Shorts", "Clothing", 22.00),
    ("P3006", "Classic Leather Belt", "Clothing", 27.00),
    ("P3007", "Winter Knit Beanie", "Clothing", 12.50),
    ("P3008", "Cozy Fleece Hoodie", "Clothing", 44.99),
    ("P4001", "Yoga Mat Non-Slip", "Sports & Outdoors", 29.99),
    ("P4002", "Resistance Bands Set", "Sports & Outdoors", 17.99),
    ("P4003", "Adjustable Dumbbell Pair", "Sports & Outdoors", 139.00),
    ("P4004", "Trail Running Shoes", "Sports & Outdoors", 94.99),
    ("P4005", "Camping Tent 2-Person", "Sports & Outdoors", 119.00),
    ("P4006", "Insulated Hiking Backpack", "Sports & Outdoors", 64.00),
    ("P4007", "Foam Roller", "Sports & Outdoors", 21.50),
    ("P4008", "Speed Jump Rope", "Sports & Outdoors", 9.99),
    ("P5001", "Vitamin C Face Serum", "Beauty & Personal Care", 26.00),
    ("P5002", "Hydrating Facial Moisturizer", "Beauty & Personal Care", 22.50),
    ("P5003", "Electric Toothbrush", "Beauty & Personal Care", 59.00),
    ("P5004", "Argan Oil Shampoo", "Beauty & Personal Care", 15.99),
    ("P5005", "Mineral Sunscreen SPF 50", "Beauty & Personal Care", 17.00),
    ("P5006", "Beard Trimmer Kit", "Beauty & Personal Care", 36.00),
    ("P6001", "Data Engineering Handbook", "Books", 44.99),
    ("P6002", "Mastering SQL Analytics", "Books", 39.95),
    ("P6003", "The Art of Cooking Basics", "Books", 28.00),
    ("P6004", "Mindfulness Journal", "Books", 14.99),
    ("P6005", "Python Programming Crash Course", "Books", 34.99),
    ("P6006", "Travel Guide Japan", "Books", 21.99),
    ("P7001", "Building Blocks Set 1000 Pieces", "Toys & Games", 39.99),
    ("P7002", "Strategy Board Game", "Toys & Games", 34.00),
    ("P7003", "Remote Control Car", "Toys & Games", 42.50),
    ("P7004", "Jigsaw Puzzle 500 Pieces", "Toys & Games", 15.99),
    ("P7005", "Plush Teddy Bear", "Toys & Games", 19.50),
    ("P8001", "Ergonomic Office Chair", "Office Supplies", 189.00),
    ("P8002", "Standing Desk Converter", "Office Supplies", 149.00),
    ("P8003", "Gel Pen Set 12 Colors", "Office Supplies", 9.50),
    ("P8004", "Hardcover Notebook A5", "Office Supplies", 11.99),
    ("P8005", "Desk Organizer Bamboo", "Office Supplies", 23.99),
    ("P8006", "Whiteboard Markers Pack", "Office Supplies", 8.99),
]
PID = {p[0]: i for i, p in enumerate(PRODUCTS)}
CATEGORIES = sorted({p[2] for p in PRODUCTS})
BY_CAT = {c: [p[0] for p in PRODUCTS if p[2] == c] for c in CATEGORIES}

# Products that tend to be bought together -> gives the recommendation query real signal.
BUNDLES = [
    ["P1011", "P1007", "P1004", "P1006"],   # home-office tech
    ["P4001", "P4002", "P2001", "P4007"],   # fitness
    ["P2002", "P2003", "P2004"],            # coffee
    ["P1001", "P1005", "P1012", "P1010"],   # mobile accessories
    ["P6001", "P6002", "P6005"],            # data books
    ["P8001", "P8002", "P1003", "P8005"],   # desk setup
    ["P3003", "P4006", "P4005", "P4004"],   # outdoors
    ["P5001", "P5002", "P5005"],            # skincare
    ["P7001", "P7004", "P7002"],            # games night
]
BUNDLE_OF = {}
for b in BUNDLES:
    for pid in b:
        BUNDLE_OF.setdefault(pid, []).append(b)

# popularity weight per product: cheaper + random factor
base_w = np.array([(1 / np.sqrt(p[3])) * rng.lognormal(0, 0.45) for p in PRODUCTS])

# --------------------------------------------------------------------------- calendar
days = [START + timedelta(d) for d in range((END - START).days + 1)]
month_w = {1: .90, 2: .85, 3: .95, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.05, 8: 1.0, 9: 1.0, 10: 1.1, 11: 1.5, 12: 1.45}
special = {date(2024, 11, 29): 4.0, date(2025, 11, 28): 4.0,   # Black Friday
           date(2024, 12, 2): 3.0, date(2025, 12, 1): 3.0}     # Cyber Monday
day_w = np.array([month_w[d.month] * (1.25 if d.weekday() >= 5 else 1.0) * special.get(d, 1.0) for d in days])


def is_promo(d):
    return (d.month == 11 and d.day >= 24) or (d.month == 12 and d.day <= 2) or (d.month == 7 and 10 <= d.day <= 14)


# --------------------------------------------------------------------------- customers
def ascii_slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.lower().replace(" ", ".") if ch.isalnum() or ch == ".").strip(".")


countries = list(COUNTRY_W)
cw = np.array([COUNTRY_W[c] for c in countries]); cw /= cw.sum()
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "example.com"]
DOMAIN_W = [.45, .2, .2, .1, .05]

customers = []
for i in range(1, N_CUSTOMERS + 1):
    country = rng.choice(countries, p=cw)
    city, lat, lon = CITIES[country][rng.integers(len(CITIES[country]))]
    f = fakers[country]
    name = f.romanized_name() if country == "Japan" else f"{f.first_name()} {f.last_name()}"
    # signup skewed towards the early part of the window
    signup = START + timedelta(int(rng.beta(1.5, 1.2) * (date(2025, 11, 30) - START).days))
    lifetime = max(25, int(rng.exponential(620)))                       # days the customer stays active
    active_until = min(signup + timedelta(lifetime), END)
    rate = 0.8 + rng.gamma(2.0, 2.6)                                    # orders per year while active
    fav = list(rng.choice(CATEGORIES, size=2, replace=False))
    customers.append(dict(
        customer_id=f"C{i:05d}", customer_name=name,
        customer_email=f"{ascii_slug(name)}{i:04d}@{rng.choice(DOMAINS, p=DOMAIN_W)}",
        country=country, city=city, latitude=lat, longitude=lon,
        signup=signup, active_until=active_until, rate=rate, fav=fav))

# --------------------------------------------------------------------------- orders
PAY = ["Credit Card", "PayPal", "Debit Card", "Apple Pay", "Gift Card", "Bank Transfer"]
PAY_W = [.48, .22, .15, .08, .04, .03]
SHIP = ["Standard", "Express", "Next Day", "Store Pickup"]
SHIP_W = [.62, .25, .08, .05]

orders = []   # (date, customer dict)
for c in customers:
    span = (c["active_until"] - c["signup"]).days
    n_extra = rng.poisson(c["rate"] * span / 365.0)
    orders.append((c["signup"], c))                                     # first order on signup day
    if n_extra and span > 0:
        i0 = (c["signup"] - START).days
        i1 = (c["active_until"] - START).days
        w = day_w[i0:i1 + 1]
        idx = rng.choice(np.arange(i0, i1 + 1), size=n_extra, p=w / w.sum())
        orders.extend((days[j], c) for j in idx)
orders.sort(key=lambda t: (t[0], t[1]["customer_id"]))

rows = []
LAST_SHIPPED_CUTOFF = END - timedelta(days=4)
for n, (d, c) in enumerate(orders, start=1):
    oid = f"ORD-{100000 + n}"
    # primary product: favourite category 65% of the time
    cat = c["fav"][rng.integers(2)] if rng.random() < 0.65 else CATEGORIES[rng.integers(len(CATEGORIES))]
    pool = BY_CAT[cat]
    w = np.array([base_w[PID[p]] for p in pool]); w /= w.sum()
    chosen = [rng.choice(pool, p=w)]
    for b in BUNDLE_OF.get(chosen[0], []):                              # cross-sell partners
        for partner in b:
            if partner not in chosen and rng.random() < 0.38 and len(chosen) < 5:
                chosen.append(partner)
    if rng.random() < 0.20:                                             # random impulse item
        extra = PRODUCTS[rng.integers(len(PRODUCTS))][0]
        if extra not in chosen:
            chosen.append(extra)

    pay = rng.choice(PAY, p=PAY_W)
    ship = rng.choice(SHIP, p=SHIP_W)
    if d > LAST_SHIPPED_CUTOFF:
        status = "Shipped"
    else:
        status = rng.choice(["Delivered", "Cancelled", "Returned"], p=[.90, .05, .05])
    for pid in chosen:
        _, pname, pcat, price = PRODUCTS[PID[pid]]
        qty = int(rng.choice([1, 2, 3, 4, 5], p=[.70, .20, .06, .03, .01]) if price < 60 else rng.choice([1, 2], p=[.9, .1]))
        disc = int(rng.choice([20, 25, 30], p=[.5, .3, .2]) if (is_promo(d) and rng.random() < .8)
                   else rng.choice([0, 5, 10, 15], p=[.62, .15, .15, .08]))
        rows.append(dict(
            order_id=oid, order_date=d.isoformat(), customer_id=c["customer_id"],
            customer_name=c["customer_name"], customer_email=c["customer_email"],
            country=c["country"], city=c["city"], latitude=c["latitude"], longitude=c["longitude"],
            product_id=pid, product_name=pname, category=pcat, quantity=qty, unit_price=f"{price:.2f}",
            discount_pct=disc, total_amount=f"{round(qty * price * (1 - disc / 100), 2):.2f}",
            payment_method=pay, order_status=status, shipping_method=ship))

df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)

# --------------------------------------------------------------------------- summary
print(f"wrote {OUT}")
print(f"rows (order lines): {len(df):,}   orders: {df.order_id.nunique():,}   customers: {df.customer_id.nunique():,}")
print(f"date range: {df.order_date.min()} -> {df.order_date.max()}")
print(df.order_status.value_counts().to_dict())
net = df[df.order_status.isin(["Delivered", "Shipped"])]
print(f"net revenue (Delivered+Shipped): {net.total_amount.astype(float).sum():,.2f}")
assert not df.duplicated(["order_id", "product_id"]).any(), "order lines must be unique"
