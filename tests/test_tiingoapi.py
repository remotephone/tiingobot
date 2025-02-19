import os
from datetime import datetime, timedelta

import pytest
from dateutil import tz
from dateutil.parser import parse
from tiingoapi import get_em_all, get_meme_stocks, get_stocks, is_new, timezoner, validate_stonk


@pytest.fixture(scope="session")
def mock_tiingo_token():
    os.environ["TIINGO_TOKEN"] = "mock_token"
    yield
    del os.environ["TIINGO_TOKEN"]

@pytest.mark.live
def test_get_stocks():
    # Arrange
    stock = "AAPL"
    # Act
    result = get_stocks(stock)

    # Assert result has the expected keys
    expected_keys = [
        "Ticker",
        "Quote Timestamp",
        "Most Recent Price",
        "Last Close",
        "Open",
        "High",
        "Low",
        "% Change since last close",
        "Mood",
    ]
    for key in expected_keys:
        assert key in result

def test_get_stocks_returns_clean_stock(mocker, mock_tiingo_token):
    # Arrange
    stock = "AAPL"
    expected = {
        "Ticker": "AAPL",
        "Quote Timestamp": "2021-03-15 20:00 UTC",
        "Most Recent Price": 123.99,
        "Last Close": 121.03,
        "Open": 121.41,
        "High": 124.0,
        "Low": 120.42,
        "% Change since last close": "2.45%",
        "Mood": "\U0001F4C8",
    }
    mock_response = [
        {
            "ticker": "AAPL",
            "timestamp": "2021-03-15T20:00:00+00:00",
            "tngoLast": 123.99,
            "prevClose": 121.03,
            "open": 121.41,
            "high": 124.0,
            "low": 120.42,
        }
    ]
    mocker.patch("tiingoapi.requests.get").return_value.json.return_value = mock_response

    # Act
    result = get_stocks(stock)

    # Assert
    assert result == expected


def test_get_stocks_returns_not_found(mocker, mock_tiingo_token):
    # Arrange
    stock = "INVALID"
    expected = {"Result": "Not Found, use a good ticker"}
    mocker.patch("tiingoapi.requests.get").return_value.json.return_value = []

    # Act
    result = get_stocks(stock)

    # Assert
    assert result == expected


def test_get_em_all_returns_list(mocker, mock_tiingo_token):
    # Arrange
    expected = [
        {
            "ticker": "AAPL",
            "quoteTimestamp": "2021-03-15T20:00:00+00:00",
            "last": 123.99,
            "prevClose": 121.03,
            "open": 121.41,
            "high": 124.0,
            "low": 120.42,
        }
    ]
    mocker.patch("tiingoapi.requests.get").return_value.json.return_value = expected

    # Act
    result = get_em_all()

    # Assert
    assert result == expected


def test_is_new_returns_true_for_recent_time(mocker):
    # Arrange
    time = "2022-01-01T00:00:00.000Z"
    mock_datetime = mocker.patch("tiingoapi.datetime")
    mock_datetime.now.return_value = parse("2022-01-03T00:00:00.000Z")
    expected = True

    # Act
    result = is_new(time)

    # Assert
    assert result == expected


def test_is_new_returns_false_for_old_time(mocker):
    # Arrange
    time = "2021-12-01T00:00:00.000Z"
    mock_datetime = mocker.patch("tiingoapi.datetime")
    mock_datetime.now.return_value = parse("2022-01-03T00:00:00.000Z")
    expected = False

    # Act
    result = is_new(time)

    # Assert
    assert result == expected


def test_is_new_returns_false_for_none_time(mocker):
    # Arrange
    time = None
    expected = False

    # Act
    result = is_new(time)

    # Assert
    assert result == expected


def test_is_new_returns_true_and_logs_error_for_invalid_time(mocker):
    # Arrange
    time = "invalid_time"
    expected = True
    mock_logger = mocker.patch("tiingoapi.logger")

    # Act
    result = is_new(time)

    # Assert
    assert result == expected
    mock_logger.error.assert_called_once()


def test_get_meme_stocks():
    assert isinstance(get_meme_stocks(), list)
    assert isinstance(get_meme_stocks()[0], str)
    assert len(get_meme_stocks()) > 3


def test_validate_stonk():
    # valid_stocks.txt from https://github.com/DrakeDavis/RedditApiStockParser/blob/499fd3a6392a72200d682d69496393906d661427/curated_stock_tickers.txt
    with open("tests/valid_stocks.txt", "r") as f:
        data = f.readlines()
    for d in data:
        assert validate_stonk(d) == d
