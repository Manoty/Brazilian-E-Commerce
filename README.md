# Olist Logistics Analytics — dbt Project

A production-style analytics pipeline built on the Brazilian Olist e-commerce dataset using dbt + DuckDB.

## Business Questions Answered
- Which Brazilian states have the highest late delivery rates?
- Who are the top performing sellers by revenue and delivery reliability?
- What is the revenue trend month over month?
- Which customers represent the highest lifetime value?

## Project Structure
```
olist_logistics_analytics/
├── models/
│   ├── staging/          # Raw source cleaning and renaming (9 models)
│   ├── intermediate/     # Pre-aggregations before marts (1 model)
│   └── marts/            # Business-facing dims, facts and analytics (9 models)
├── seeds/                # Lookup/reference tables
├── data/                 # Raw Olist CSVs (DuckDB external sources)
└── dbt_project.yml
```

## Data Sources
All 9 Olist datasets from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce):

| Table | Description |
|---|---|
| orders | All customer orders |
| order_items | Individual items per order |
| customers | Customer details and location |
| products | Product catalog |
| payments | Payment transactions |
| sellers | Seller details and location |
| reviews | Customer reviews |
| geolocation | Brazilian zip code lat/lng |
| product_category_name_translation | Portuguese → English categories |

## Lineage
```
[Raw CSVs]
    ↓
[Staging Layer]        stg_orders, stg_customers, stg_products ...
    ↓
[Intermediate Layer]   int_orders_enriched
    ↓
[Marts Layer]          dim_customers, dim_products, dim_sellers
                       fct_orders, fct_order_items
                       mart_revenue_analysis, mart_delivery_performance
                       mart_customer_ltv, mart_seller_performance
```

## Key Metrics

### Delivery Performance
- Late delivery rate by customer state and seller state
- Average actual vs estimated delivery days

### Revenue Analysis
- Monthly revenue trends
- Average order value over time
- Revenue per unique customer

### Customer LTV
- Total spend segmented into high / mid / low value tiers
- Customer lifespan in days
- Average review score per customer

### Seller Performance
- Revenue tiering: top / mid / low seller
- Late delivery rate per seller
- Unique product categories sold

## Stack
- **Transform:** dbt Core
- **Warehouse:** DuckDB
- **Language:** SQL
- **Data:** Olist Brazilian E-commerce (Kaggle)

## Running the Project
```bash
# Install dependencies
pip install dbt-duckdb

# Install dbt packages
dbt deps

# Run all models
dbt run

# Run tests
dbt test

# Generate and serve docs
dbt docs generate && dbt docs serve
```

## Design Decisions
- **Geolocation centroids:** Multiple lat/lng readings per zip code are averaged to produce a centroid — more statistically stable than taking a single arbitrary record
- **Intermediate layer:** Payment and review aggregations are pre-computed in `int_orders_enriched` before hitting the facts layer, keeping mart models clean and maintainable
- **External sources:** Raw CSVs loaded directly via DuckDB `read_csv_auto()` — no separate ingestion script needed
- **LTV segmentation:** Thresholds set at 1000 BRL (high) and 300 BRL (mid) based on dataset revenue distribution