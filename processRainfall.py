import collections
import datetime
import csv
import json
import requests
import pika

def runAPICall(event, context):

    api_obs = []
    rain_rates = []
    averages = []
    average = 0
    prev_rain_total = 0
    current_rain_total = 0
    rain_last10mins = 0
    rain_rate_last10mins = 0
    rain_rate_average = 0.0
    rain_duration_in_mins = 0
    BASE_URL = 'localhost'

    # flag to indicate whether we want to send to rabbitmq
    send_message = 1

    # New hobo data download (IALEXA29 currently unavailable - ILOCHE16 updates 15 mins)
    #allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA29&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
    allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=ILOCHE16&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f" 
    api_obs = requests.get(allDay)

    # Handle unexpected responses by sending message to debug queue and restarting function
    if api_obs.status_code:
        if api_obs.status_code != 200:
            # Send to debug topic
            if (send_message == 1):

                # set up connection to  rabbitmq
                # todo handle failure to connect to queue?
                connection = pika.BlockingConnection(pika.ConnectionParameters(BASE_URL))
                if (connection):
                    # start a channel
                    channel = connection.channel()
                    # rabbit config sets up: exchange='rabt-debug-exchange', queue='rabt-rainfall-debug'
                    json_map = {}
                    json_map["error"] = "Weather API returned status " + str(api_obs.status_code)
                    message = json.dumps(json_map)

                    # send a message
                    channel.basic_publish(exchange='rabt-debug-exchange', routing_key='debug.rainfall',
                                          body=message)
                    print("Message sent to consumer (debug topic)")
                    connection.close()
                    # todo is this correct behaviour in prod or would this rerun kubeless function?
                    runAPICall(None, None)

    response = api_obs.json()

    # iterate through the array and add each element to the sum variable one at a time 
    def _sum(arr):   
        sum = 0 
        for i in arr: 
            sum = sum + i      
        return(sum) 

    # increment for each 10 minute period
    rain_duration_in_mins = rain_duration_in_mins + 10

    # loop through the data set using the total number of observations as a limit
    for i in range(len(response['observations'])):

        # get each rain rate measurement
        rain_rate_last10mins =response['observations'][i]['metric']['precipRate']

        # check for invalid values: if it's not the first reading use previous value instead, otherwise reset to zero
        if(rain_rate_last10mins > 300) or (rain_rate_last10mins < 0):
            if(i != 0):
                rain_rate_last10mins = response['observations'][i-1]['metric']['precipRate']
            else:      
                rain_rate_last10mins = 0.0

        # store all the rain rates
        rain_rates.append(rain_rate_last10mins)

        # if its not the first reading use the previous value
        if(i != 0):
            prev_rain_total=(response['observations'][i-1]['metric']['precipTotal'] )
        

        current_rain_total=(response['observations'][i]['metric']['precipTotal'] )
        rain_last10mins = (current_rain_total-prev_rain_total)
        rain_last10mins = round(rain_last10mins, 2)
        last_recorded_timeUTC=(response['observations'][i]['obsTimeUtc'] )
        
        ## format last recorded time
        last_recorded_time = datetime.datetime.strptime(last_recorded_timeUTC, "%Y-%m-%dT%H:%M:%SZ")
        # calculate the sum of all rain rate obs
        sum_of_rain_rates = _sum(rain_rates)
        sum_of_rain_rates = round(sum_of_rain_rates,2)

        # avoid division by zero on the first row
        if(i != 0):
            rain_rate_average = sum_of_rain_rates / i
            rain_rate_average = round(rain_rate_average, 2)

        # increment i
        i = i + 1

    # only send last values
    # this will send a a message to rabbitmq given that it connects correctly
    # if any consumer is running at the same time, the messages will travel through rabbitmq, otherwise they will wait in the 'rabt-rainfall' queue
    if(send_message == 1):

        print(last_recorded_time ,'|', rain_last10mins,'|', current_rain_total, '|', rain_rate_last10mins, '|', rain_rate_average, '|', rain_duration_in_mins, '\n') 
        
    
        # set up connection to  rabbitmq  
        connection = pika.BlockingConnection(pika.ConnectionParameters(BASE_URL))
        if(connection):
            # start a channel
            channel = connection.channel() 
            # rabbit config sets up: exchange='rabt-rainfall-exchange', queue='rabt-rainfall-queue'
            json_map = {}
            json_map["last recorded time"] = str(last_recorded_time)
            json_map["rain last 10 mins"] = rain_last10mins
            json_map["current rain total"] = current_rain_total
            json_map["rain rate last 10 mins"] = rain_rate_last10mins
            json_map["rain rate average"] = rain_rate_average
            json_map["rain duration in  mins"] = rain_duration_in_mins
            message = json.dumps(json_map)

            # send a message : routing key must match the queue name
            channel.basic_publish(exchange='rabt-rainfall-exchange', routing_key='rabt-rainfall-queue', body=message)
            print ("Message sent to consumer")
            connection.close()

    return(event)
