
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


""" es = Elasticsearch(
    ['https://es.rabt.ncldata.dev/'],
    http_auth=('elastic', os.environ['ES_PASSWORD']),
    # turn on SSL
    use_ssl=True,
    # make sure we verify SSL certificates
    verify_certs=True,
    # provide a path to CA certs on disk
    ca_certs='/path/to/CA_certs'
) """

if not es.ping():
    raise ValueError("Connection failed")

def runAPICall(event, context):
    confirmation_message = getStormData()
    return confirmation_message

def getStormData:
   # query Elasticsearch for all values in the last 48 hours
    res = es.search(index="rabt-rainfall-*", body={"sort": [{"@timestamp": {"order": "asc"}}],"query":  {"bool": {"filter": [ { "range" : { "@timestamp" : { "gte" : "now-7d" } } }, { "range" : { "rain-last-10-mins" : { "gte" : 0.0 } } } ]}}}, size=288)

    # check that we have some results
    if(res['hits']['hits'] != []):

        # declare a dataframe
        df = pd.DataFrame()
    
        # for each 'hit' add to the dataframe
        for hit in enumerate(res['hits']['hits']):
            dict_new = dict(hit[1]['_source'])
            df = df.append(dict_new, ignore_index=True)

        # declare a empty list and blank message
        lastindex = []
        confirmation_message = ''

        # check size of groups having 0 value
        for k, v in df[df['rain-rate-average']== 0].groupby((df['rain-rate-average'] != 0).cumsum()):
            groupsize  = v.shape[0]
            # this gets the most recent time period where there are more than 30 zero values
            if(groupsize >=20) :
                # get the last row in that set i.e. the last time there was a zero value before it started raining
                lastrow = v.tail(1)
                # get the row index (the data type is list)
                lastindex = lastrow.index


        if(lastindex[0]):
            # get rows from the one after the lastindex onwards, by slicing from the index value(+1) to the end of the original dataframe  
            resdf = df.iloc[lastindex[0]+1:-1]
            #print(resdf['rain-rate-average'].mean())

            # check that the mean of rain-rate-average is over 0.2
            if(resdf['rain-rate-average'].mean() > 0.2):
            
                # create a storm event in ElasticSearch
                stormindex = 'storm-event-' + datetime.today().strftime('%Y-%m-%d')
                # loop through the dataframe, convert each row to json, then send to ElasticSearch using the same index
                for i in resdf.index:
                    stormdata = resdf.loc[i].to_json()
                    res = es.index(index=stormindex, body=stormdata)
                    # should return 'created'
                    #print(res['result'])
                confirmation_message = 'Storm data sent'
            else: 
                confirmation_message = 'Not enough rain'    
        else:
            confirmation_message = 'No storm data'            


        # close the connection to ElasticSearch
        es.close()
        return(confirmation_message)


    else:
        print('no results')