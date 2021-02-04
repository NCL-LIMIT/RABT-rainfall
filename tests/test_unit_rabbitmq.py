import pytest
from rainfall.handleAPIResponse import getResponse
import rabbitmqConnection
from unittest.mock import Mock, patch, MagicMock
from tests.mocks import pika


# To run only unit tests, run pytest -m unit, else run pytest to run all tests
# Unit tests using mock pika to mock the connection with RabbitMQ



@pytest.mark.unit
def test_channel_sets_parameters(monkeypatch):
    mocked_pika = Mock()
    mocked_pika.URLParameters.return_value = 'testChannel'
    monkeypatch.setattr('rabbitmqConnection.pika', mocked_pika)

    rabbitmqConnection.create('testChannel host', 1)

    mocked_pika.URLParameters.assert_called_once_with('testChannel host')


@pytest.mark.unit
def test_create_calls_connection(monkeypatch):
    mocked_pika = Mock()
    mocked_pika.URLParameters.return_value = 'testChannel'
    mocked_pika.BlockingConnection.return_value = pika.Connection()
    monkeypatch.setattr('rabbitmqConnection.pika', mocked_pika)

    rabbitmqConnection.create('testChannel host', 1)

    mocked_pika.BlockingConnection.assert_called_once_with('testChannel')


@pytest.mark.unit
def test_sender_publishes_new_message():
    channel = pika.Channel()
    channel.basic_publish = Mock()
    mocked_pika = Mock()
    mocked_pika.BlockingConnection.return_value = pika.Connection()

    rabbitmqConnection.publish(pika.Connection(), channel, 'testMessage', 'testQueue', 'testExchange')

    channel.basic_publish.assert_called_once_with(
        routing_key='testQueue',
        exchange='testExchange',
        body='testMessage'
    )


@pytest.mark.unit
@patch('pika.URLParameters')
def test_exception_thrown_when_rabbit_down(pika_mock):
    pika_mock = Mock()
    pika_mock.URLParameters.return_value = 'testHost'
    pika_mock.BlockingConnection.side_effect = pika.exceptions.AMQPConnectionError

    with pytest.raises(Exception):
        rabbitmqConnection.create('testHost', 1)

# https://medium.com/@odelucca/recommendation-algorithm-using-python-and-rabbitmq-part-2-connecting-with-rabbitmq-aa0ec933e195
# https://alexmarandon.com/articles/python_mock_gotchas/
# https://realpython.com/python-mock-library/
#https://medium.com/@yasufumy/python-mock-basics-674c33de1ced




@pytest.mark.unit
@patch('rainfall.handleAPIResponse.requests.get', autospec=True)
def test_response_sample_function(mock_get):
    url = 'https://example.com/sample.txt'
    mock_get.return_value.status_code = 204

    assert getResponse(url).status_code == 204

    # test requests.get actually gets called
    mock_get.assert_called_once_with(url)


# @pytest.mark.unit
# @patch('rainfall.handleAPIResponse.requests.get', autospec=True)
# def test_correct_queue_sent_on_non_200_response(mock_get):


# https://docs.pytest.org/en/stable/pythonpath.html 


