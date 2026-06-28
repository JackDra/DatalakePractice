import logging

from azure.mgmt.datafactory.models import (
    PipelineResource,
)

from pipelines.database.connect import get_df_client
from pipelines.database.data_factory import get_datafactory
from pipelines.database.datasets import DatasetConfig
from pipelines.database.linked_service import get_linked_svc
from pipelines.database.pipeline import CopyConfig
from pipelines.utils import wait_for_pipeline_run

logger = logging.getLogger(__name__)


def build_bronze(
    ls_name: str = "ls_adls_practice",
    pipeline_name: str = "pl_copy_raw_to_bronze_code",
    run_pipeline: bool = False,
):
    logger.info("Connecting to services")
    df_client, client_cfg = get_df_client()
    df_factory, factory_cfg = get_datafactory(df_client)
    linked_svc, linked_cfg = get_linked_svc()

    logger.info("Creating linked service")
    df_client.linked_services.create_or_update(
        client_cfg.resource_group,
        client_cfg.factory_name,
        ls_name,
        linked_svc,
    )

    logger.info("Constructing pipeline definitions")
    bronze_code_bdset = DatasetConfig(
        reference_name=ls_name,
        file_system="bronze",
        folder_path="bronze_code",
    ).get_binary_dset()

    raw_bdset = DatasetConfig(
        reference_name=ls_name,
        file_system="raw",
    ).get_binary_dset()

    df_client.datasets.create_or_update(
        client_cfg.resource_group,
        client_cfg.factory_name,
        "ds_raw_binary_code",
        raw_bdset,
    )

    df_client.datasets.create_or_update(
        client_cfg.resource_group,
        client_cfg.factory_name,
        "ds_bronze_code_binary",
        bronze_code_bdset,
    )

    copy_activity = CopyConfig(
        name="copy_raw_to_bronze_code",
        input_ref_name="ds_raw_binary_code",
        output_ref_name="ds_bronze_code_binary",
    ).get_copy_activity()

    pipeline = PipelineResource(activities=[copy_activity])

    logger.info("Creating pipeline")
    df_client.pipelines.create_or_update(
        client_cfg.resource_group,
        client_cfg.factory_name,
        pipeline_name,
        pipeline,
    )
    logger.info(f"pipeline {pipeline_name} created!")

    if run_pipeline:
        run_response = df_client.pipelines.create_run(
            client_cfg.resource_group,
            client_cfg.factory_name,
            pipeline_name,
        )

        logger.info(f"Started pipeline run: {run_response.run_id}")
        status = wait_for_pipeline_run(
            df_client,
            client_cfg.resource_group,
            client_cfg.factory_name,
            run_response.run_id,
        )
        logger.info("Pipeline run finished with status: %s", status)
