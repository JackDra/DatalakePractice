import csv
import io
import logging
import random
from dataclasses import dataclass
from datetime import UTC, datetime

from pipelines.operations.upload_sample import get_dl_service

logger = logging.getLogger(__name__)

CUSTOMER_IDS = ["CUST-0001", "CUST-0002", "CUST-0003", "CUST-0004", "CUST-0005"]
PRODUCTS = [
    ("PROD-1001", "139.00"),
    ("PROD-1002", "49.00"),
    ("PROD-1003", "89.00"),
    ("PROD-1004", "7.50"),
    ("PROD-1008", "79.00"),
]
PAYMENT_METHODS = ["card", "paypal"]
CHANNELS = ["web", "mobile", "store"]


@dataclass(frozen=True)
class FakeOrderBatch:
    directory: str
    filename: str
    data: bytes


def build_fake_order_batch(row_count: int) -> FakeOrderBatch:
    now = datetime.now(UTC)
    batch_id = now.strftime("%Y%m%d%H%M%S")
    directory = f"orders/year={now:%Y}/month={now:%m}/day={now:%d}"
    filename = f"orders_extra_{batch_id}.csv"

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "order_id",
            "order_timestamp",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "currency",
            "payment_method",
            "channel",
        ]
    )

    for index in range(1, row_count + 1):
        product_id, unit_price = random.choice(PRODUCTS)
        writer.writerow(
            [
                f"ORD-{batch_id}-{index:04d}",
                now.isoformat().replace("+00:00", "Z"),
                random.choice(CUSTOMER_IDS),
                product_id,
                random.randint(1, 4),
                unit_price,
                "AUD",
                random.choice(PAYMENT_METHODS),
                random.choice(CHANNELS),
            ]
        )

    return FakeOrderBatch(
        directory=directory,
        filename=filename,
        data=buffer.getvalue().encode("utf-8"),
    )


def ingest_fake_orders(row_count: int = 5) -> None:
    batch = build_fake_order_batch(row_count=row_count)
    dl_service = get_dl_service()
    raw_client = dl_service.get_file_system_client("raw")
    directory_client = raw_client.get_directory_client(batch.directory)
    directory_client.create_directory()

    file_client = directory_client.get_file_client(batch.filename)
    file_client.upload_data(batch.data, overwrite=True)

    logger.info("Uploaded fake order batch to raw/%s/%s", batch.directory, batch.filename)
