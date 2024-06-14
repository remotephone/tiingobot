import json
import logging
import random
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import tz
from tiingologger import logger


def get_next_powerball():
    # Parse it to get the date of the next drawing (10/07/2023 in this example), the size of the jackpot ($1.40 Billion) and the cash payout ($643.7 Million)
    r = requests.get("https://www.texaslottery.com/export/sites/lottery/Games/Powerball/index.html")
    soup = BeautifulSoup(r.text, "html.parser")
    jackpot = soup.find("div", {"class": "jackpotPadding"})
    jackpot_date = jackpot.find("p").text
    # Get the date from the string and remove the :
    jackpot_date = jackpot_date.split()[-1].strip(":")
    jackpot_amount = jackpot.find("h1").text
    jackpot_cash = jackpot.find_all("p")[1].text.split(":")[1].strip()
    if jackpot_date and jackpot_amount and jackpot_cash:
        return f"Next Powerball drawing: {jackpot_date} - Jackpot: {jackpot_amount} - Cash Payout: {jackpot_cash}"
    else:
        return "Something went wrong"


def get_one_pb_number():
    return str(random.choice(range(1, 70)))


def get_pb_red():
    return str(random.choice(range(1, 27)))


def pick_my_powerball_numbers():
    numbers = []
    for i in range(1, 7):
        numbers.append(get_one_pb_number())
    return f"Your numbers are {', '.join(numbers[:-1])} - Red Powerball: {get_pb_red()}"


def process_megamillions_results(results):
    logger.info(f"Got {len(results)} results")
    winning_numbers = ""
    drawing = json.loads(results)
    results = drawing["Drawing"]
    for k, v in results.items():
        if k == "PlayDate":
            logger.info(f"Results for date: {v}")
            winning_numbers = f"Winning Numbers for {v.split('T')[0]}:\n".format(v)
        if "N" in k:
            winning_numbers += str(v) + " - "
        if k == "MBall":
            winning_numbers += f"Megaball - {v}".format(v)
    logging.info(f"Constructed winning_numbers string: {winning_numbers.split(':')[0]}")
    return winning_numbers


def make_lottery_web_request(url: str) -> tuple[str, int]:
    try:
        r = requests.get(url)
        status = r.status_code
        r.raise_for_status()
        logging.info("Successfully connected to endpoint")
    except Exception as e:
        logger.error(f"Failed to connect to lottery endpoint. Reason: {e}")
        return e, status
    return r, status


def parse_megamillions_results(results):
    # The endpoint returns a json string inside xml ?????
    # I hate that, so I just regex it out
    parsed_results = re.findall(r"{.*}", results.text)
    return parsed_results[0]


def get_megamillions():
    r, status = make_lottery_web_request("https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData")
    if status == 200:
        parsed_results = parse_megamillions_results(r)
    else:
        return r
    processed_results = process_megamillions_results(parsed_results)
    return processed_results


def parse_powerball_results(results: dict) -> str:
    data = results.get("data", None)
    current_results = str()
    try:
        numbers = data[-1]
        date = numbers[-3].split("T")[0]
        current_results = f"Winning Powerball numbers for {date}: {numbers[-2]} - Powerball: {numbers[-1]}"
    except Exception as e:
        logging.error(f"Error processing powerball numbers - {e}")
        current_results = "Something went wrong"
    return current_results


def get_powerball() -> str:
    r, status = make_lottery_web_request("https://data.ny.gov/api/views/d6yy-54nr/rows.json")
    if status == 200:
        processed_results = parse_powerball_results(r.json())
    else:
        return r
    return processed_results
