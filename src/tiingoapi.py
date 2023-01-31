import logging
import os
import re
from datetime import datetime, timedelta

import requests
from dateutil import tz
from dateutil.parser import parse

logger = logging.getLogger("tiingobot_logger")


def validate_stonk(stock):
    if re.search(r"^[A-Za-z][\S]{0,4}$", stock):
        logger.info(f"validated {stock}")
        return stock
    else:
        logger.info(f"Failed to validate {str(stock)}")
        return "gme"


def is_new(time):
    """Had the logic backwards here at first. If the test passes and the dates for the
    quote and now are less than 3 days apart, assume the stock is currently listed and
    keep it in the list by returning true. Otherwise return false and remove it.
    Also had to switch to dateutil.parser.parse because occassionally the timestamps
    come back in a format that python doesnt recognize as iso and it throws an error.
    Logging that now so I can troubleshoot it better and just returning True since it
    only seems to do that with timestamps during trading hours, otherwise Tiingo
    truncates the milliseconds to an iso compatible length"""
    try:
        if time is not None:
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


def get_stocks(stock):
    """return a stock quote, cleaned up"""
    TOKEN = os.environ["TIINGO_TOKEN"]
    validstock = validate_stonk(stock)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(
            f"https://api.tiingo.com/iex/?tickers={validstock}&token={TOKEN}",
            headers=headers,
        )
        validstock = response.json()
    except Exception as e:
        logger.error(f"Failed to connect to tiingo api. Reason: {e}")
        validstock = []
    # This returns a list of dictionaries with each item a stock
    # [{'askPrice': None, 'ticker': 'AAPL', 'mid': None, 'quoteTimestamp': '2021-03-15T20:00:00+00:00',
    # 'timestamp': '2021-03-15T20:00:00+00:00', 'askSize': None, 'open': 121.41, 'prevClose': 121.03,
    # 'tngoLast': 123.99, 'bidSize': None, 'lastSaleTimestamp': '2021-03-15T20:00:00+00:00',
    # 'volume': 92590555, 'bidPrice': None, 'low': 120.42, 'lastSize': None, 'high': 124.0, 'last': 123.99}]

    clean_stock = {}

    if validstock == []:
        clean_stock["Result"] = "Not Found, use a good ticker"
        logger.info(f"ticker failed to return any results for {str(stock)}")
    else:
        clean_stock["Ticker"] = validstock[0]["ticker"]
        clean_stock["Quote Timestamp"] = timezoner(validstock[0]["quoteTimestamp"])
        clean_stock["Most Recent Price"] = validstock[0]["last"]
        clean_stock["Last Close"] = validstock[0]["prevClose"]
        clean_stock["Open"] = validstock[0]["open"]
        clean_stock["High"] = validstock[0]["high"]
        clean_stock["Low"] = validstock[0]["low"]
        if validstock[0]["prevClose"] is not None:
            clean_stock[
                "% Change since last close"
            ] = f"{round(((validstock[0]['last'] - validstock[0]['prevClose']) / validstock[0]['prevClose']) * 100, 2)}%"
            if validstock[0]["last"] > validstock[0]["prevClose"]:
                clean_stock["Mood"] = "\U0001F4C8"
            elif validstock[0]["last"] < validstock[0]["prevClose"]:
                clean_stock["Mood"] = "\U0001F4C9"
        else:
            clean_stock[
                "% Change since open"
            ] = f"{round(((validstock[0]['last'] - validstock[0]['open']) / validstock[0]['open']) * 100, 2)}%"
            if validstock[0]["last"] > validstock[0]["open"]:
                clean_stock["Mood"] = "\U0001F4C8"
            elif validstock[0]["last"] < validstock[0]["open"]:
                clean_stock["Mood"] = "\U0001F4C9"

    return clean_stock


def get_em_all():
    """a helper function for stonkest and stankest. Get me all the stocks
    and return them as a dictionary for further processing"""
    TOKEN = os.environ["TIINGO_TOKEN"]

    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(
            f"https://api.tiingo.com/iex/?token={TOKEN}", headers=headers
        )
        stocks = response.json()
        return stocks
    except Exception as e:
        logger.error(f"Failed to get all iex results. Error: {e}")
        stocks = []
        return stocks


