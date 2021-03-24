import json
import os
import re
from datetime import datetime, timedelta

import requests


def validate_stonk(stock):
    print(stock)
    if re.search(r'^[A-Za-z][\S]{0,4}$', stock):
        return stock
    else:
        return "gme"

def is_new(time):
    dtobj = datetime.fromisoformat(time)
    tz_info = dtobj.tzinfo
    if (datetime.now(tz_info) - dtobj) > timedelta(days=1): 
        return False
    else:
        return True

def get_stocks(stock):
    TOKEN = os.environ['TIINGO_TOKEN']
    stock = validate_stonk(stock)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(f"https://api.tiingo.com/iex/?tickers={stock}&token={TOKEN}", headers=headers)
    # This returns a list of dictionaries with each item a stock
    # [{'askPrice': None, 'ticker': 'AAPL', 'mid': None, 'quoteTimestamp': '2021-03-15T20:00:00+00:00', 'timestamp': '2021-03-15T20:00:00+00:00', 'askSize': None, 'open': 121.41, 'prevClose': 121.03, 'tngoLast': 123.99, 'bidSize': None, 'lastSaleTimestamp': '2021-03-15T20:00:00+00:00', 'volume': 92590555, 'bidPrice': None, 'low': 120.42, 'lastSize': None, 'high': 124.0, 'last': 123.99}]
    stock = response.json()

    clean_stock = {}

    if stock == []:
        clean_stock['Result'] =  "Not Found, use a good ticker"
    else:
        clean_stock['Ticker'] = stock[0]['ticker']
        clean_stock['Quote Timestamp'] = stock[0]['quoteTimestamp']
        clean_stock['Most Recent Price'] = stock[0]['last']
        clean_stock['Open'] = stock[0]['open']
        clean_stock['High'] = stock[0]['high']
        clean_stock['Low'] = stock[0]['low']
        clean_stock['% Change'] = f"{round(((stock[0]['last'] - stock[0]['open']) / stock[0]['open']) * 100, 2)}%" 
        if stock[0]['last'] > stock[0]['open']:
            clean_stock['Mood'] = "\U0001F4C8"
        elif stock[0]['last'] < stock[0]['open']:
            clean_stock['Mood'] = "\U0001F4C9"

    return clean_stock

def get_em_all():
    TOKEN = os.environ['TIINGO_TOKEN']

    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.get(f"https://api.tiingo.com/iex/?token={TOKEN}", headers=headers)
    stocks = response.json()
    return stocks

def get_stonkest():
    stocks = get_em_all()

    clean_stocks = []

    for stock in stocks:
        clean_stock = {}
        clean_stock['Ticker'] = stock['ticker']
        clean_stock['Quote Timestamp'] = stock['quoteTimestamp']
        clean_stock['Most Recent Price'] = stock['last']
        clean_stock['Open'] = stock['open']
        clean_stock['\U0001F680'] = round(((float(stock['last']) - float(stock['open'])) / float(stock['open'])) * 100, 2) 
        clean_stocks.append(clean_stock)

    no_oldies = [clean_stock for clean_stock in clean_stocks if (is_new(clean_stock['Quote Timestamp']))] 
    no_pennies = [clean_stock for clean_stock in no_oldies if (clean_stock['Most Recent Price'] > 1.0)] 
    stonkest = sorted(no_pennies, key = lambda x: x['\U0001F680'])

    for stonk in stonkest:
        stonk['\U0001F680'] = "{}% up up up".format(str(stonk['\U0001F680']))

    return stonkest[-5:]


def get_stankest():
    stocks = get_em_all()

    clean_stocks = []

    for stock in stocks:
        clean_stock = {}
        clean_stock['Ticker'] = stock['ticker']
        clean_stock['Quote Timestamp'] = stock['quoteTimestamp']
        clean_stock['Most Recent Price'] = stock['last']
        clean_stock['Open'] = stock['open']
        clean_stock['\U0001F4A5'] = round(((float(stock['last']) - float(stock['open'])) / float(stock['open'])) * 100, 2) 
        clean_stocks.append(clean_stock)

    no_oldies = [clean_stock for clean_stock in clean_stocks if (is_new(clean_stock['Quote Timestamp']))] 
    no_pennies = [clean_stock for clean_stock in no_oldies if (clean_stock['Most Recent Price'] > 1.0)] 
    stankest = sorted(no_pennies, key = lambda x: x['\U0001F4A5'], reverse=True)

    for stonk in stankest:
        stonk['\U0001F4A5'] = "{}% down down down".format(str(stonk['\U0001F4A5']))

    return stankest[-5:]
