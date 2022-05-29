# coding=<UTF-8>

from flask import Flask, render_template, request, Markup
from elasticsearch import Elasticsearch
import os


app = Flask(__name__)
es = Elasticsearch('127.0.0.1', port=9200)


@app.route('/')
def home():
  mypath = "../listoffiles"
  onlyfiles = [f for f in os.listdir(mypath)]
  return render_template('search.html', dirs=onlyfiles)


@app.route('/search/results', methods=['GET','POST'])
def request_search():
    mypath = "../listoffiles"
    onlyfiles = [f for f in os.listdir(mypath)]
    search_term = request.form["input"]
    regfilter = request.form["regfilter"]
    res = es.search(
    index='sync_demo',
    body = {
    "query": {
      "bool": {
        "must": [{
          "simple_query_string": {
            "fields": ["content"],
            "query": search_term
          }
        }, {
          "simple_query_string": {
            "fields": ["path.virtual"],
            "query": regfilter
          }
        }]
      }
    },
    "highlight": {
      "pre_tags": ["<span style='background-color: yellow;'>"],
      "post_tags": ["</span>"],
      "fields": {
        "content": {}
      }
    }
    })
    res['ST']=search_term
    
    for hit in res['hits']['hits']:
        dd =""
        for each in hit['highlight']['content']:
            dd += each.replace("\n","<br>")
        htext = Markup(dd)
        hit['good_summary'] = htext

    return render_template('results.html', res=res, dirs=onlyfiles)


if __name__ == '__main__':
    app.run('0.0.0.0',port=5005, debug=True)


'''
GET /multiple_hosts/_search
{
  "query": {
    "bool": {
      "must": {
        "simple_query_string": {
          "query": "port"
        }
      },
      "filter": {
        "regexp": {
          "path.virtual": "/host1/.*"
        }
      }
    }
  }
}


GET /multiple_hosts/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "query_string": {
            "default_field": "content",
            "query": "port"
          }
        },
        {
          "simple_query_string": {
            "fields": ["path.virtual"],
            "query": "/host2/ttys and /host2/gettytab"
          }
        }
      ]
    }
  }
}
'''