def get_stonkest():
    stocks = get_em_all()
    if len(stocks) == 0:
        logger.error("No stonkest returned, something went wrong")
        return None
    clean_stocks = []
    logger.info(f"cleaning {len(stocks)}")
    for stock in stocks:
        clean_stock = {}
        clean_stock["Ticker"] = stock["ticker"]
        clean_stock["Quote Timestamp"] = stock["quoteTimestamp"]
        clean_stock["Most Recent Price"] = stock["last"]
        clean_stock["Open"] = stock["open"]
        try:
            if stock["prevClose"] is not None:
                clean_stock["\U0001F680"] = round(
                    (
                        (float(stock["last"]) - float(stock["prevClose"]))
                        / float(stock["prevClose"])
                    )
                    * 100,
                    2,
                )
            else:
                clean_stock["\U0001F680"] = round(
                    (
                        (float(stock["last"]) - float(stock["open"]))
                        / float(stock["open"])
                    )
                    * 100,
                    2,
                )
        except Exception as e:
            logger.error(f"error: {e}, issues processing {stock['ticker']}")
            continue

        clean_stocks.append(clean_stock)

    logger.info(f"returned {len(clean_stocks)} clean_stocks")

    no_oldies = [
        clean_stock
        for clean_stock in clean_stocks
        if (is_new(clean_stock["Quote Timestamp"]))
    ]

    logger.info(f"returned {len(no_oldies)} current stocks")

    no_pennies = [
        clean_stock
        for clean_stock in no_oldies
        if (clean_stock["Most Recent Price"] > 1.0)
    ]
    logger.info(f"returned {len(no_pennies)} non-penny stocks")

    stonkest = sorted(no_pennies, key=lambda x: x["\U0001F680"])
    logger.info(f"sorted {len(stonkest)} stocks successfully")

    for stonk in stonkest:
        stonk["Quote Timestamp"] = timezoner(stonk["Quote Timestamp"])
        stonk["\U0001F680"] = "{}% ".format(str(stonk["\U0001F680"]))
    logger.info("added emojis successfully")

    return stonkest[-5:]


def get_stankest():
    stocks = get_em_all()
    if len(stocks) == 0:
        logger.error("No stankest returned, something went wrong")
        return None
    logger.info(f"cleaning {len(stocks)}")

    clean_stocks = []

    for stock in stocks:
        clean_stock = {}
        clean_stock["Ticker"] = stock["ticker"]
        clean_stock["Quote Timestamp"] = stock["quoteTimestamp"]
        clean_stock["Most Recent Price"] = stock["last"]
        clean_stock["Open"] = stock["open"]
        try:
            if stock["prevClose"] is not None:
                clean_stock["\U0001F4A5"] = round(
                    (
                        (float(stock["last"]) - float(stock["prevClose"]))
                        / float(stock["prevClose"])
                    )
                    * 100,
                    2,
                )
            else:
                clean_stock["\U0001F4A5"] = round(
                    (
                        (float(stock["last"]) - float(stock["open"]))
                        / float(stock["open"])
                    )
                    * 100,
                    2,
                )
        except Exception as e:
            logger.error(f"error: {e}, issues processing {stock['ticker']}")
            continue

        clean_stocks.append(clean_stock)

    logger.info(f"returned {len(clean_stocks)} clean_stocks")

    no_oldies = [
        clean_stock
        for clean_stock in clean_stocks
        if (is_new(clean_stock["Quote Timestamp"]))
    ]

    logger.info(f"returned {len(no_oldies)} current stocks")

    no_pennies = [
        clean_stock
        for clean_stock in no_oldies
        if (clean_stock["Most Recent Price"] > 1.0)
    ]
    logger.info(f"returned {len(no_pennies)} non-penny stocks")

    stankest = sorted(no_pennies, key=lambda x: x["\U0001F4A5"], reverse=True)
    logger.info(f"sorted {len(stankest)} stocks successfully")

    for stonk in stankest:
        stonk["Quote Timestamp"] = timezoner(stonk["Quote Timestamp"])
        stonk["\U0001F4A5"] = "{}% ".format(str(stonk["\U0001F4A5"]))
    logger.info("added emojis successfully")

    return stankest[-5:]


def get_stock_on_day(valid_stock, day):
    """return a stock quote, and the difference over the last week cleaned up"""
    TOKEN = os.environ["TIINGO_TOKEN"]
    headers = {"Content-Type": "application/json"}
    try:
        price_at_day = []
        counter = 0
        while price_at_day == [] and counter < 5:
            logger.info(f"Checking {valid_stock} on {day}")
            response = requests.get(
                f"https://api.tiingo.com/tiingo/daily/{valid_stock}/prices?startDate={day.strftime('%Y-%m-%d')}&endDate={day.strftime('%Y-%m-%d')}&token={TOKEN}",
                headers=headers,
            )
            price_at_day = response.json()
            counter += 1
            day -= timedelta(days=1)
            logger.info(
                f"price_at_day = {price_at_day}, day = {day.strftime('%Y-%m-%d')}, counter = {counter}"
            )
        logger.info(f"Got - {price_at_day} - checking details...")
    except Exception as e:
        logger.error(f"Failed to connect to tiingo api. Reason: {e}")
        price_at_day = None

    if "detail" in price_at_day:
        logger.error(f"Error requested {valid_stock} - {price_at_day['detail']}")
        price_at_day = None
    logger.info(f"Working with price_at_day = {price_at_day}")
    # This returns a list of dictionaries with each item a stock
    # [{'askPrice': None, 'ticker': 'AAPL', 'mid': None, 'quoteTimestamp': '2021-03-15T20:00:00+00:00',
    # 'timestamp': '2021-03-15T20:00:00+00:00', 'askSize': None, 'open': 121.41, 'prevClose': 121.03,
    # 'tngoLast': 123.99, 'bidSize': None, 'lastSaleTimestamp': '2021-03-15T20:00:00+00:00',
    # 'volume': 92590555, 'bidPrice': None, 'low': 120.42, 'lastSize': None, 'high': 124.0,
    # 'last': 123.99}]
    return day, price_at_day


