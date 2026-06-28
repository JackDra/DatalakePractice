from dataclasses import dataclass

from azure.mgmt.datafactory.models import (
    AzureBlobFSReadSettings,
    AzureBlobFSWriteSettings,
    BinarySink,
    BinarySource,
    CopyActivity,
    DatasetReference,
)


@dataclass
class CopyConfig:
    name: str
    input_ref_name: str
    output_ref_name: str

    def get_copy_activity(self) -> CopyActivity:
        return CopyActivity(
            name=self.name,
            inputs=[
                DatasetReference(
                    type="DatasetReference",
                    reference_name=self.input_ref_name,
                )
            ],
            outputs=[
                DatasetReference(
                    type="DatasetReference",
                    reference_name=self.output_ref_name,
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
