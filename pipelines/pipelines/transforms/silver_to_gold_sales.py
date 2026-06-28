import logging

from pipelines.database.spark_service import GOLD_APP_NAME, SparkService

logger = logging.getLogger(__name__)


def create_silver_to_gold() -> None:
    logger.info("Connecting to spark")
    spark_svc = SparkService.from_appname(app_name=GOLD_APP_NAME)

    logger.info("Building daily sales summary")
    spark_svc.custom_silver_to_gold()


if __name__ == "__main__":
    create_silver_to_gold()