def prev_weekday(adate):
    _offsets = (3, 0, 0, 0, 0, 0, 2)
    if adate.weekday() in [0, 1, 2, 3, 4]:
        return adate
    else:
        return adate - timedelta(days=_offsets[adate.weekday()])



def get_stocks_weekly(stock):
    """return a stock quote, and the difference over the last week cleaned up

    # This returns a list of dictionaries with an item per day
    # [
    #   {
    #     "date": "2019-01-14T00:00:00.000Z",
    #     "close": 150,
    #     "high": 151.27,
    #     "low": 149.22,
    #     "open": 150.85,
    #     "volume": 32439186,
    #     "adjClose": 36.3556620563,
    #     "adjHigh": 36.6634733284,
    #     "adjLow": 36.1666126136,
    #     "adjOpen": 36.5616774746,
    #     "adjVolume": 129756744,
    #     "divCash": 0,
    #     "splitFactor": 1
    #   }
    # ]
    """
    valid_stock = validate_stonk(stock)

    today = datetime.today()
    today = today.replace(tzinfo=None)

    try:
        currentdate = prev_weekday(today)
        day, latest_price = get_stock_on_day(valid_stock, currentdate)
        week_ago = prev_weekday(day - timedelta(days=7))
        weekagoday, week_ago_price = get_stock_on_day(valid_stock, week_ago)
        logging.info(f"Got {latest_price} and {week_ago_price}")
    except Exception as e:
        logging.error(e)
    difference = (
        (latest_price[0]["close"] - week_ago_price[0]["close"])
        / week_ago_price[0]["close"]
    ) * 100

    logger.info(f"Building response with difference {difference}...")
    clean_stock = {}

    clean_stock["Ticker"] = valid_stock
    clean_stock["Beginning of Week Date"] = weekagoday.strftime("%Y-%m-%d")
    clean_stock["Beginning of Week Price"] = week_ago_price[0]["close"]
    clean_stock["End of Week Price"] = latest_price[0]["close"]
    clean_stock["End of Week Date"] = day.strftime("%Y-%m-%d")
    clean_stock["Change over Time"] = str(difference) + "%"
    if latest_price[0]["close"] > week_ago_price[0]["close"]:
        clean_stock["Mood"] = "\U0001F4C8"
    else:
        clean_stock["Mood"] = "\U0001F4C9"
    logger.info(f"Returning result {clean_stock}...")
    return clean_stock



def get_stocks_monthly(stock):
    """return a stock quote, and the difference over the last month cleaned up

    # This returns a list of dictionaries with an item per day
    # [
    #   {
    #     "date": "2019-01-14T00:00:00.000Z",
    #     "close": 150,
    #     "high": 151.27,
    #     "low": 149.22,
    #     "open": 150.85,
    #     "volume": 32439186,
    #     "adjClose": 36.3556620563,
    #     "adjHigh": 36.6634733284,
    #     "adjLow": 36.1666126136,
    #     "adjOpen": 36.5616774746,
    #     "adjVolume": 129756744,
    #     "divCash": 0,
    #     "splitFactor": 1
    #   }
    # ]
    """
    valid_stock = validate_stonk(stock)

    today = datetime.today()
    today = today.replace(tzinfo=None)

    try:
        currentdate = prev_weekday(today)
        day, latest_price = get_stock_on_day(valid_stock, currentdate)
        month_ago = prev_weekday(day - timedelta(days=30))
        monthagoday, month_ago_price = get_stock_on_day(valid_stock, month_ago)
        logging.info(f"Got {latest_price} and {month_ago_price}")
    except Exception as e:
        logging.error(e)
    difference = (
        (latest_price[0]["close"] - month_ago_price[0]["close"])
        / month_ago_price[0]["close"]
    ) * 100

    logger.info(f"Building response with difference {difference}...")
    clean_stock = {}

    clean_stock["Ticker"] = valid_stock
    clean_stock["Beginning of month Date"] = monthagoday.strftime("%Y-%m-%d")
    clean_stock["Beginning of month Price"] = month_ago_price[0]["close"]
    clean_stock["End of month Price"] = latest_price[0]["close"]
    clean_stock["End of month Date"] = day.strftime("%Y-%m-%d")
    clean_stock["Change over Time"] = str(difference) + "%"
    if latest_price[0]["close"] > month_ago_price[0]["close"]:
        clean_stock["Mood"] = "\U0001F4C8"
    else:
        clean_stock["Mood"] = "\U0001F4C9"
    logger.info(f"Returning result {clean_stock}...")
    return clean_stock
