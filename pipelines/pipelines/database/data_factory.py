import os
from dataclasses import dataclass
from typing import Optional

from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import Factory


@dataclass
class FactoryConfig:
    resource_group: str
    factory_name: str

    @classmethod
    def from_env(cls):
        resource_group = os.environ["AZURE_RESOURCE_GROUP"]
        factory_name = os.environ["AZURE_DATA_FACTORY_NAME"]
        return cls(resource_group=resource_group, factory_name=factory_name)


def get_datafactory(
    df_client: DataFactoryManagementClient,
    factory_config: Optional[FactoryConfig] = None,
) -> tuple[Factory, FactoryConfig]:
    if factory_config is None:
        factory_config = FactoryConfig.from_env()
    factory = df_client.factories.get(
        factory_config.resource_group, factory_config.factory_name
    )
    return factory, factory_config
