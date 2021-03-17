import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from tiingoapi import get_stocks

logging.basicConfig(filename='tiingo.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = discord.ext.commands.Bot(command_prefix = "!")

@bot.event
async def on_ready():
    logging.info(f'tiingobot has connected to Discord!')


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel, content='This command is on a %.2fs cooldown' % error.retry_after)
    logging.info(error)  # re-raise the error so all the errors will still show up in console


@bot.command(name='stonkshelp', help='return help')
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonks(ctx):
    helpmsg = "Gimme a stonk ticker, I only accept 4 character symbols. Cooldown enforced, no funny business."
    await ctx.send(helpmsg)


@bot.command(name='stonks', help='Return stock message, defaults to GME if trickery is afoot')
@commands.cooldown(1, 10, commands.BucketType.user)
async def stonks(ctx, stock: str):
    ticker = get_stocks(stock)
    ticker_response = ""
    for k, v in ticker.items():
        ticker_response += k + ": " + str(v) + "\n"
    await ctx.send(ticker_response)

bot.run(TOKEN)