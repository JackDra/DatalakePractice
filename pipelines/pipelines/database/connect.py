import os
from dataclasses import dataclass
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient


@dataclass
class AzureConfig:
    subscription_id: str
    resource_group: str
    factory_name: str
    storage_account_name: str

    @classmethod
    def from_env(cls):
        return cls(
            subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
            resource_group=os.environ["AZURE_RESOURCE_GROUP"],
            factory_name=os.environ["AZURE_DATA_FACTORY_NAME"],
            storage_account_name=os.environ["AZURE_STORAGE_ACCOUNT_NAME"],
        )


def get_df_client(
    azure_cfg: Optional[AzureConfig] = None,
) -> tuple[DataFactoryManagementClient, AzureConfig]:
    if azure_cfg is None:
        azure_cfg = AzureConfig.from_env()
    credential = DefaultAzureCredential()
    return DataFactoryManagementClient(credential, azure_cfg.subscription_id), azure_cfg
