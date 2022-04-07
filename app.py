#!/usr/bin/env python3
import threading, requests
import pandas as pd
from datetime import datetime, timedelta
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceExistsError
import azure.functions as func

# Azure Storage Account Info
AZURE_ACC_KEY = "..."
AZURE_ENDPOINT_SUFFIX = "..."
AZURE_ACC_NAME = "..."
AZURE_ENDPOINT = "{}.table.{}".format(AZURE_ACC_NAME, AZURE_ENDPOINT_SUFFIX)
AZURE_CONN_STR = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
    AZURE_ACC_NAME, AZURE_ACC_KEY, AZURE_ENDPOINT_SUFFIX
)
# Sucuri Info
SUCURI_API_URL = "https://waf.sucuri.net/api?v2"
SUCURI_API_KEY = "..."
SUCURI_SITES = [
    ...
]

def sucuri_to_blob(key, secret, date, mutex):
    mutex.acquire()
    body = requests.post(
        SUCURI_API_URL,
        data={
            "k": key,
            "s": secret,
            "a": "audit_trails",
            "date": date.strftime("%Y-%m-%d"),
            "format": "json",
            "limit": 1000
        }
    ).json()
    if len(body) > 6:
        for o in body:
            try:
                o["request_date"] = date.strftime("%d-%b-%Y")
                o["request_time"] = datetime.now().strftime("%H:%M:%S")
            except:
                pass
            else:
                try:
                    del o['geo_location']
                except KeyError:
                    continue
                except TypeError:
                    pass
        try:
            df = pd.DataFrame(body)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            pass
        else:
            df = df[df.is_usable != 0]
            data = df.to_csv(index=False)
            BLOB = '-'.join([
                domain,
                date.strftime("%Y-%m-%d"),
                '1000'
            ]) + '.csv'
            with BlobClient.from_connection_string(conn_str=AZURE_CONN_STR, container_name="...", blob_name=BLOB) as blob:
                try:
                    blob.upload_blob(data)
                except ResourceExistsError:
                    pass
    mutex.release()

def main(mytimer: func.TimerRequest):
    yesterday = datetime.now() - timedelta(1)
    threads = list()
    mtx = threading.Lock()
    for i in SUCURI_SITES:
        data = requests.post(
            SUCURI_API_URL,
            data={
                "k": SUCURI_API_KEY,
                "s": i['secret'],
                "a": "show_settings"
            }
        ).json()
        i['enabled'] = True if data['output']['proxy_active'] == 1 else False
        i['domain'] = data['output']['domain']
        i['key'] = SUCURI_API_KEY
        if i["enabled"]:
            x = threading.Thread(
                target=sucuri_to_blob,
                args=(
                    i["key"],
                    i["secret"],
                    yesterday,
                    mtx
                ), daemon=True
            )
            threads.append(x)
            x.start()
    for index, thread in enumerate(threads):
        thread.join()
