import azure.functions as func
import logging
import json
import io
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobBlock, BlobClient, StandardBlobTier
from agents import main as agents_main

app = func.FunctionApp()
account_url = "https://yogendrastorage.blob.core.windows.net"
credential = DefaultAzureCredential()

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url, credential=credential)


@app.service_bus_queue_trigger(arg_name="azservicebus", queue_name="firstqueue",
                               connection="servicebusqueueacc_SERVICEBUS") 
def servicebus_queue_trigger(azservicebus: func.ServiceBusMessage):
    logging.info('Python ServiceBus Queue trigger processed a message:')
    message_body = azservicebus.get_body().decode('utf-8')
    
    logging.info(f"Received message: {message_body}")

    output_json = agents_main(message_body)
    logging.info(output_json)

    typeq = output_json.get("type", "").strip().lower()
    categoryq = output_json.get("category", "").strip()

    if typeq == "query":
        b_container = "query-container"
    elif typeq == "complaint":
        b_container = "complaint-container"

    try:
        blob_client = blob_service_client.get_blob_client(
            container=b_container,
            blob=f"{categoryq}/{uuid.uuid4()}.bin"
        )

        blob_client.upload_blob(
            message_body.encode('utf-8'),
            blob_type="BlockBlob",
            overwrite=True
        )

        logging.info(f"Blob uploaded successfully to container '{b_container}' with name '{blob_client.blob_name}'.")
    except Exception as e:  
        logging.error(f"Error occurred while uploading blob: {e}")
        
    