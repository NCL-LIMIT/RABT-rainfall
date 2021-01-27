import pytest
import rabbitmq
from unittest.mock import Mock
from tests.mocks import pika


# To run only unit tests, run pytest -m unit, else run pytest to run all tests
# Unit tests using mock pika to mock the connection with RabbitMQ
@pytest.mark.unit
def test_channel_sets_parameters(monkeypatch):
    mocked_pika = Mock()
    mocked_pika.URLParameters.return_value = 'testChannel'
    monkeypatch.setattr('rabbitmq.pika', mocked_pika)

    rabbitmq.create('testChannel host')

    mocked_pika.URLParameters.assert_called_once_with('testChannel host')


@pytest.mark.unit
def test_channel_creates_connection(monkeypatch):
    mocked_pika = Mock()
    mocked_pika.URLParameters.return_value = 'testChannel'
    mocked_pika.BlockingConnection.return_value = pika.Connection()
    monkeypatch.setattr('rabbitmq.pika', mocked_pika)

    rabbitmq.create('testChannel host')

    mocked_pika.BlockingConnection.assert_called_once_with('testChannel')


@pytest.mark.unit
def test_sender_publish_new_message(monkeypatch):
    channel = pika.Channel()
    channel.basic_publish = Mock()

    rabbitmq.publish(channel, 'testMessage', 'testQueue', 'testExchange')

    channel.basic_publish.assert_called_once_with(
        routing_key='testQueue',
        exchange='testExchange',
        body='testMessage'
    )


# https://medium.com/@odelucca/recommendation-algorithm-using-python-and-rabbitmq-part-2-connecting-with-rabbitmq-aa0ec933e195
