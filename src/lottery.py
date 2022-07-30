import requests
import re
import json

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

def megamillions():
    try:
        r = requests.get(' https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData')
        r.raise_for_status()
    except Exception as e:
        logger.error(f'Failed to connect - {e}')

    results = re.findall(r'{.*}', r.text)
    if len(results) != 1:
        logger.error('Got too many results???')
        return "Come back later"

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