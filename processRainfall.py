import datetime
import time
import requests
import json
import pika
import os


def runAPICall(event, context):
    averages = []
    average = 0

    # flag to indicate whether we want to send to rabbitmq
    send_message = 1

    # New hobo data download (IALEXA29 currently unavailable - ILOCHE16 updates 15 mins)
    # allDay = "https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA29&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
    # allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=ILOCHE16&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
    allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=IGIFFNOC2&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
    api_obs = requests.get(allDay)

    # handle API response by creating message and publishing to appropriate queue
    confirmation_message = handleResponse(api_obs, send_message)
    return confirmation_message


def handleResponse(res, send_message):
    # rabbit_connection_string = 'amqp://oF4pn_zQff8sisySjKAbm-vOzgG83NvR:1SBFwoAL5IuTa7C7IkaLNvlfgPgbb5ff@rabt-mq:5672/%2F'
    rabbit_connection_string = os.environ['RABBIT_CONNECTION_STRING']
    # rabbit_connection_string = 'amqp://guest:guest@localhost:5672/%2F'

    # rabbit_connection_string = os.environ.get('RABBIT_CONNECTION_STRING')
    connectionAttemptInterval = 10  # interval to retry to connect to rabbitMQ in seconds

    confirmation_message = 'No message sent'

    if res.status_code == 200:

        response = res.json()

        # generate values to publish to queue
        message = createRainfallMessage(response)

        # only send last values
        # this will send a a message to rabbitmq given that it connects correctly
        # if any consumer is running at the same time, the messages will travel through rabbitmq, otherwise they will wait in the 'rabt-rainfall' queue

        # set up connection to  rabbitmq
        connection = create(rabbit_connection_string, connectionAttemptInterval)

        # send a message : routing key must match the queue name
        if send_message == 1:
            publish(connection, message, 'rabt-rainfall-queue', 'rabt-rainfall-exchange', 'direct', 'rabt-rainfall-queue')
            print("Message sent to consumer")
            confirmation_message = "Message sent to consumer"

    else:
        # Unexpected status code so send to debug topic
        connection = create(rabbit_connection_string, connectionAttemptInterval)

        json_map = {}
        json_map["error"] = "Weather API returned status " + str(res.status_code)
        message = json.dumps(json_map)

        # send a message
        if send_message == 1:
            publish(connection, message, 'rabt-debug-rainfall', 'rabt-debug-exchange', 'topic', 'debug.rainfall')
            print("Message sent to consumer (debug topic)")
            confirmation_message = "Message sent to consumer (debug topic)"

    return confirmation_message


def createRainfallMessage(response):
    prev_rain_total = 0
    current_rain_total = 0
    rain_last10mins = 0
    rain_rate_average = 0.0

    # loop through the data set using the total number of observations as a limit
    for i in range(len(response['observations'])):

        # get each rain rate measurement
        rain_rate_average = response['observations'][i]['metric']['precipRate']

        # check for invalid values: if it's not the first reading use previous value instead, otherwise reset to zero
        if (rain_rate_average > 300) or (rain_rate_average < 0):
            if (i != 0):
                rain_rate_average = response['observations'][i - 1]['metric']['precipRate']
            else:
                rain_rate_average = 0.0

        # if its not the first reading use the previous value
        if (i != 0):
            prev_rain_total = (response['observations'][i - 1]['metric']['precipTotal'])

        current_rain_total = (response['observations'][i]['metric']['precipTotal'])
        rain_last10mins = (current_rain_total - prev_rain_total)
        rain_last10mins = round(rain_last10mins, 2)
        last_recorded_timeUTC = (response['observations'][i]['obsTimeUtc'])
        ## format last recorded time
        last_recorded_time = datetime.datetime.strptime(last_recorded_timeUTC, "%Y-%m-%dT%H:%M:%SZ")

        # increment i
        i = i + 1

    json_map = {}
    json_map["last-recorded-time"] = str(last_recorded_time)
    json_map["rain-last-10-mins"] = rain_last10mins
    json_map["current-rain-total"] = current_rain_total
    json_map["rain-rate-average"] = rain_rate_average

    message = json.dumps(json_map)
    print(last_recorded_time, '|', rain_last10mins, '|', current_rain_total, '|',
          rain_rate_average,  '\n')

     
    return message


# Create or attempt to create a connection to rabbitMQ
def create(rabbit_connection_string, attempt_interval):
    attempts = 1
    parameters = pika.URLParameters(rabbit_connection_string)
    maxAttempts = 10

    # try to connect
    while attempts < maxAttempts + 1:
        try:
            connection = pika.BlockingConnection(parameters)
            return connection

        except Exception as e:
            print("Connection error, retrying. Attempt " + str(attempts))
            time.sleep(attempt_interval)
            attempts += 1

            # give up and throw exception
            if attempts == maxAttempts + 1:
                raise Exception('Cannot connect to RabbitMQ ' + str(e))


# Publish a message to the queue and close connection
def publish(
        connection,
        body,
        queue,
        exchange,
        exchange_type,
        key
):
    # todo error handling as above?

    # create channel, exchange and queue
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True, auto_delete=False,internal=False)
    channel.queue_declare(queue=queue, durable=True, auto_delete=False)
    channel.queue_bind(exchange=exchange, queue=queue, routing_key=key)

    # publish message
    channel.basic_publish(exchange=exchange, routing_key=key, body=body)

    # close connection
    if connection.is_open:
        connection.close()
