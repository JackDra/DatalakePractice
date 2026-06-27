# Sample Data Lake Dataset

This folder contains small sample files for practicing data lake ingestion and transformation patterns.

Suggested lake layout:

```text
raw/
bronze/
silver/
gold/
```

The files here are intentionally kept small so they are cheap to upload to Azure Data Lake Storage Gen2.

## Files

- `raw/customers/customers.csv` - customer master data.
- `raw/products/products.csv` - product master data.
- `raw/orders/year=2026/month=06/day=01/orders.csv` - order transactions for one day.
- `raw/orders/year=2026/month=06/day=02/orders.csv` - order transactions for another day, including a few messy records for validation practice.
- `raw/web_events/year=2026/month=06/day=01/events.jsonl` - clickstream-style JSON Lines events.

## Practice Ideas

1. Upload everything under `data/raw` into a cloud data lake `raw` container or folder.
2. Convert CSV and JSONL files into Parquet in a `bronze` zone.
3. Validate orders:
   - reject missing customer IDs
   - reject negative quantities
   - flag unknown product IDs
   - standardize timestamp formats
4. Join orders with customers and products into a `silver/orders_enriched` dataset.
5. Aggregate daily revenue by product category into a `gold/daily_category_revenue` dataset.
6. Aggregate customer lifetime value into a `gold/customer_value` dataset.

