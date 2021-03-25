import logging
import os

import discord
from discord.ext import commands

from tiingoapi import get_stankest, get_stocks, get_stonkest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fhandler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
fhandler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
shandler = logging.StreamHandler()
shandler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(fhandler)
logger.addHandler(shandler)

bot = discord.ext.commands.Bot(command_prefix = "!")

@bot.event
async def on_ready():
    logger.info(f"tiingobot has connected to Discord!")


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


@bot.command(name="stonkshelp", help="return help")
async def stonks(ctx):
    helpmsg = """Gimme a stonk ticker, I only accept 4 character symbols. \n10 second cooldown enforced, and no funny business.\n \
        Supported commands:\n\
        !stonkshelp - you're looking at it\n\
        !stonks <ticker> - gimme a ticker, I'll look it up. no funny business\n\
        !stonkest - gimme the stonkingest stonks of the day (most positive % change)\n\
        !stankest - gimme the stankingest stonks of the day (most negative % change)\n\
            (These last two omit stocks worth less than $1)"""
    logger.info(f"{ctx.author} requested help")
    await ctx.send(helpmsg)


@bot.command(
    name="stonks", help="Return stock message, defaults to GME if trickery is afoot"
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonks(ctx, stock: str):
    ticker = get_stocks(stock)
    ticker_response = ""
    for k, v in ticker.items():
        ticker_response += k + ": " + str(v) + "\n"
    logger.info(f"{ctx.author} requested stock {stock}")
    await ctx.send(ticker_response)


@bot.command(name="stonkest", help="Return top 5 most performat stocks by percent")
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonkest(ctx):
    stonkest = get_stonkest()
    if len(stonkest) == 0:
        logger.info(f"{ctx.author} requested stankest. No results returned")
        await ctx.send("Something went wrong")
    stonkest_response = ""
    tickers = []
    for stonk in stonkest:
        for k, v in stonk.items():
            stonkest_response += k + ": " + str(v) + "\n"
            if k == "Ticker":
                tickers.append(v)
    logger.info(f"{ctx.author} requested stonkest. returned tickers: {tickers}")
    await ctx.send(stonkest_response)


@bot.command(name="stankest", help="Return bottom 5 most performat stocks by percent")
@commands.cooldown(1, 10, commands.BucketType.user)
async def stankest(ctx):
    stankest = get_stankest()
    if len(stankest) == 0:
        logger.info(f"{ctx.author} requested stankest. No results returned")
        await ctx.send("Something went wrong")
    stankest_response = ""
    for stonk in stankest:
        for k, v in stonk.items():
            stankest_response += k + ": " + str(v) + "\n"
            if k == "Ticker":
                tickers.append(v)
    logger.info(f"{ctx.author} requested stankest. returned tickers: {tickers}")
    await ctx.send(stankest_response)


bot.run(TOKEN)
