import requests
import json
import pandas as pd
import hashlib
import base64
import time
import os

def to_es_db(df, url, index_name):
    from elasticsearch import Elasticsearch, helpers
    import hashlib
    es = Elasticsearch(url)
    def gen_data():
        for row in df.itertuples():
            doc = {}
            for col_num,  col in enumerate(df.columns):
                doc.update({col: row[col_num+1]})
            yield {"_op_type": "create","_index": index_name,"_id":hashlib.md5(str(doc).encode()).hexdigest(), "_source":doc}
    helpers.bulk(es, gen_data())
    es.close()

def upload_file(path, url, index_name):
    with open(path, "rb") as f:
        file = f.read()
    file_base64 = base64.b64encode(file)
    id_ = hashlib.md5(file_base64).hexdigest()
    print(requests.put(url+"/"+index_name + "/_doc/"+id_+"?pipeline=attachment", data = json.dumps({"data":file_base64.decode('utf-8'),"filename":os.path.basename(path)}),headers = {"Content-Type": "application/json"}).text)
    print(requests.post(url+"/"+index_name + "/_doc/"+id_+"/_update", data=json.dumps({"script": "ctx._source.remove('data')"}), headers = {"Content-Type": "application/json"}).text)

def show_es_old(url, index_name, search_col = False, search_word = False, size=10, from_ = 0):
    from elasticsearch import Elasticsearch
    es = Elasticsearch(url)
    if search_col and search_word:
        query = {"match":{search_col: search_word}}
    else:
        query = None
    res = es.search(index=index_name, size = size, from_ = from_, query = query)
    es.close()
    return res

def show_es(url, index_name, search_col=[] , search_word = False, size=10, from_ = 0):
    import requests
    import json
    query_dict = {
      "query": {
        "multi_match": {
          "query": search_word,
          "fields": search_col + ["attachment.content"],
          #"type": "phrase",
          "fuzziness": "AUTO" 
        }
      },
      "highlight": {
        "fields": {
          "attachment.content": {
            "post_tags": [
              "</strong>"
            ],
            "pre_tags": [
              "<strong>"
            ]
          }
        },
        "fragment_size": 100,
        "number_of_fragments": 1,
        "fragmenter": "plain"
      }
    }

    for col in search_col:
        query_dict["highlight"]["fields"].update({col:{'post_tags': ['</strong>'], 'pre_tags': ['<strong>']}})

    query = json.dumps(query_dict)
    res = json.loads(requests.get(url+"/"+index_name + "/_search?size="+str(size)+"&from="+str(from_), data = query, headers = {"Content-Type": "application/json"}).text)
    print(res)
    return res

#Elasticsearchが起動するまで待つ関数
def wait_til_es(url):
    while(True):
        try:
            requests.get(url)
        except :
            time.sleep(5)
            continue
        time.sleep(5)
        break