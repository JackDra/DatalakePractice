import logging
import time
from datetime import datetime, timedelta, timezone

from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import RunFilterParameters

logger = logging.getLogger(__name__)


def wait_for_pipeline_run(
    df_client: DataFactoryManagementClient,
    resource_group: str,
    factory_name: str,
    run_id: str,
    poll_interval_seconds: int = 10,
) -> str:
    terminal_statuses = {"Succeeded", "Failed", "Cancelled"}

    while True:
        pipeline_run = df_client.pipeline_runs.get(
            resource_group,
            factory_name,
            run_id,
        )
        logger.info("Pipeline status: %s", pipeline_run.status)

        if pipeline_run.status in terminal_statuses:
            if pipeline_run.status != "Succeeded":
                log_activity_errors(
                    df_client,
                    resource_group,
                    factory_name,
                    run_id,
                )
            return pipeline_run.status

        time.sleep(poll_interval_seconds)


def log_activity_errors(
    df_client: DataFactoryManagementClient,
    resource_group: str,
    factory_name: str,
    run_id: str,
) -> None:
    now = datetime.now(timezone.utc)
    activity_runs = df_client.activity_runs.query_by_pipeline_run(
        resource_group,
        factory_name,
        run_id,
        RunFilterParameters(
            last_updated_after=now - timedelta(hours=2),
            last_updated_before=now + timedelta(minutes=5),
        ),
    )

    for activity in activity_runs.value:
        if activity.status != "Succeeded":
            logger.error(
                "Activity failed: name=%s status=%s error=%s",
                activity.activity_name,
                activity.status,
                activity.error,
            )
