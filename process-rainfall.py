import collections

import hashlib
import hmac
import time
import datetime

import urllib.parse
import urllib.request
import json
import requests
import pandas as pd

api_obs = []
file_data = []
rain_rates = []
averages = []
average = 0
i = 0
prev_rain_total = 0
current_rain_total = 0
rain_last10mins = 0
rain_rate_last10mins = 0
rain_rate_average = 0
rain_duration = 0


# New hobo data download 
# uncomment this block to run with live api data
allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA29&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
api_obs = requests.get(allDay)
response = api_obs.json()

# run with static file data
#with open('sample_rain_data.json') as f:
  #file_data = json.load(f)

#response = file_data
#print(response) 

# iterate through the array and add each element to the sum variable one at a time 
def _sum(arr):   
    sum = 0 
    for i in arr: 
        sum = sum + i      
    return(sum) 
      
print('\nDateTime|Rain last 10 mins|Total rainfall|Rain rate|Rain rate last 10 mins|Rainfall duration\n')

# loop through the data set using the total number of observations as a limit
for i in range(len(response['observations'])):

    # get each rain rate measurement
    rain_rate_last15mins =response['observations'][i]['metric']['precipRate']

    # check for invalid values, use previous value instead
    if(rain_rate_last15mins > 300) or (rain_rate_last15mins < 0):
        rain_rate_last15mins = response['observations'][i-1]['metric']['precipRate'] 
    
    # add to array (for debug)
    rain_rates.append(rain_rate_last15mins)
    if(i != 0):
        prev_rain_total=(response['observations'][i-1]['metric']['precipTotal'] )
        print('prev_rain_total', prev_rain_total)
        current_rain_total=(response['observations'][i]['metric']['precipTotal'] )
        print('current_rain_total',  current_rain_total)
        rain_last15mins = (current_rain_total-prev_rain_total)
        rain_last15mins = round(rain_last10mins, 2)
        print('rain_last15mins', rain_last10mins, '\n')

    last_recorded_timeUTC=(response['observations'][i]['obsTimeUtc'] )
    ## format last recorded time
    last_recorded_time = datetime.datetime.strptime(last_recorded_timeUTC, "%Y-%m-%dT%H:%M:%SZ")
    print('last_recorded_time', last_recorded_time)
    # calculate the sum of all rain rate obs
    sum_of_rain_rates = _sum(rain_rates)
    sum_of_rain_rates = round(sum_of_rain_rates,2)
    # avoid division by zero on the first row
    if(i != 0):
        #print('row :', i, 'sum of rain rat :', sum_of_rain_rates, '\n')
        rain_rate_average = sum_of_rain_rates / i
        rain_rate_average = round(rain_rate_average, 2)
        # add to array for debug
        averages.append(rain_rate_average)
        # increment for each 10 minute period
        rain_duration = rain_duration + 10
        print(last_recorded_time ,'|', rain_last10mins,'|', sum_of_rain_rates, '|', rain_rate_last10mins, '|', rain_rate_average, '|', rain_duration, '\n')
    else:
        print(last_recorded_time ,'|', rain_last10mins,'|', sum_of_rain_rates, '|', rain_rate_last10mins, '|', rain_rate_average, '|', rain_duration, '\n')    
    i = i + 1
    
   
#print(rain_rates)
#print(averages)



