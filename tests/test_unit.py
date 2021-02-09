import json
import pytest
from processRainfall import handleResponse
from processRainfall import create
from processRainfall import publish
import processRainfall
from unittest.mock import Mock, patch
from tests.mocks import pika
from dotenv import load_dotenv
load_dotenv()

# To run only unit tests, run pytest -m unit, else run pytest to run all tests

@pytest.mark.unit
def test_channel_sets_parameters(monkeypatch):
    mocked_pika = Mock()
    mocked_pika.URLParameters.return_value = 'testChannel'
    monkeypatch.setattr('processRainfall.pika', mocked_pika)

    create('testChannel host', 1)

    mocked_pika.URLParameters.assert_called_once_with('testChannel host')


@pytest.mark.unit
def test_create_calls_connection(monkeypatch):
    mocked_pika = Mock()
    mocked_pika.URLParameters.return_value = 'testChannel'
    mocked_pika.BlockingConnection.return_value = pika.Connection()
    monkeypatch.setattr('processRainfall.pika', mocked_pika)

    create('testChannel host', 1)

    mocked_pika.BlockingConnection.assert_called_once_with('testChannel')


@pytest.mark.unit
@patch('pika.URLParameters')
def test_exception_thrown_when_rabbit_down(pika_mock):
    pika_mock = Mock()
    pika_mock.URLParameters.return_value = 'testHost'
    pika_mock.BlockingConnection.side_effect = pika.exceptions.AMQPConnectionError

    with pytest.raises(Exception):
        create('testHost', 1)

@pytest.mark.unit
@patch('processRainfall.create', autospec=True)
@patch('processRainfall.publish', autospec=True)
def test_correct_queue_used_on_non_200_response(mock_publish, mock_create_connection):
    # mock connection to rabbitMQ and API response
    connection = pika.Connection()
    mock_create_connection.return_value = connection
    response = Mock()
    response.status_code = 204

    # expected message
    json_map = {}
    json_map["error"] = "Weather API returned status 204"
    message = json.dumps(json_map)

    # call function
    handleResponse(response, 1)

    # check publish function called with correct parameters to direct message to debug queue
    processRainfall.publish.assert_called_once_with(connection,  message, 'debug.rainfall', 'rabt-debug-exchange', 'topic')

@pytest.mark.unit
@patch('processRainfall.create', autospec=True)
@patch('processRainfall.publish', autospec=True)
@patch('processRainfall.createRainfallMessage', autospec=True)
def test_correct_queue_used_on_200_response(mock_create_message, mock_publish, mock_create_connection):
    # mock connection to rabbitMQ, API response and message creation
    connection = pika.Connection()
    mock_create_connection.return_value = connection
    json_map = {}
    json_map["message"] = "Test message"
    message = json.dumps(json_map)
    mock_create_message.return_value = message
    response = Mock()
    response.status_code = 200

    # call function
    handleResponse(response, 1)

    # check publish function called with correct parameters to direct message to rainfall queue
    processRainfall.publish.assert_called_once_with(connection,  message, 'rabt-rainfall-queue', 'rabt-rainfall-exchange', 'direct')

