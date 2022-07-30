import logging
import os

import discord
from discord.ext import commands

from lottery import megamillions
from tiingoapi import get_stankest, get_stocks, get_stonkest, get_stocks_weekly, get_wigglers, put_wigglers
from tiingocrypto import get_crypto

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fhandler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
fhandler.setFormatter(
    logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: {%(pathname)s:%(lineno)d}: %(message)s"
    )
)
fhandler.setLevel(logging.ERROR)
shandler = logging.StreamHandler()
shandler.setFormatter(
    logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: {%(pathname)s:%(lineno)d}: %(message)s"
    )
)
logger.addHandler(fhandler)
logger.addHandler(shandler)

TOKEN = os.getenv("DISCORD_TOKEN")
bot = discord.ext.commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    logger.info("tiingobot has connected to Discord!")


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(
            ctx.message.channel,
            content=f"This command is on a {error.retry_after} cooldown",
        )
    logger.info(
        error
    )  # re-raise the error so all the errors will still show up in console


@bot.command(name="stonkshelp", help="return help", pass_context=True)
async def stonkshelp(ctx):
    helpmsg = """Gimme a stonk ticker, I only accept 4 character symbols. 
10 second cooldown enforced, and no funny business.
Supported commands:
!stonkshelp - you're looking at it
!stonks <ticker> - gimme a ticker, I'll look it up. no funny business - https://api.tiingo.com/documentation/iex
!stonk_week <ticker> - gimme a ticker, I'll tell you how it did over the last week. no funny business - https://api.tiingo.com/documentation/iex
!crypto <ticker> - gimme a ticker, I'll look it up. no funny business - https://api.tiingo.com/documentation/crypto
!stonkest - gimme the stonkingest stonks of the day (most positive % change)
!stankest - gimme the stankingest stonks of the day (most negative % change)
    (These last two omit stocks worth less than $1)"""
    logger.info(f"{ctx.message.author} requested help")
    await ctx.send(helpmsg)


@bot.command(
    name="stonks", help="Return stock message, defaults to GME if trickery is afoot"
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonks(ctx, stock: str):
    logger.info(f"{ctx.message.author} requested stock {stock}")
    ticker = get_stocks(stock)
    ticker_response = ""
    for k, v in ticker.items():
        ticker_response += k + ": " + str(v) + "\n"
    logger.info(f"{ctx.message.author} got info on {stock}")
    await ctx.send(ticker_response)


@bot.command(
    name="crypto", help="Return crypto message, defaults to btcusd if trickery is afoot"
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def crypto(ctx, crypto: str):
    logger.info(f"{ctx.message.author} requested crypto {crypto}")
    ticker = get_crypto(crypto)
    ticker_response = ""
    for k, v in ticker.items():
        ticker_response += k + ": " + str(v) + "\n"
    logger.info(f"{ctx.message.author} got info on {crypto}")
    await ctx.send(ticker_response)


@bot.command(name="stonkest", help="Return top 5 most performant stocks by percent")
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonkest(ctx):
    try:
        logger.info(f"{ctx.message.author} requested stonkest.")
        stonkest = get_stonkest()
        logger.info(
            f"{ctx.message.author} requested stonkest. {len(stonkest)} results returned"
        )
        if len(stonkest) == 0:
            logger.info(f"{ctx.message.author} requested stonkest. No results returned")
            await ctx.send("Something went wrong")
        stonkest_response = ""
        tickers = []
        for stonk in stonkest:
            stonkest_response += "**{}** - :rocket::rocket::rocket: {} up\n".format(
                stonk["Ticker"], stonk["\U0001F680"]
            )
            for k, v in stonk.items():
                if k == "Ticker":
                    tickers.append(v)
        logger.info(
            f"{ctx.message.author} requested stonkest. returned tickers: {tickers}"
        )
    except Exception as e:
        logger.error(e)
    await ctx.send(stonkest_response)


@bot.command(name="stankest", help="Return bottom 5 most performant stocks by percent")
@commands.cooldown(1, 10, commands.BucketType.user)
async def stankest(ctx):
    try:
        logger.info(f"{ctx.message.author} requested stankest.")
        stankest = get_stankest()
        logger.info(
            f"{ctx.message.author} requested stankest. {len(stankest)} results returned"
        )
        if len(stankest) == 0:
            logger.info(f"{ctx.message.author} requested stankest. No results returned")
            await ctx.send("Something went wrong")
        stankest_response = ""
        tickers = []
        for stonk in stankest:
            stankest_response += "**{}** - :boom::boom::boom: {} down\n".format(
                stonk["Ticker"], stonk["\U0001F4A5"]
            )
            for k, v in stonk.items():
                if k == "Ticker":
                    tickers.append(v)
    except Exception as e:
        logger.error(e)
    logger.info(f"{ctx.message.author} requested stankest. returned tickers: {tickers}")
    await ctx.send(stankest_response)


@bot.command(
    name="stonk_week",
    help="Returns a result of stonk over a week, defaults to GME if trickery is afoot",
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonk_week(ctx, stock: str):
    logger.info(f"{ctx.message.author} requested stock {stock}")
    try:
        ticker = get_stocks_weekly(stock)
        ticker_response = "Performance over week:\n"
        logger.info(f"processing - {ticker_response}")
        for k, v in ticker.items():
            ticker_response += k + ": " + str(v) + "\n"
        logger.info(f"{ctx.message.author} got info on {stock}")
        await ctx.send(ticker_response)
    except Exception as e:
        logger.error(f"Something broke - {e}")
        await ctx.send("Something broke :(")


@bot.command(
    name="megamillions", help="Get latest megamillions numbers"
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def megamillions(ctx, stock: str):
    logger.info(f"{ctx.message.author} requested megamillions data")
    results = megamillions()
    logger.info(f"{ctx.message.author} got results {results}")
    await ctx.send(results)



bot.run(TOKEN)
