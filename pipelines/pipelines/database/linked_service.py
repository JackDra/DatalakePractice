import os
from dataclasses import dataclass
from typing import Optional

from azure.mgmt.datafactory.models import (
    AzureBlobFSLinkedService,
    LinkedServiceResource,
    SecureString,
)


@dataclass
class LinkedConfig:
    storage_account_name: str
    storage_account_key: str

    @classmethod
    def from_env(cls):
        return cls(
            storage_account_name=os.environ["AZURE_STORAGE_ACCOUNT_NAME"],
            storage_account_key=os.environ["AZURE_STORAGE_ACCOUNT_KEY"],
        )


def get_linked_svc(
    linked_cfg: Optional[LinkedConfig] = None,
) -> tuple[LinkedServiceResource, LinkedConfig]:
    if linked_cfg is None:
        linked_cfg = LinkedConfig.from_env()
    return LinkedServiceResource(
        properties=AzureBlobFSLinkedService(
            url=f"https://{linked_cfg.storage_account_name}.dfs.core.windows.net",
            account_key=SecureString(value=linked_cfg.storage_account_key),
        )
    ), linked_cfg
