
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ['https://es.rabt.ncldata.dev/'],
    http_auth=('elastic', os.environ['ES_PASSWORD']),
    # turn on SSL
    use_ssl=True,
    # make sure we verify SSL certificates
    verify_certs=True
)

if not es.ping():
    raise ValueError("Connection failed")


def runAPICall(event, context):
    confirmation_message = getStormData()
    return confirmation_message

# function to query ElasticSearch for any rainfall data in the 48 hours and then examine that data to see if we have a enough rain to merit recording a storm event. Any rainfall should be preceded by a dry period, which is defined by using a variable: 'number_of_zeros'. The average amount of rain is then calculated and compared to a set limit, defined by a variable: 'rain_threshold'.
def getStormData():

   # create blank message
    confirmation_message = ''
    # set the threshold over which limit data will be recorded as a storm event
    rain_threshold = 0.2
    # set the number of zeros to be used as the measure of a dry period
    number_of_zeros = 36
    # initialise to zero
    duration_in_mins = 0

    # query Elasticsearch for all values in the last 48 hours
    res = es.search(index="rabt-rainfall-*", body={"sort": [{"@timestamp": {"order": "asc"}}],"query":  {"bool": {"filter": [ { "range" : { "@timestamp" : { "gte" : "now-48h" } } }, { "range" : { "rain-last-10-mins" : { "gte" : 0.0 } } } ]}}}, size=288)

    # check that we have some results
    if(res['hits']['hits'] != []):

        # declare a dataframe
        df = pd.DataFrame()
    
        # for each 'hit' add to the dataframe
        for hit in enumerate(res['hits']['hits']):
            dict_new = dict(hit[1]['_source'])
            df = df.append(dict_new, ignore_index=True)

        # declare a empty list
        lastindex = []
       
        # check size of groups having 0 value
        for k, v in df[df['rain-rate-average']== 0].groupby((df['rain-rate-average'] != 0).cumsum()):
            groupsize  = v.shape[0]
            # this gets the most recent time period where there are more than the set limit of zero values
            if(groupsize >= number_of_zeros) :
                # get the last row in that set i.e. the last time there was a zero value before it started raining
                lastrow = v.tail(1)
                # get the row index (the data type is list)
                lastindex = lastrow.index


        if(lastindex[0]):
            # get rows from the one after the lastindex onwards, by slicing from the index value(+1) to the end of the original dataframe  
            resdf = df.iloc[lastindex[0]+1:-1]
      
            # check that the mean of rain-rate-average is over the set threshold
            if(resdf['rain-rate-average'].mean() > rain_threshold):
            
                # create a storm event in ElasticSearch
                # set create an ElasticSearch index using the current date
                stormindex = 'storm-event-' + datetime.today().strftime('%Y-%m-%d')
                # loop through the dataframe, convert each row to json, then send to ElasticSearch using the same index
                for i in resdf.index:
                    # increase the duration each time so we can map against intensity-threshold data in powerBi
                    duration_in_mins = duration_in_mins + 10
                    stormdata = resdf.loc[i].to_json()
                    stormdata = json.loads(stormdata)
                    new_json_field = {"duration_in_mins": duration_in_mins} 
                    # add the duration in mins
                    stormdata.update(new_json_field)
                    # save the data to ElasticSearch
                    res = es.index(index=stormindex, body=stormdata)
                    # should return 'created'
                    #print(res['result'])
                confirmation_message = 'Storm data sent'
            else: 
                confirmation_message = 'Not enough rain'    
        else:
            confirmation_message = 'No storm data' 

 
    else:
        confirmation_message = 'No results'


    # close the connection to ElasticSearch
    es.close() 
    return(confirmation_message) 