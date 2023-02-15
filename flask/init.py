from functions import *
import os
import pandas as pd
import json
import time
import requests

url = "http://es01:9200"

wait_til_es(url)
#初期登録
dir_ = "../data/db/"
for filename in os.listdir(dir_):
    path = os.path.join(dir_, filename)
    df = pd.read_csv(path, encoding = "shift_jis", index_col=0)
    to_es_db(df, url, "df")

dir_ = "../data/file/"
setting_query = json.dumps({"description" : "Extract attachment information","processors" : [{"attachment" : {"field" : "data"}}]})

requests.put(url + "/_ingest/pipeline/attachment", data = setting_query, headers = {"Content-Type": "application/json"})
for filename in os.listdir(dir_):
    path = os.path.join(dir_, filename)    
    upload_file(path, url, "df")