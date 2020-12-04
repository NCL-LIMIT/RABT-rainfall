## RABT-rainfall

This project contains files to process and test rainfall data from Rest-and-Be-Thankful rain sensors via a weather api.

The HOBOnet sensors live on the RABT hillside and work with a HOBOnet Station Data Logger to send information to www.hobolink.com. The HOBOnet application has a data feed that sends rainfall data to Weather Underground. Data arrives from the weather api every 10 minutes from midnight onwards. Their api is at:  https://api.weather.com/v2/pws/observations/all/1day?stationId=IALEXA29&format=json&units=m&apiKey=4a83daf5d1b3462d83daf5d1b3f62d8f.

The process-rainfall.py file can be configured to run from the api, or accept test json input from file. The output from the script can be directed to a csv file or the RabbitMQ message broker

### RabbitMQ

A local instance of RabbitMQ can be created by using the following Docker commands at the command prompt (tested on Windows only).

```
docker pull rabbitmq:3-management
```
```
docker run -d -p 15672:15672 -p 5672:5672 --name rabbit-test rabbitmq:3-management
```

If Docker is successful a GUID will be output at the terminal. The RabbitMQ management portal will also be accessible at: http://localhost:15672/#/ 
(username: guest, password: guest).

After running the process-rainfall.py file with the send_message flag enabled, messages should appear in the RabbitMQ 'rainfall' queue, unless the consumer.py file is running in a separate terminal, in which case the messages will pass straight through to that terminal. The consumer.py program stays open listening for messages, but will eventually time out if none are received.
