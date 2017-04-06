from unittest import mock

import requests


def return_my_ip():
    response = requests.get('https://httpbin.org/ip')
    return response.json()['origin']


def test_return_my_ip():
    mock_get_request = mock.MagicMock()
    with mock.patch('requests.get', new=mock_get_request):
        ip = return_my_ip()

    mock_get_request.assert_called_once_with('https://httpbin.org/ip')
    mock_response = mock_get_request.return_value
    mock_response.json.assert_called_once_with()
    obj = mock_response.json.return_value
    obj.__getitem__.assert_called_once_with('origin')
    assert obj.__getitem__.return_value == ip