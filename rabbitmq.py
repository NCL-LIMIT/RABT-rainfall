import pika

def create(rabbit_connection_string):
    parameters = pika.URLParameters(rabbit_connection_string)
    connection = pika.BlockingConnection(parameters)

    return connection.channel()

def publish(
        channel,
        body,
        queue,
        exchange,
):
    channel.basic_publish(routing_key=queue, exchange=exchange, body=body)

def subscribe(
        channel,
        handler,
        queue,
        durable,
        exchange,
        prefetch_count
):
    channel.queue_declare(queue=queue, durable=durable)
    channel.queue_bind(queue=queue, exchange=exchange)
    channel.basic_qos(prefetch_count=prefetch_count)
    channel.basic_consume(queue=queue, on_message_callback=handler)
