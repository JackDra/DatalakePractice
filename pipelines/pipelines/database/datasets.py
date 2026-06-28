from dataclasses import dataclass
from typing import Optional

from azure.mgmt.datafactory.models import (
    AzureBlobFSLocation,
    BinaryDataset,
    DatasetResource,
    LinkedServiceReference,
)


@dataclass
class DatasetConfig:
    reference_name: str
    file_system: str
    folder_path: Optional[str] = None
    type: str = "LinkedServiceReference"

    def get_binary_dset(self) -> BinaryDataset:
        return DatasetResource(
            properties=BinaryDataset(
                linked_service_name=LinkedServiceReference(
                    type="LinkedServiceReference",
                    reference_name=self.reference_name,
                ),
                location=AzureBlobFSLocation(
                    file_system=self.file_system,
                    folder_path=self.folder_path,
                ),
            )
        )
