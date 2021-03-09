
import pandas as pd
import numpy as np
import json
from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ['localhost'],
    http_auth=('elastic', 'N3KLm07g303vFAu7rz9KQ2K8'),
    scheme="https",
    port=9200,
    verify_certs=False,
    ssl_show_warn=False
)


# set expected rows
numberOfRows = 144
# create dataframe
df = pd.DataFrame(index=np.arange(0, numberOfRows), columns=('last-recorded-time', 'rain-rate-average') )
print(df)

# query Elasticsearch for all values in the last 48 hours
res = es.search(index="rabt-rainfall-*", body={"query":  {"bool": {"filter": [ { "range" : { "@timestamp" : { "gte" : "now-48h" } } }, { "range" : { "rain-rate-average" : { "gte" : 0.0 } } } ]}}}, size=144)

print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
  # print("%(last-recorded-time)s: %(rain-rate-average)s" % hit["_source"])

   print(type(hit["_source"]))

   row_list = []
   row_list.append(hit["_source"])


   #data = json.dumps(hit["_source"])
   #print(data)

   #last-recorded-time = data["last-recorded-time"]
   #rain-rate-average = hit["_source"]["rain-rate-average"]

   #datadict[0] =  hit["_source"]["last-recorded-time"]
   #datadict[1] = hit["_source"]["rain-rate-average"]

     # dict = {'lrt': last-recorded-time, 'rra' : rain-rate-average }
  # for x in np.arange(0, numberOfRows):
    #loc or iloc both work here since the index is natural numbers
   # df.loc[x] = [np.random.randint(-1,1) for n in range(3)]

print(row_list)
