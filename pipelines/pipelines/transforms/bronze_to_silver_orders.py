import logging

from pipelines.database.spark_service import SparkService

logger = logging.getLogger(__name__)


def create_bronze_to_silver():
    logger.info("Connecting to spark")
    spark_svc = SparkService.from_appname()

    logger.info("Defining custom bronze_to_silver")
    spark_svc.custom_bronze_to_silver()


if __name__ == "__main__":
    create_bronze_to_silver()
