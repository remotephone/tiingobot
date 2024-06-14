import json
import logging
import os
import random

import openai
import requests
from bs4 import BeautifulSoup
from tiingologger import logger


def get_tax_refund(ssn: str = None):
    if not ssn:
        logger.warning("No SSN provided")  # Assuming 'logger' is the imported logger instance
        return "Please provide your real, honest social security number"
    ssn = ssn.replace("-", "")
    try:
        minimum = -int(ssn) * 10
        maximum = int(ssn) * 10
        random.seed()
        refund = random.randint(minimum, maximum)
        logger.info(f"Calculated refund: {refund}")  # Replaced print with logger.info
        if refund > 0:
            return f"Your refund is ${str(abs(refund))}"
        else:
            return f"You owe ${str(abs(refund))}"
    except ValueError as e:
        logger.error("Error calculating refund", exc_info=True)  # Use logger to log exceptions
        return "You owe one million dollars"


def get_artificial_intelligence():
    response = requests.get("https://api.adviceslip.com/advice")
    json_data = json.loads(response.text)
    quote = json_data["slip"]["advice"]
    return quote


def get_artificial_intelligence_v2(question: str) -> str:
    # Use the chatGPT free api to ask a question
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if len(question) > 1000:
        return "Please ask a shorter question"
    # Create a completion object
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}])

    # Check if the completion was successful
    if completion.choices[0].message.content is None:
        raise RuntimeError("Unable to get a response from the AI")

    return completion.choices[0].message.content


def process_movie_title(title):
    logger.info(f"Processing movie title: {title}")
    return title.lower().replace(" ", "_")


def rt(movie_title: str) -> str:
    # Get user input for the movie title
    logger.info(f"User input for movie title: {movie_title}")

    # Process the movie title
    processed_title = process_movie_title(movie_title)
    logger.info(f"Processed movie title: {processed_title}")

    # Construct the URL of the Rotten Tomatoes movie page
    url = f"https://www.rottentomatoes.com/m/{processed_title}"
    logger.info(f"Constructed URL: {url}")

    # Make the HTTP request to the URL
    logger.info(f"Making HTTP request to URL: {url}")
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        logger.info("HTTP request successful")
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find("title")
        rt_title_tag = soup.find("rt-title")

        title = title_tag.get_text(strip=True) if title_tag else rt_title_tag.get_text(strip=True) if rt_title_tag else "N/A"

        # Extract the critics score
        critics_score_tag = soup.find("rt-button", {"slot": "criticsScore"})
        audience_score_tag = soup.find("rt-button", {"slot": "audienceScore"})
        image_tag = soup.find("rt-img", {"alt": "movie poster"})
        image_url = image_tag["src"] if image_tag else None
        if image_url:
            image_url = image_url.split("/v2/")[-1]

        critics_score = critics_score_tag.find("rt-text").get_text(strip=True) if critics_score_tag else "N/A"
        logger.info(f"Critic score extracted: {critics_score}")

        audience_score = audience_score_tag.find("rt-text").get_text(strip=True) if audience_score_tag else "N/A"

        logger.info(f"Audience score extracted: {audience_score}")

        result = f"[{title}:]({url})\nCritics Score: {critics_score}\nAudience Score: {audience_score}"
        logger.info(f"Result: {result}")
        return result
    else:
        logger.error(f"Failed to retrieve the page. Status code: {response.status_code}")
        return f"Failed to retrieve the page. Status code: {response.status_code}"
