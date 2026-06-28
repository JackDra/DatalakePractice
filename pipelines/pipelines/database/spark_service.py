from dataclasses import dataclass

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DEFAULT_STORAGE_ACCOUNT_NAME = "jddatalakepractice01"
DEFAULT_APP_NAME = "bronze-to-silver-orders"
GOLD_APP_NAME = "silver-to-gold-sales"


@dataclass
class SparkService:
    session: SparkSession
    storage_account: str = DEFAULT_STORAGE_ACCOUNT_NAME

    @classmethod
    def from_appname(
        cls,
        app_name: str = DEFAULT_APP_NAME,
        storage_account: str = DEFAULT_STORAGE_ACCOUNT_NAME,
    ):
        return cls(
            session=SparkSession.builder.appName(app_name).getOrCreate(),
            storage_account=storage_account,
        )

    @property
    def bronze_base(self) -> str:
        return f"abfss://bronze@{self.storage_account}.dfs.core.windows.net/bronze_code"

    @property
    def silver_base(self) -> str:
        return f"abfss://silver@{self.storage_account}.dfs.core.windows.net"

    @property
    def gold_base(self) -> str:
        return f"abfss://gold@{self.storage_account}.dfs.core.windows.net"

    def custom_bronze_to_silver(self) -> None:
        orders = self.session.read.option("header", True).csv(
            f"{self.bronze_base}/orders"
        )
        customers = self.session.read.option("header", True).csv(
            f"{self.bronze_base}/customers"
        )
        products = self.session.read.option("header", True).csv(
            f"{self.bronze_base}/products"
        )

        typed_orders = (
            orders.withColumn("order_timestamp", F.to_timestamp("order_timestamp"))
            .withColumn("quantity", F.col("quantity").cast("int"))
            .withColumn("unit_price", F.col("unit_price").cast("decimal(10,2)"))
        )

        orders_enriched = (
            typed_orders.alias("o")
            .join(customers.alias("c"), on="customer_id", how="left")
            .join(products.alias("p"), on="product_id", how="left")
            .select(
                F.col("o.order_id"),
                F.col("o.order_timestamp"),
                F.col("o.customer_id"),
                F.col("o.product_id"),
                F.col("o.quantity"),
                F.col("o.unit_price").alias("order_unit_price"),
                (F.col("o.quantity") * F.col("o.unit_price")).alias("line_total"),
                F.col("o.currency").alias("order_currency"),
                F.col("o.payment_method"),
                F.col("o.channel"),
                F.col("c.first_name"),
                F.col("c.last_name"),
                F.col("c.email"),
                F.col("c.country"),
                F.col("c.state"),
                F.col("c.loyalty_tier"),
                F.col("p.sku"),
                F.col("p.product_name"),
                F.col("p.category"),
                F.col("p.unit_price").cast("decimal(10,2)").alias("product_unit_price"),
                F.col("p.currency").alias("product_currency"),
                F.col("p.active").cast("boolean").alias("product_active"),
            )
        )

        orders_enriched.write.mode("overwrite").parquet(
            f"{self.silver_base}/orders_enriched"
        )

    def custom_silver_to_gold(self) -> None:
        orders_enriched = self.session.read.parquet(
            f"{self.silver_base}/orders_enriched"
        )

        daily_sales_summary = (
            orders_enriched.withColumn("order_date", F.to_date("order_timestamp"))
            .groupBy("order_date", "channel", "category", "order_currency")
            .agg(
                F.countDistinct("order_id").alias("order_count"),
                F.sum("quantity").alias("units_sold"),
                F.sum("line_total").alias("gross_sales"),
                F.avg("line_total").alias("avg_line_total"),
            )
            .withColumn("processed_at", F.current_timestamp())
            .orderBy("order_date", "channel", "category")
        )

        daily_sales_summary.write.mode("overwrite").parquet(
            f"{self.gold_base}/daily_sales_summary"
        )

        daily_sales_summary.coalesce(1).write.mode("overwrite").json(
            f"{self.gold_base}/dashboard/daily_sales_summary_json"
        )
