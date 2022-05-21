from typing import Callable, Optional, Tuple, List, Dict, Union
import datetime
import pandas as pd
import pytz
import re

from requests import delete
import logging

def datetime_ago(
    window_days: int, 
    end_date: Optional[datetime.datetime] = None, 
    date_format:str = '%Y-%m-%d'
) -> Tuple[str, str]:
    if not end_date:
        end_date = datetime.datetime.now()
    start_date_str: str = (end_date - datetime.timedelta(days=window_days)).strftime(date_format)
    end_date_str: str = end_date.strftime(date_format)
    return (start_date_str, end_date_str)


def list_unique(seq:list, idfun:Callable=None) -> list: 
    '''
    Preserves ordering
    Complexity O(n)
    '''
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        item = idfun(item)
        if item in seen: continue
        seen[item] = 1
        result.append(item)
    return result
    
def crop_string(s:str, th:int=22) -> str:
    if len(s) > (th-3):
        return s[:th-3] + '...'
    else:
        return s


def hours2pretty(hours:float) -> str:
    if hours<1:
        return str(int(hours*60)) + 'min'
    elif hours<72:
        return str(int(hours)) + 'h ' + str(int((hours%1)*60)) + 'min'
    else:
        return str(int(hours/24)) + 'd ' + str(int(hours%24)) + 'h ' + str(int((hours%1)*60)) + 'min'

def simplify_string(s:str) -> str:
    return s.lower()

def translate_names(s:str, aggregator:str='Title', translations:dict={}) -> str:
    '''
    `translations` should be in the structure `aggregator -> original fragment -> translated fragment`
    '''
    final = s
    if aggregator in translations:
        for translation in translations[aggregator]:
            if simplify_string(translation) in simplify_string(s):
                final = translations[aggregator][translation]
    return final




def str_match_prefixes(s, prefixes:List[str], case_sensitive:bool=True) -> bool:
    if case_sensitive:
        return any([s[:len(prefix)]==prefix for prefix in prefixes])    
    else:
        return any([s[:len(prefix)].lower()==prefix.lower() for prefix in prefixes]) 
#assert str_match_prefixes('oioi', ['oi'])==True
#assert str_match_prefixes('oi123', ['oi'])==True
#assert str_match_prefixes('oioi', ['oi', 'xau'])==True
#assert str_match_prefixes('oioi', ['xau', 'oi'])==True
#assert str_match_prefixes('oioi', ['xau'])==False
#assert str_match_prefixes('oioi', ['OI'])==False
#assert str_match_prefixes('oioi', ['OI'], case_sensitive=False)==True

####
## Azure storage
# Version 0.1.0

from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions

def conn_string2account_key(connection_string:str) -> str:
    pattern = f';AccountKey=(.*?);'
    result = re.findall(pattern, connection_string)
    if len(result)==0:
        raise ValueError('Invalid connection string')
    return result[0]

def conn_string2account_name(connection_string:str) -> str:
    pattern = f';AccountName=(.*?);'
    result = re.findall(pattern, connection_string)
    if len(result)==0:
        raise ValueError('Invalid connection string')
    return result[0]

def blob_upload(connection_string:str, container:str, filename:str, content:Union[bytes, str], overwrite: bool = False) -> dict:
    if blob_exists(connection_string, container, filename):
        if overwrite:
            logging.info('Overwriting existing file')
            blob_delete(container, connection_string, filename)
        else:
            raise Exception('File already exists')
    blob_client = BlobClient.from_connection_string(connection_string, container, filename)
    r = blob_client.upload_blob(content)
    return r


def blob_exists(connection_string:str, container:str, filename:str) -> bool:
    blob_client = BlobClient.from_connection_string(connection_string, container, filename)
    return blob_client.exists()

def blob_download_link(connection_string, container, filename, hours=1):
    account_name = conn_string2account_name(connection_string)
    sas_blob = generate_blob_sas(
        account_name=account_name, 
        container_name=container,
        blob_name=filename,
        account_key=conn_string2account_key(connection_string),
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    )
    url = 'https://'+account_name+'.blob.core.windows.net/'+container+'/'+filename+'?'+sas_blob
    return url

