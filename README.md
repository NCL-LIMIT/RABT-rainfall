## RABT-rainfall

This project contains files to process and test rainfall data from Rest-and-Be-Thankful rain sensors via a weather api.

The HOBOnet sensors live on the RABT hillside and work with a HOBOnet Station Data Logger to send information to www.hobolink.com. The HOBOnet application has a data feed that sends rainfall data to Weather Underground. Data arrives from the weather api every 10 minutes from midnight onwards. Their api is at:  https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA29&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f.


The process-rainfall.py file can be configured to run from the api, or accept test json input from file. The output from the script can be directed to a csv file or to RabbitMQ.


### RabbitMQ and the RELK stack

RabbitMQ forms part of the RELK stack that also contains ElasticSearch, Logstash and Kibana.

Please see the readme at :
https://github.com/NCL-LIMIT/RABT-Infrastructure/tree/main/docker-relk

It has instructions on how to set up and access the RELK stack. Messages are passed through the RabbitMQ exchange to ElasticSearch via a Logstash consumer. Messages are visible in Kibana's UI.