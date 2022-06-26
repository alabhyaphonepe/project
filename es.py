import imp
from elasticsearch import Elasticsearch
from datetime import datetime
from pprint import pprint
import socket

hostname=socket.gethostname()   
ipaddr=socket.gethostbyname(hostname)   

es = Elasticsearch(ipaddr, port=9200)

val = int(input("Enter 1 to index data \nEnter 2 to search \n"))


if val == 1:
    file_name = input("Enter file name \n")
    with open(file_name, 'r') as file:
        data = file.read()

    doc = {
        'title': file_name,
        'data': data,
        'hostname': hostname,
        'timestamp': datetime.now(),
    }

    res = es.index(index="test-index", document=doc)
    es.indices.refresh(index="test-index")
    pprint(res['result'])

elif val == 2:
    search = str(input("Enter text to search \n"))
    res = es.search(index="test-index",query={"bool": {"must": {"match": {"data": search}}}})
    pprint(res)

    print("\n\n\n\n\n\n ================================== \n\n\n\n\n\n")
    #pprint("Got %d Hits:" % res['hits']['total']['value'])


    #for hit in res['hits']['hits']:
        #pprint(hit['good_summary'])
        #pprint("%(timestamp)s %(title)s: %(data)s" % hit["_source"])

