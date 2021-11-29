#!/usr/bin/env python3
from datetime import datetime, timedelta
from os import path, getcwd
import threading
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceExistsError

# Azure Data 
AZURE_ACC_KEY = ""
AZURE_ENDPOINT_SUFFIX = "core.windows.net"
AZURE_ACC_NAME = ""
AZURE_ENDPOINT = "{}.table.{}".format(AZURE_ACC_NAME, AZURE_ENDPOINT_SUFFIX)
AZURE_CONN_STR = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
    AZURE_ACC_NAME, AZURE_ACC_KEY, AZURE_ENDPOINT_SUFFIX
)

# Sucuri Info
SUCURI_API_URL = "https://waf.sucuri.net/api?v2"
SUCURI_SITES = []

#Disk to Azure Storage Blob
def disk_to_blob(domain, date, enabled):
    if enabled:
        PATH = '/'.join([
            getcwd(),
            'sucuri',
            domain
        ])
        SUCURI_FILE = '-'.join([
            domain,
            date.strftime("%Y-%m-%d"),
            '1000'
        ]) + '.csv'
        FILE = '/'.join([PATH,SUCURI_FILE])
        if path.isfile(FILE):
            with BlobClient.from_connection_string(conn_str=AZURE_CONN_STR, container_name="", blob_name=SUCURI_FILE) as blob:
                with open(FILE, 'rb') as data:
                    try:
                        blob.upload_blob(data)
                    except ResourceExistsError:
                        pass

if __name__ == "__main__":
    yesterday = datetime.now() - timedelta(1)
    threads = list()
    for i in SUCURI_SITES:
        x = threading.Thread(target=disk_to_blob, args=(i["domain"],yesterday,i["enabled"]), daemon=True)
        threads.append(x)
        x.start()
    for index, thread in enumerate(threads):
        thread.join()
