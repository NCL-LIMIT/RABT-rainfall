import time

import pika


# Create a connection
def create(rabbit_connection_string, attempt_interval):
    attempts = 0
    parameters = pika.URLParameters(rabbit_connection_string)
    print(parameters)
    while attempts < 10:
        try:
            connection = pika.BlockingConnection(parameters)
            return connection

        except pika.exceptions:
            print("Connection error, retrying. Attempt " + str(attempts))
            time.sleep(attempt_interval)
            attempts += 1

    raise ConnectionError("Unable to connection to RabbitMQ")


# Publish a message to the queue and close channel
def publish(
        connection,
        channel,
        body,
        queue,
        exchange,
):  # todo error handling?
    channel.basic_publish(routing_key=queue, exchange=exchange, body=body)
    if connection.is_open:
        connection.close()

# def subscribe(
#         channel,
#         handler,
#         queue,
#         durable,
#         exchange,
#         prefetch_count
# ):
#     channel.queue_declare(queue=queue, durable=durable)
#     channel.queue_bind(queue=queue, exchange=exchange)
#     channel.basic_qos(prefetch_count=prefetch_count)
#     channel.basic_consume(queue=queue, on_message_callback=handler)
