import re
import json
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fhandler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
fhandler.setLevel(logging.ERROR)
fhandler.setFormatter(
    logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: {%(pathname)s:%(lineno)d}: %(message)s"
    )
)
shandler = logging.StreamHandler()
shandler.setFormatter(
    logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: {%(pathname)s:%(lineno)d}: %(message)s"
    )
)
logger.addHandler(fhandler)
logger.addHandler(shandler)


def process_results(results):
    if len(results) != 1:
        logger.error('Got too many results???')
    for result in results:
        winning_numbers = ""
        drawing = json.loads(result)
        results = drawing['Drawing']
        for k,v in results.items():
            if k == "PlayDate":
                winning_numbers = f"Winning Numbers for {v.split('T')[0]}:\n".format(v)
            if 'N' in k:
                winning_numbers += str(v) + " - "
            if k == "MBall":
                winning_numbers += f"Megaball - {v}".format(v)
    return winning_numbers


async def megamillions():
    url = 'https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            r_text = await r.text
    results = re.findall(r'{.*}', r_text)
    winning_numbers = process_results(results)
    return winning_numbers

