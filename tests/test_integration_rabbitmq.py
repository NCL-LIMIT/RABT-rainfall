# import pytest
# import rabbitmqConnection
# from time import sleep
#
#
# # todo env var for rabbitMQ host
#
#
# # Remove test exchange and queue after tests are complete
# def teardown_module(module):
#     print('teardown')
#     channel = rabbitmqConnection.create('amqp://guest:guest@localhost:5672/%2F')
#     channel.queue_delete(queue='testQueue')
#     channel.exchange_delete(exchange='testExchange')
#
#
# # Add listener inside of a channel
# def setup_listener(
#         channel,
#         on_message_callback,
#         queue='testQueue',
#         exchange='testExchange',
#         durable=False,
#         prefetch_count=1
# ):
#     channel.exchange_declare(exchange='testExchange',
#                              exchange_type='direct')
#     channel.queue_declare(queue=queue, durable=durable)
#     channel.queue_bind(queue=queue, exchange=exchange)
#     channel.basic_qos(prefetch_count=prefetch_count)
#     channel.basic_consume(queue=queue, on_message_callback=on_message_callback)
#
#     return channel
#
#
# # Check after 60s, 5 tries, to see if the listener has been called as RabbitMQ can take some time to reply.
# def wait_for_result(
#         channel,
#         anchor,
#         expected,
#         tries=0,
#         retry_after=.6
# ):
#     if anchor == expected or tries > 5:
#         assert anchor == expected
#     else:
#         sleep(retry_after)
#         return wait_for_result(channel, anchor, expected, tries + 1)
#
#
#
# # Create a new channel and test to see if we can send and receive a message in it
# @pytest.mark.integration
# def test_rabbitmq_send_message():
#     # Should be able to send a message in a given queue
#     calls = []
#     expected = ['testMessage']
#     rabbitmq_channel = rabbitmqConnection.create('amqp://guest:guest@localhost:5672/%2F')
#
#     # Handle response from server, ch=channel that received message, body=message in bytes
#     def mocked_handler(ch, method, props, body):
#         calls.append(body.decode('utf-8'))
#         ch.basic_ack(delivery_tag=method.delivery_tag)
#         ch.close()
#
#     # Send message and check that listener receives it
#     rabbitmq_channel = setup_listener(rabbitmq_channel, mocked_handler)
#     rabbitmqConnection.publish(rabbitmq_channel, 'testMessage', 'testQueue', 'testExchange')
#
#     rabbitmq_channel.start_consuming()
#     wait_for_result(rabbitmq_channel, calls, expected)
#
#
# # Test full processRainfall method by mocking a 200 and non 200 response from the API
#
# #  https://changhsinlee.com/pytest-mock/
