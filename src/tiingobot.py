import logging
import os

import discord
from discord.ext import commands

from lottery import get_megamillions, get_powerball
from randoms import (
    get_artificial_intelligence,
    get_artificial_intelligence_v2,
    get_tax_refund,
)
from tiingoapi import (
    get_stankest,
    get_stocks,
    get_stonkest,
    get_stocks_monthly,
    get_stocks_weekly,
)
from tiingocrypto import get_crypto
from sparkle import give_sparkle, get_leaderboard


logger = logging.getLogger("tiingobot_logger")
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
shandler.setLevel(logging.INFO)
logger.addHandler(fhandler)
logger.addHandler(shandler)

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents(messages=True, guilds=True, message_content=True)
bot = discord.ext.commands.Bot(intents=intents, command_prefix="!")


@bot.event
async def on_ready():
    logger.info("tiingobot has connected to Discord!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"This command is on a {int(error.retry_after)} second cooldown, please wait"
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
!stonks <ticker> - gimme a ticker, I'll look it up. no funny business
!stonk_week <ticker> - gimme a ticker, I'll tell you how it did over the last week. no funny business
!crypto <ticker> - gimme a ticker, I'll look it up. no funny business
!stonkest - gimme the stonkingest stonks of the day (most positive % change)
!stankest - gimme the stankingest stonks of the day (most negative % change)
(These last two omit stocks worth less than $1)
See https://api.tiingo.com/documentation for tiingo API docs"""
    logger.info(f"{ctx.message.author} requested help")
    await ctx.send(helpmsg)


@bot.command(
    name="stonks", help="Return stock message, defaults to GME if trickery is afoot"
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonks(
    ctx,
    stock: str = commands.parameter(
        default="GME",
        description="A stock ticker, don't try any trickery",
    ),
):
    logger.info(f"{ctx.message.author} requested stock {stock}")
    if stock.lower() == "greg":
        await ctx.send("I love you Greg, please don't try to hurt me.")
        return
    else:
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
async def crypto(
    ctx,
    crypto: str = commands.parameter(
        default="BTCUSD",
        description="A cryuto currency token ticker, don't try any trickery",
    ),
):
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
    aliases=["stonks_week", "stonk_weekly", "stonks_weekly", "weekly"],
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonk_week(
    ctx,
    stock: str = commands.parameter(
        default="GME",
        description="A stock ticker, don't try any trickery",
    ),
):
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
    name="stonk_month",
    help="Returns a result of stonk over a month, defaults to GME if trickery is afoot",
    aliases=["stonks_month", "stonk_monthly", "stonks_monthly", "monthly"],
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonk_month(
    ctx,
    stock: str = commands.parameter(
        default="GME",
        description="A stock ticker, don't try any trickery",
    ),
):
    logger.info(f"{ctx.message.author} requested stock {stock}")
    try:
        ticker = get_stocks_monthly(stock)
        ticker_response = "Performance over month:\n"
        logger.info(f"processing - {ticker_response}")
        for k, v in ticker.items():
            ticker_response += k + ": " + str(v) + "\n"
        logger.info(f"{ctx.message.author} got info on {stock}")
        await ctx.send(ticker_response)
    except Exception as e:
        logger.error(f"Something broke - {e}")
        await ctx.send("Something broke :(")


@bot.command(name="megamillions", help="Get latest megamillions numbers")
@commands.cooldown(1, 10, commands.BucketType.user)
async def megamillions(ctx):
    logger.info(f"{ctx.message.author} requested megamillions data")
    try:
        results = get_megamillions()
        logger.info(f"got {results}")
    except Exception as e:
        logger.error(f"no picks for you - {e}")
    logger.info(f"{ctx.message.author} got results {results.split(':')[0]}")
    await ctx.send(results)


@bot.command(name="powerball", help="Get latest powerball numbers")
@commands.cooldown(1, 10, commands.BucketType.user)
async def powerball(ctx):
    logger.info(f"{ctx.message.author} requested powerball data")
    try:
        results = get_powerball()
        logger.info(f"got {results}")
    except Exception as e:
        logger.error(f"no picks for you - {e}")
    logger.info(f"{ctx.message.author} got results {results.split(':')[0]}")
    await ctx.send(results)


@bot.command(name="sparkle", help="Sparkle a chat member")
@commands.cooldown(1, 10, commands.BucketType.user)
async def sparkle(ctx):
    receiver = (
        ctx.message.mentions[0].name + "#" + ctx.message.mentions[0].discriminator
    )
    logger.info(f"{ctx.message.author} sparkled {receiver}")
    sparkle_response = give_sparkle(ctx.message.author, receiver)
    sparkle_response = (
        f"@{ctx.message.author} sparkled @{receiver}.\n  {sparkle_response}"
    )
    logger.info(sparkle_response)
    await ctx.send(sparkle_response)


@bot.command(name="sparkle_leaderboard", help="See the top 3 sparklers")
@commands.cooldown(1, 10, commands.BucketType.user)
async def sparkle_leaderboard(ctx):
    logger.info(f"{ctx.message.author} requested the leaderboard")
    try:
        sparkle_response = get_leaderboard()
        logger.info("Got sparkle_response, posting to discord")
    except Exception as e:
        logger.error(f"something happened - {e}")
    await ctx.send(sparkle_response)


@bot.command(
    name="whats_my_refund",
    help="Provide your social security number and estimate your tax refund",
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def tax_refund(
    ctx,
    ssn: str = commands.parameter(
        default=None,
        description="Your real social security number, please do not use a fake",
    ),
):
    logger.info(f"{ctx.message.author} requested their tax refund")
    try:
        sparkle_response = get_tax_refund(ssn)
        logger.info("successfully returned tax refund")
    except Exception as e:
        logger.error(f"something happened - {e}")
    await ctx.send(sparkle_response)


@bot.command(
    name="ai",
    help="Tap into the unlimited power of AI to generate brilliant insight and advice",
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def ai(ctx):
    logger.info(f"{ctx.message.author} requested artificial intelligence")
    try:
        ai_response = get_artificial_intelligence()
        logger.info("successfully got AI")
    except Exception as e:
        logger.error(f"something happened - {e}")
    await ctx.send(ai_response)


@bot.command(
    name="aiv2",
    help="Ask ChatGPT something, surround your message in double quotes. Rate limited to 3x per minute total",
)
@commands.cooldown(3, 60)
async def new_issue(ctx, *, arg):
    try:
        # parse the arguements
        response = get_artificial_intelligence_v2(arg)
        logger.info(f"Bot response: {response}")
        # send the results of the github issue creation to the channel
        await ctx.send(f"{response}")
    except KeyError as e:
        logger.warning(f"KeyError: {e}")
        await ctx.send(f"KeyError: {e}")


bot.run(TOKEN)
