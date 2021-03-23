import json
import re 
import os

import requests


def validate_stonk(stock):
    print(stock)
    if re.search(r'^[A-Za-z][\S]{0,4}$', stock):
        return stock
    else:
        return "gme"

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
        clean_stock['% Change'] = f"{round(((stock[0]['last'] - stock[0]['open']) / stock[0]['open']) * 100, 4)}%" 
        if stock[0]['last'] > stock[0]['open']:
            clean_stock['Mood'] = "\U0001F4C8"
        elif stock[0]['last'] < stock[0]['open']:
            clean_stock['Mood'] = "\U0001F4C9"

    return clean_stock

def get_stonkest():
    TOKEN = os.environ['TIINGO_TOKEN']

    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.get(f"https://api.tiingo.com/iex/?token={TOKEN}", headers=headers)
    stocks = response.json()

    clean_stocks = []

    for stock in stocks:
        clean_stock = {}
        clean_stock['Ticker'] = stock['ticker']
        clean_stock['Quote Timestamp'] = stock['quoteTimestamp']
        clean_stock['Most Recent Price'] = stock['last']
        clean_stock['Open'] = stock['open']
        clean_stock['High'] = stock['high']
        clean_stock['Low'] = stock['low']
        clean_stock['% Change'] = round(((float(stock['last']) - float(stock['open'])) / float(stock['open'])) * 100, 4) 
        if stock['last'] > stock['open']:
            clean_stock['Mood'] = "\U0001F4C8"
        elif stock['last'] < stock['open']:
            clean_stock['Mood'] = "\U0001F4C9"
        clean_stocks.append(clean_stock)

    no_pennies = [clean_stock for clean_stock in clean_stocks if (clean_stock['Most Recent Price'] > 0.10)] 

    stonkest = sorted(no_pennies, key = lambda x: x['% Change'])

    return stonkest[-4:]