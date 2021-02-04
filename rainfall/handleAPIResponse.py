import json

import requests

import rabbitmqConnection
def getResponse(api):
    return requests.get(api)

def handleResponse(res, rabbit_connection_string, connectionAttemptInterval):

    if res.status_code != 200:
        # Send to debug topic

        # set up connection to  rabbitmq
        # start a channel

        connection = rabbitmqConnection.create(rabbit_connection_string, connectionAttemptInterval)
        channel = connection.channel()
        # rabbit config sets up: exchange='rabt-debug-exchange', queue='rabt-rainfall-debug'
        json_map = {}
        json_map["error"] = "Weather API returned status " + str(res.status_code)
        message = json.dumps(json_map)

        # send a message
        rabbitmqConnection.publish(channel, message, 'debug.rainfall', 'rabt-debug-exchange')
        print("Message sent to consumer (debug topic)")
