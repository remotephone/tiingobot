from tiingoapi import get_meme_stocks, validate_stonk


def test_get_meme_stocks():
    assert isinstance(get_meme_stocks(), list) 
    assert isinstance(get_meme_stocks()[0], str)
    assert len(get_meme_stocks()) > 3


def test_validate_stonk():
    # valid_stocks.txt from https://github.com/DrakeDavis/RedditApiStockParser/blob/499fd3a6392a72200d682d69496393906d661427/curated_stock_tickers.txt
    with open('tests/valid_stocks.txt', 'r') as f:
        data = f.readlines()
    for d in data:
        assert validate_stonk(d) == d
