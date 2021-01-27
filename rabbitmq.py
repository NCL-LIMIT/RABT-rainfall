import pika

# Create a channel
def create(rabbit_connection_string):
    while(True):
        parameters = pika.URLParameters(rabbit_connection_string)
        try:
            connection = pika.BlockingConnection(parameters)
            return connection.channel()

        except pika.exceptions.AMQPConnectionError:
            print("Connection error, retrying...")
            # todo how to handle not being able to create a connection



# Publish a message to the queue
def publish(
        channel,
        body,
        queue,
        exchange,
):
    while(True):
        try:
            channel.basic_publish(routing_key=queue, exchange=exchange, body=body)
        except pika.exceptions.AMQPConnectionError:
            print("Connection error, retrying...")


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
