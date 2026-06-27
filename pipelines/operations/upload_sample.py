import os
import pathlib
from typing import Iterator
from azure.storage.filedatalake import DataLakeServiceClient


def get_dl_service(conn_str: str | None = None) -> DataLakeServiceClient:
    """Connect and create datalake service client

    Args:
        conn_str (str): Connection string used to connect to datalake

    Returns:
        DataLakeServiceClient: Datalake service connected.
    """
    conn_str = conn_str or os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    dl_service = DataLakeServiceClient.from_connection_string(conn_str)
    return dl_service

def get_all_paths(base_path: pathlib.Path) -> Iterator[tuple[str, str, pathlib.Path]]:
    for local_path in base_path.rglob("*"):
        if local_path.is_file():
            relative_path = local_path.relative_to(base_path)
            directory = relative_path.parent.as_posix()
            yield directory, local_path.name, local_path
    

def main():
    dl_service = get_dl_service()
    raw_data_path = pathlib.Path(__file__).parent.parent.parent / "data" / "raw" 
    raw_client = dl_service.get_file_system_client("raw")

    for ifolder, ifile, ipath in get_all_paths(raw_data_path):
        
        directory_client = raw_client.get_directory_client(ifolder)
        directory_client.create_directory()
        file_client = directory_client.get_file_client(ifile)

        with open(ipath, "rb") as f:
            file_client.upload_data(f, overwrite=True)
        print(f"Uploaded {ipath} -> raw/{ifolder}") 


if __name__ == "__main__":
    main()
