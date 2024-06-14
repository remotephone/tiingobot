import os

import pytest
import requests
from tiingocrypto import get_crypto


def test_get_crypto(mocker):
    mocker.patch.dict(os.environ, {"TIINGO_TOKEN": "test_token"})
    mock_response = [
        {
            "ticker": "BTC",
            "topOfBookData": [
                {
                    "quoteTimestamp": "2021-03-15T20:00:00+00:00",
                    "lastPrice": 60000.0,
                    "lastExchange": "Coinbase",
                }
            ],
        }
    ]
    mocker.patch.object(
        requests, "get", return_value=mocker.Mock(json=lambda: mock_response)
    )
    assert get_crypto("btcusd") == {
        "Ticker": "BTC",
        "Quote Timestamp": "2021-03-15 20:00 UTC",
        "Most Recent Price": 60000.0,
        "Exchange Reporting": "Coinbase",
    }


def test_get_crypto_invalid(mocker):
    mocker.patch.dict(os.environ, {"TIINGO_TOKEN": "test_token"})
    mock_response = []
    mocker.patch.object(
        requests, "get", return_value=mocker.Mock(json=lambda: mock_response)
    )
    assert get_crypto("invalidticker") == {"Result": "Not found. Use a valid ticker."}
    assert get_crypto(None) == {"Result": "Not found. Use a valid ticker."}
