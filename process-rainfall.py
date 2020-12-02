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


# New hobo data download 
allDay="https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA29&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f"
response = requests.get(allDay)
#prevRainMeasuredTotal=(response.json()['observations'][-2]['metric']['precipTotal'] )
#lastRainMeasuredTotal=(response.json()['observations'][-1]['metric']['precipTotal'] )

with open('sample_rain_data.json') as f:
  response = json.load(f)

#print(response) 

# iterate through the array and add each element to the sum variable one at a time 
def _sum(arr):  
      
    sum = 0 
    for i in arr: 
        sum = sum + i 
          
    return(sum) 

# rounding function    
def round_minutes(dt, direction, resolution):
    new_minute = (dt.minute // resolution + (1 if direction == 'up' else 0)) * resolution
    return dt + datetime.timedelta(minutes=new_minute - dt.minute)

      
rain_rates = []
averages = []
average = 0
i = 0
prev_rain_total = 0
current_rain_total = 0
rain_last15mins = 0
rain_rate_last15mins = 0
rain_rate_average = 0
rain_duration = 0

print('DateTime|Rain last 15 mins|Total rainfall|Rain rate|Rain rate last 15 mins|Rainfall duration')

# loop through the data set using the total number of observations as a limit
for i in range(len(response['observations'])):

    # get each rain rate measurement
    rain_rate_last15mins =response['observations'][i]['metric']['precipRate']

    # check for invalid values, use previous value instead
    if(rain_rate_last15mins > 300) or (rain_rate_last15mins < 0):
        rain_rate_last15mins = =response['observations'][i-1]['metric']['precipRate'] 
    
    # add to array (for debug)
    rain_rates.append(rain_rate_last15mins)
    prev_rain_total=(response['observations'][i-1]['metric']['precipTotal'] )
    current_rain_total=(response['observations'][i]['metric']['precipTotal'] )
    rain_last15mins=round(current_rain_total-prev_rain_total)


    last_recorded_timeUTC=(response['observations'][i]['obsTimeUtc'] )
    ## format last recorded time
    last_recorded_time = datetime.datetime.strptime(last_recorded_timeUTC, "%Y-%m-%dT%H:%M:%SZ")
    print(last_recorded_time)
    time_rounded_down=round_minutes(last_recorded_time,'down',15)
    print(time_rounded_down)
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
        # increment for each 15 minute period
        rain_duration = rain_duration + 0.25
        print(time_rounded_down ,'|', rain_last15mins,'|', sum_of_rain_rates, '|', rain_rate_last15mins, '|', rain_rate_average, '|', rain_duration)
        
    i = i + 1
    
   
#print(rain_rates)
#print(averages)



