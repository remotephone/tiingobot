import requests
import re
import json
import logging

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


def process_results(results):
    logger.info(f'Got {len(results)} results')
    for result in results:
        winning_numbers = ""
        drawing = json.loads(result)
        results = drawing['Drawing']
        for k,v in results.items():
            if k == "PlayDate":
                logger.info(f'Results for date: {v}')
                winning_numbers = f"Winning Numbers for {v.split('T')[0]}:\n".format(v)
            if 'N' in k:
                winning_numbers += str(v) + " - "
            if k == "MBall":
                winning_numbers += f"Megaball - {v}".format(v)
    logging.info(f"Constructed winning_numbers string: {winning_numbers.split(':')[0]}")
    return winning_numbers

def get_megamillions():
    try:
        r = requests.get('https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData')
    except Exception as e:
        logger.error(f"Failed to connect to megamillions endpoint. Reason: {e}")
    results = re.findall(r'{.*}', r.text)
    return process_results(results)
