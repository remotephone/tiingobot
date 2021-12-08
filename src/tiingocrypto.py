import json
import logging
import os
import re
from datetime import datetime, timedelta

import requests
from dateutil import tz
from dateutil.parser import parse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fhandler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
fhandler.setLevel(logging.ERROR)
fhandler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
shandler = logging.StreamHandler()
shandler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(fhandler)
logger.addHandler(shandler)


def validate_stonk(crypto):
    if re.search(r"^[A-Za-z0-9][\S]{0,15}$", crypto):
        logger.info(f"validated {crypto}")
        return crypto
    else:
        logger.info(f"Failed to validate {str(crypto)}")
        return "btcusd"


def is_new(time):
    """Had the logic backwards here at first. If the test passes and the dates for the
    quote and now are less than 3 days apart, assume the crypto is currently listed and
    keep it in the list by returning true. Otherwise return false and remove it.
    Also had to switch to dateutil.parser.parse because occassionally the timestamps
    come back in a format that python doesnt recognize as iso and it throws an error.
    Logging that now so I can troubleshoot it better and just returning True since it
    only seems to do that with timestamps during trading hours, otherwise Tiingo
    truncates the milliseconds to an iso compatible length"""
    try:
        if time != None:
            dtobj = parse(time)
            tz_info = dtobj.tzinfo
            if (datetime.now(tz_info) - dtobj) < timedelta(days=3):
                return True
            else:
                return False
        else:
            return False    
    except Exception as e:
        logger.error(f"testing time: {str(time)}, exception: {e}")
        return True

def timezoner(stamp):
    return parse(stamp).astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z")

def get_crypto(crypto):
    """ return a crypto quote, cleaned up """
    TOKEN = os.environ["TIINGO_TOKEN"]
    validcrypto = validate_stonk(crypto)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(
            f"https://api.tiingo.com/tiingo/crypto/top?tickers={validcrypto}&token={TOKEN}",
            headers=headers,
        )
        validcrypto = response.json()
    except Exception as e:
        logger.error(f"Failed to connect to tiingo api. Reason: {e}")
        validcrypto = []
    # This returns a list of dictionaries with each item a crypto
    # [{'askPrice': None, 'ticker': 'AAPL', 'mid': None, 'quoteTimestamp': '2021-03-15T20:00:00+00:00', 'timestamp': '2021-03-15T20:00:00+00:00', 'askSize': None, 'open': 121.41, 'prevClose': 121.03, 'tngoLast': 123.99, 'bidSize': None, 'lastSaleTimestamp': '2021-03-15T20:00:00+00:00', 'volume': 92590555, 'bidPrice': None, 'low': 120.42, 'lastSize': None, 'high': 124.0, 'last': 123.99}]

    clean_crypto = {}

    if validcrypto == []:
        clean_crypto["Result"] = "Not Found, use a good ticker"
        logger.info(f"ticker failed to return any results for {str(crypto)}")
    else:
        clean_crypto["Ticker"] = validcrypto[0]["ticker"]
        clean_crypto["Quote Timestamp"] = timezoner(validcrypto[0]["topOfBookData"][0]["quoteTimestamp"])
        clean_crypto["Most Recent Price"] = validcrypto[0]["topOfBookData"][0]["lastPrice"]
        clean_crypto["Exchange Reporting"] = validcrypto[0]["topOfBookData"][0]["lastExchange"]

    return clean_crypto
