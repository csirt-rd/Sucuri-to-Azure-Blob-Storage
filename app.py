#!/usr/bin/env python3
from datetime import datetime, timedelta
from os import getcwd, path
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceExistsError
import threading

# Azure Data 
AZURE_ACC_KEY = ""
AZURE_ENDPOINT_SUFFIX = "core.windows.net"
AZURE_ACC_NAME = ""
AZURE_ENDPOINT = "{}.table.{}".format(AZURE_ACC_NAME, AZURE_ENDPOINT_SUFFIX)
AZURE_CONN_STR = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
    AZURE_ACC_NAME, AZURE_ACC_KEY, AZURE_ENDPOINT_SUFFIX
)

# Sucuri Info
AZURE_TABLE_NAME = ""
SUCURI_API_URL = "https://waf.sucuri.net/api?v2"
SUCURI_SITES = []

def daterange(start_date, end_date):    #date range generator
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def disk_to_blob():
    for i in SUCURI_SITES: #iterate through sites dictionaries list
        if i["enabled"]:    #if site marked as enabled
            for single_date in daterange(datetime.strptime(i["added_time"], "%Y-%m-%d"), datetime.now()):
                try:
                    MY_PATH = '/'.join([
                        "/mnt/cleonardo",
                        'sucuri',
                        i["domain"]
                    ])
                    SUCURI_FILE = '-'.join([
                        i["domain"],
                        single_date.strftime("%Y-%m-%d"),
                        '1000'
                    ]) + '.csv'
                    FILE = '/'.join([MY_PATH,SUCURI_FILE])
                    if path.isfile(FILE):
                        with BlobClient.from_connection_string(conn_str=AZURE_CONN_STR, container_name="sucuri", blob_name=SUCURI_FILE) as blob:
                            with open(FILE, 'rb') as data:
                                try:
                                    blob.upload_blob(data)
                                except ResourceExistsError:
                                    pass
                except:
                    continue

if __name__ == "__main__":
    threads = list()
    for index in range(100):
        x = threading.Thread(target=disk_to_blob, daemon=True)
        threads.append(x)
        x.start()
    for index, thread in enumerate(threads):
        thread.join()
