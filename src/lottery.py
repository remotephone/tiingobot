import requests
from bs4 import BeautifulSoup
import re
import json
import time
import logging

logger = logging.getLogger("tiingobot_logger")


def get_next_powerball():
    url = "https://www.powerball.com/"
    for i in range(3):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            next_date = soup.find("div", {"class": "count-down"})["data-drawdateutc"]
            jackpot = soup.find("span", {"class": "game-jackpot-number text-xxxl lh-1 text-center"}).text.strip()
            cash_value = soup.find("span", {"class": "game-jackpot-number text-lg lh-1 text-center"}).text.strip()
            return f"Next Drawing Date: {next_date}, Jackpot Amount: {jackpot}, Cash Value: {cash_value}"
        except Exception as e:
            logger.error(f"Error parsing powerball html - {e}")
            if i < 2:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
    return "Something went wrong"


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
