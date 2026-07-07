import io
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobBlock, BlobClient, StandardBlobTier

#: Replace <storage-account-name> with your actual storage account name
account_url = "https://yogendrastorage.blob.core.windows.net"
credential = DefaultAzureCredential()

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url, credential=credential)

def upload_blob_data(blob_service_client: BlobServiceClient, container_name: str):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob="sample-blob.txt")
        data = b"Sample data for blob"

        # Upload the blob data - default blob type is BlockBlob
        blob_client.upload_blob(data, blob_type="BlockBlob")
        print(f"Blob uploaded successfully to container '{container_name}' with name 'sample-blob.txt'.")
    except Exception as e:
        print(f"Error occurred while uploading blob: {e}")

upload_blob_data(blob_service_client, "incoming")