import collections

import time
import datetime
import csv

import json
import requests
import pika

def runAPICall(event, context):

    api_obs = []
    file_data = []
    rain_rates = []
    averages = []
    average = 0
    prev_rain_total = 0
    current_rain_total = 0
    rain_last10mins = 0
    rain_rate_average = 0.0
    rain_rate_av = ""

    # flag to indicate whether we want to send to rabbitmq
    send_message = 1
    # flag to indciate whether to write to file
    write_to_file = 0


    # run with static file data
    with open('sample_rain_data.json') as f:
        file_data = json.load(f)

    response = file_data
    #print(response) 


    print('\nDateTime|Rain last 10 mins|Total rainfall|Rain rate|Rain rate last 10 mins|Rainfall duration\n')

    # if write to file is required, open the file handle and write the header
    if(write_to_file ==1):
        with open('rain_data_out.csv', mode='w',  newline='') as csv_file:
            fieldnames = ['last recorded time', 'rain last 10 mins', 'current rain total', 'rain rate last 10 mins', 'rain rate average', 'rain duration in mins' ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    # loop through the data set using the total number of observations as a limit
    for i in range(len(response['observations'])):

        # get each rain rate measurement
        rain_rate_average =response['observations'][i]['metric']['precipRate']

        # check for invalid values: if it's not the first reading use previous value instead, otherwise reset to zero
        if(rain_rate_average > 300) or (rain_rate_average < 0):
            if(i != 0):
                rain_rate_average = response['observations'][i-1]['metric']['precipRate']
            else:      
                rain_rate_average = 0.0

    
        # if its not the first reading use the previous value
        if(i != 0):
            prev_rain_total=(response['observations'][i-1]['metric']['precipTotal'] )
        
        current_rain_total=(response['observations'][i]['metric']['precipTotal'] )
        rain_last10mins = (current_rain_total-prev_rain_total)
        rain_last10mins = round(rain_last10mins, 2)
        last_recorded_timeUTC=(response['observations'][i]['obsTimeUtc'] )
        ## format last recorded time
        last_recorded_time = datetime.datetime.strptime(last_recorded_timeUTC, "%Y-%m-%dT%H:%M:%SZ")

        print(last_recorded_time ,'|', rain_last10mins,'|', current_rain_total, '|',  rain_rate_average, '\n') 
        
        # write each row to file
        if (write_to_file == 1):
            writer.writerow({'last recorded time': last_recorded_time, 'rain last 10 mins': rain_last10mins, 'current rain total': current_rain_total, 'rain rate average': rain_rate_average })


        if(send_message == 1):

            # set up connection to  rabbitmq  
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            if(connection):
                channel = connection.channel() # start a channel

                # not needed now as set up in rabbit config
                # channel.exchange_declare(exchange='rabt-rainfall-exchange', exchange_type='direct')
                # channel.queue_declare(queue='rabt-rainfall-queue') # declare a queue, then bind the queue to the exchange
                # channel.queue_bind(queue='rabt-rainfall-queue', exchange='rabt-rainfall-exchange', routing_key='rabt-rainfall-queue')

                # send a message
                # routing key must match the queue name

                json_map = {}
                json_map["last-recorded-time"] = str(last_recorded_time)
                json_map["rain-last-10-mins"] = rain_last10mins
                json_map["current-rain-total"] = current_rain_total
                json_map["rain-rate-average"] = rain_rate_average
                message = json.dumps(json_map)
                
                channel.basic_publish(exchange='rabt-rainfall-exchange', routing_key='rabt-rainfall-queue', body=message)
                print ("Message sent to consumer")
                connection.close()
            

            # this will send a a message to rabbitmq given that it connects correctly
            # if consumer.py is running at the same time, the messages will appear in the console, otherwise they will wait in the 'rainfall' queue

            # increment i
            i = i + 1

    return(event)


runAPICall(None,None)    