def blob_upload_and_generate_link(connection_string:str, container:str, filename:str, content:Union[bytes, str], hours:int=1, overwrite: bool = False) -> str:
    r = blob_upload(connection_string, container, filename, content, overwrite=overwrite)
    if not r:
        raise Exception('Could not upload file')
    url = blob_download_link(connection_string, container, filename, hours=hours)
    return url

def blob_reupload(container:str, connection_string:str, filename:str) -> bytes:
    '''
    Download, delete and reupload blob
    This function can potencially cause data loss: if the upload fail, the blob is gone
    The blob content is returned, in case you want to handle this error
    '''
    blob_client = BlobClient.from_connection_string(connection_string, container, filename)
    content = blob_client.download_blob().readall()
    assert content!=None
    try:
        blob_client.delete_blob()
        r = blob_client.upload_blob(content)
        assert r!=None
    except:
        pass
    return content
    
def blob_delete(container:str, connection_string:str, filename:str) -> None:
    blob_client = BlobClient.from_connection_string(connection_string, container, filename)
    blob_client.delete_blob()

def blob_delete_all(connection_string:str, container:str, prefixes:List[str]=None):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container)
    total = 0
    for blob in container_client.list_blobs():
        if prefixes and not str_match_prefixes(blob.name, prefixes):
            continue
        total += 1
        blob_delete(connection_string=connection_string, container=container, filename=blob.name)
    return total
    
def blob_reupload_old(container:str, connection_string:str, date:datetime.datetime, prefixes:List[str]=None):
    '''
    Delete and upload all files older than a given date
    '''
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container)
    total = 0
    for blob in container_client.list_blobs():
        if blob.last_modified > date:
            if prefixes and not str_match_prefixes(blob.name, prefixes):
                continue
            total += 1
            blob_reupload(container, connection_string, blob.name)
    return total

def blob_download(connection_string:str, container:str, filename:str, filename_local: Optional[str]) -> Tuple[str, bytes]:
    blob_client = BlobClient.from_connection_string(connection_string, container, filename)
    content = blob_client.download_blob().readall()
    assert content!=None
    if filename_local:
        with open(filename_local, 'wb') as f:
            f.write(content)
    return content

def blob_get_file(container:str, connection_string:str, prefix:str=None) -> Tuple[str, bytes]:
    '''
    Get one file from the given prefix
    '''
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container)

    for blob in container_client.list_blobs():
        if prefix and blob.name[:len(prefix)] == prefix:
            last_blob = container_client.get_blob_client(blob)
            break
    return last_blob.blob_name, last_blob.download_blob().readall()

def blob_get_last_file(container:str, connection_string:str, prefix:str=None) -> Tuple[str, bytes]:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container)
    last_modified = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)
    last_blob = None
    for blob in container_client.list_blobs():
        if blob.last_modified > last_modified:
            if prefix and blob.name[:len(prefix)] != prefix:
                continue
            last_modified = blob.last_modified
            last_blob = container_client.get_blob_client(blob)
    return last_blob.blob_name, last_blob.download_blob().readall()

def blob_download_folder(connection_string:str, container:str, path_cloud:str, path_local:str) -> None:
    '''
    :param path_cloud Prefix that will determine if the file is downloaded
    :param folder to where the files will be downloaded; should not contain a trailling `/`; path must exists
    '''
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container)
    for blob in container_client.list_blobs():
        if blob.name[:len(path_cloud)] == path_cloud:
            blob_client = container_client.get_blob_client(blob)
            with open(f'{path_local}/{blob_client.blob_name}', 'wb') as f:
                f.write(blob_client.download_blob().readall())

def blob_last_modified(container:str, connection_string:str):
    '''
    Return info about the last modified file in a given container
    '''
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container)
    last_modified = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)
    last_name = None
    total = 0
    for blob in container_client.list_blobs():
        total += 1
        if blob.last_modified > last_modified:
            last_modified = blob.last_modified
            last_name = blob.name
    return last_modified, last_name, total
