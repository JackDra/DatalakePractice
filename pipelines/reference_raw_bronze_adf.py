"""Reference-only example for deploying the raw -> bronze ADF pipeline.

This file is not wired into the `operations` CLI. Use it as a map while
building your own implementation in `operations/build_bronze.py`.
"""

import os
import subprocess

import click
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import (
    AzureBlobFSLinkedService,
    AzureBlobFSLocation,
    AzureBlobFSReadSettings,
    AzureBlobFSWriteSettings,
    BinaryDataset,
    BinarySink,
    BinarySource,
    CopyActivity,
    DatasetReference,
    DatasetResource,
    LinkedServiceReference,
    LinkedServiceResource,
    PipelineResource,
    SecureString,
)


DEFAULT_RESOURCE_GROUP = "rg-datalake-practice"
DEFAULT_FACTORY_NAME = "adf-datalake-practice-jd01"
DEFAULT_STORAGE_ACCOUNT_NAME = "jddatalakepractice01"

LINKED_SERVICE_NAME = "ls_adls_practice"
RAW_DATASET_NAME = "ds_raw_binary"
BRONZE_DATASET_NAME = "ds_bronze_binary"
PIPELINE_NAME = "pl_copy_raw_to_bronze"
COPY_ACTIVITY_NAME = "copy_raw_to_bronze"


def get_subscription_id() -> str:
    if subscription_id := os.environ.get("AZURE_SUBSCRIPTION_ID"):
        return subscription_id

    result = subprocess.run(
        ["az", "account", "show", "--query", "id", "-o", "tsv"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_storage_account_key() -> str:
    if account_key := os.environ.get("AZURE_STORAGE_ACCOUNT_KEY"):
        return account_key

    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
    for part in conn_str.split(";"):
        if part.startswith("AccountKey="):
            return part.removeprefix("AccountKey=")

    raise RuntimeError(
        "Set AZURE_STORAGE_ACCOUNT_KEY or AZURE_STORAGE_CONNECTION_STRING."
    )


def upsert_linked_service(
    client: DataFactoryManagementClient,
    resource_group: str,
    factory_name: str,
    storage_account_name: str,
) -> None:
    url = f"https://{storage_account_name}.dfs.core.windows.net"
    linked_service = LinkedServiceResource(
        properties=AzureBlobFSLinkedService(
            url=url,
            account_key=SecureString(value=get_storage_account_key()),
        )
    )

    client.linked_services.create_or_update(
        resource_group,
        factory_name,
        LINKED_SERVICE_NAME,
        linked_service,
    )


def binary_dataset(file_system: str) -> DatasetResource:
    return DatasetResource(
        properties=BinaryDataset(
            linked_service_name=LinkedServiceReference(
                type="LinkedServiceReference",
                reference_name=LINKED_SERVICE_NAME,
            ),
            location=AzureBlobFSLocation(file_system=file_system),
        )
    )


def upsert_datasets(
    client: DataFactoryManagementClient,
    resource_group: str,
    factory_name: str,
) -> None:
    datasets = {
        RAW_DATASET_NAME: binary_dataset("raw"),
        BRONZE_DATASET_NAME: binary_dataset("bronze"),
    }

    for name, dataset in datasets.items():
        client.datasets.create_or_update(resource_group, factory_name, name, dataset)


def upsert_pipeline(
    client: DataFactoryManagementClient,
    resource_group: str,
    factory_name: str,
) -> None:
    copy_activity = CopyActivity(
        name=COPY_ACTIVITY_NAME,
        inputs=[
            DatasetReference(
                type="DatasetReference",
                reference_name=RAW_DATASET_NAME,
            )
        ],
        outputs=[
            DatasetReference(
                type="DatasetReference",
                reference_name=BRONZE_DATASET_NAME,
            )
        ],
        source=BinarySource(
            store_settings=AzureBlobFSReadSettings(
                recursive=True,
                delete_files_after_completion=False,
            )
        ),
        sink=BinarySink(
            store_settings=AzureBlobFSWriteSettings(
                copy_behavior="PreserveHierarchy",
            )
        ),
    )

    pipeline = PipelineResource(activities=[copy_activity])

    client.pipelines.create_or_update(
        resource_group,
        factory_name,
        PIPELINE_NAME,
        pipeline,
    )


@click.command()
@click.option(
    "--subscription-id",
    default=lambda: os.environ.get("AZURE_SUBSCRIPTION_ID"),
    help="Azure subscription ID. Defaults to AZURE_SUBSCRIPTION_ID.",
)
@click.option("--resource-group", default=DEFAULT_RESOURCE_GROUP, show_default=True)
@click.option("--factory-name", default=DEFAULT_FACTORY_NAME, show_default=True)
@click.option(
    "--storage-account-name",
    default=DEFAULT_STORAGE_ACCOUNT_NAME,
    show_default=True,
)
def main(
    subscription_id: str | None,
    resource_group: str,
    factory_name: str,
    storage_account_name: str,
) -> None:
    subscription_id = subscription_id or get_subscription_id()
    credential = DefaultAzureCredential()
    client = DataFactoryManagementClient(credential, subscription_id)

    upsert_linked_service(
        client,
        resource_group,
        factory_name,
        storage_account_name,
    )
    upsert_datasets(client, resource_group, factory_name)
    upsert_pipeline(client, resource_group, factory_name)


if __name__ == "__main__":
    main()
