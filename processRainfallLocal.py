import time
import requests
from handleAPIResponse import handleResponse

def runAPICall(event, context):
    averages = []
    average = 0

    # flag to indicate whether we want to send to rabbitmq
    send_message = 1

    # allDay = "https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA829&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
    allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=ILOCHE16&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
    api_obs = requests.get(allDay)

    # handle API response by creating message and publishing to appropriate queue
    handleResponse(api_obs, send_message)
    return (event)

runAPICall(None, None)
