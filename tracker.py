import os
import sys
import time
import socket
from elasticsearch import Elasticsearch
from pprint import pprint
from datetime import datetime

first_run = True
doc_id = None

file_path = input("Enter the absolute path of your file: ")


class Watcher(object):
    running = True
    refresh_delay_secs = 1

    # Constructor
    def __init__(self, watch_file, call_func_on_change=None, *args, **kwargs):
        self._cached_stamp = 0
        self.filename = watch_file
        self.call_func_on_change = call_func_on_change
        self.args = args
        self.kwargs = kwargs

    # Look for changes
    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            # File has changed, so do something...
            if self.call_func_on_change is not None:
                self.call_func_on_change(*self.args, **self.kwargs)

    # Keep watching in a loop
    def watch(self):
        while self.running:
            try:
                # Look for changes
                time.sleep(self.refresh_delay_secs)
                self.look()
            except KeyboardInterrupt:
                print("\nDone")
                break
            except FileNotFoundError:
                # Action on file not found
                pass
            except:
                print("Unhandled error: %s" % sys.exc_info()[0])


# Call this function each time a change happens
def custom_action(file_name):
    global first_run
    global doc_id

    es = Elasticsearch("10.57.57.106", port=9200)

    with open(file_name, "r") as file:
        data = file.read()

    doc = {
        "title": file_name,
        "data": data,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(),
    }

    if not first_run:
        res = es.index(index="test-index", id=doc_id, document=doc)
        es.indices.refresh(index="test-index")
        print(res["result"])

    else:
        first_run = False
        res = es.index(index="test-index", document=doc)
        es.indices.refresh(index="test-index")
        doc_id = res["_id"]
        pprint(res["result"])


watch_file = file_path

# watcher = Watcher(watch_file)  # simple
watcher = Watcher(
    watch_file, custom_action, file_name=watch_file
)  # also call custom action>
watcher.watch()  # start the watch going
