import logging
import os
import re
from datetime import datetime, timedelta

import requests
from dateutil import tz
from dateutil.parser import parse

logger = logging.getLogger("tiingobot_logger")


def validate_stonk(crypto):
    """Validate a crypto ticker."""
    if crypto and re.match(r"^\w{1,16}$", crypto):
        logger.info(f"Validated {crypto}")
        return crypto
    else:
        logger.info(f"Failed to validate {crypto}")
        return "btcusd"


def is_new(time):
    """Check if a crypto quote is less than 3 days old."""
    try:
        if time is not None:
            dtobj = parse(time)
            if (datetime.now(dtobj.tzinfo) - dtobj) < timedelta(days=3):
                return True
        return False
    except Exception as e:
        logger.error(f"Error testing time: {time}. Exception: {e}")
        return True


def timezoner(stamp):
    """Convert a timestamp to local time."""
    return parse(stamp).astimezone(tz.UTC).strftime("%Y-%m-%d %H:%M %Z")


def get_crypto(crypto):
    """Return a cleaned-up crypto quote."""
    TOKEN = os.environ["TIINGO_TOKEN"]
    validcrypto = validate_stonk(crypto)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(
            f"https://api.tiingo.com/tiingo/crypto/top?tickers={validcrypto}usd&token={TOKEN}",
            headers=headers,
        )
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to connect to Tiingo API. Reason: {e}")
        return {"Result": "Error connecting to Tiingo API."}

    if not data:
        logger.info(f"No results found for {crypto}.")
        return {"Result": "Not found. Use a valid ticker."}

    return {
        "Ticker": data[0]["ticker"],
        "Quote Timestamp": timezoner(data[0]["topOfBookData"][0]["quoteTimestamp"]),
        "Most Recent Price": data[0]["topOfBookData"][0]["lastPrice"],
        "Exchange Reporting": data[0]["topOfBookData"][0]["lastExchange"],
    }
