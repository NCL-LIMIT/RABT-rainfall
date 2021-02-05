import time
import pika

# Create or attempt to create a connection to rabbitMQ
def create(rabbit_connection_string, attempt_interval):
    attempts = 0
    parameters = pika.URLParameters(rabbit_connection_string)

    # try to connect
    while attempts < 10:
        try:
            connection = pika.BlockingConnection(parameters)
            return connection

        except pika.exceptions:
            print("Connection error, retrying. Attempt " + str(attempts))
            time.sleep(attempt_interval)
            attempts += 1

    # give up and throw exception
    raise ConnectionError("Unable to connection to RabbitMQ")


# Publish a message to the queue and close connection
def publish(
        connection,
        body,
        queue,
        exchange,
):
    # todo error handling as above?

    channel = connection.channel()

    channel.basic_publish(exchange=exchange, routing_key=queue, body=body)

    # close connection
    if connection.is_open:
        connection.close()

