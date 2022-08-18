import requests
import re
import json
import logging

logger = logging.getLogger("tiingobot_logger")


def process_results(results):
    logger.info(f'Got {len(results)} results')
    winning_numbers = ""
    drawing = json.loads(results)
    results = drawing['Drawing']
    for k, v in results.items():
        if k == "PlayDate":
            logger.info(f'Results for date: {v}')
            winning_numbers = f"Winning Numbers for {v.split('T')[0]}:\n".format(v)
        if 'N' in k:
            winning_numbers += str(v) + " - "
        if k == "MBall":
            winning_numbers += f"Megaball - {v}".format(v)
    logging.info(f"Constructed winning_numbers string: {winning_numbers.split(':')[0]}")
    return winning_numbers


def make_web_request() -> tuple[str, int]:
    try:
        r = requests.get('https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData')
        status = r.status_code
        r.raise_for_status()
        logging.info('Successfully connected to endpoint')
    except Exception as e:
        logger.error(f"Failed to connect to megamillions endpoint. Reason: {e}")
        return e, status
    return r, status


def parse_results(results):
    # The endpoint returns a json string inside xml ?????
    # I hate that, so I just regex it out
    parsed_results = re.findall(r'{.*}', results.text)
    return parsed_results[0]


def get_megamillions():
    r, status = make_web_request()
    if status == 200:
        parsed_results = parse_results(r)
    else:
        return r

    processed_results = process_results(parsed_results)
    return processed_results
