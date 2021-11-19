#!/usr/bin/env python3
from datetime import datetime, timedelta
from os import getcwd, makedirs
from azure.storage.blob import BlobClient

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

LOG_FILE = '-'.join([
    '/'.join([getcwd(), 'logs', 'log']),
    datetime.now().strftime("%Y%m%d")
]) + '.txt'
yesterday = datetime.now() - timedelta(1)

def disk_to_blob():
    try:   
        makedirs('/'.join([getcwd(), 'logs']))
    except FileExistsError:
        pass
    for i in SUCURI_SITES:
        if i["enabled"]:   
            try:   
                MY_PATH = '/'.join([
                    getcwd(),
                    'sucuri',
                    i["domain"]
                ])
                SUCURI_FILE = '-'.join([
                    i["domain"],
                    yesterday.strftime("%Y-%m-%d"),
                    '1000'
                ]) + '.csv'  
                BLOB = '/'.join([i["domain"], SUCURI_FILE])
                with open(LOG_FILE, 'a', encoding='utf-8') as l:
                    l.write(
                        ' '.join([
                            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
                            '+00:00',
                            '[INF]',
                            'Getting csv file from',
                            i["domain"],
                            'at',
                            datetime.now().strftime("%Y-%m-%d"),
                            '\n'
                        ])
                    )
                    l.close()  
                with BlobClient.from_connection_string(conn_str=AZURE_CONN_STR, container_name="sucuri", blob_name=BLOB) as blob:
                    FILE = '/'.join([MY_PATH,SUCURI_FILE])
                    with open(FILE, 'rb') as data:
                        blob.upload_blob(data)
                with open(LOG_FILE, 'a', encoding='utf-8') as l:
                    l.write(
                        ' '.join([
                            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
                            '+00:00',
                            '[INF]',
                            'Sending to',
                            'Sucuri Blob Storage'
                            '\n'
                        ])
                    )
                    l.close()  
            except:
                continue

if __name__ == "__main__":
    disk_to_blob()
