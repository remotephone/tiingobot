import json
import os
import random
import logging
import openai
import requests
from bs4 import BeautifulSoup
from src.tiingobot import logger


def get_tax_refund(ssn: str = None):
    if not ssn:
        logger.warning(
            "No SSN provided"
        )  # Assuming 'logger' is the imported logger instance
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
        logger.error(
            "Error calculating refund", exc_info=True
        )  # Use logger to log exceptions
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
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}]
    )

    # Check if the completion was successful
    if completion.choices[0].message.content is None:
        raise RuntimeError("Unable to get a response from the AI")

    return completion.choices[0].message.content


def process_movie_title(title):
    logger.info(f"Processing movie title: {title}")  # Use logger instead of logging
    return title.lower().replace(" ", "_")


def rt(movie_title: str) -> str:
    # Get user input for the movie title
    logger.info(
        f"User input for movie title: {movie_title}"
    )  # Use logger instead of logging

    # Process the movie title
    processed_title = process_movie_title(movie_title)
    logger.info(
        f"Processed movie title: {processed_title}"
    )  # Use logger instead of logging

    # Construct the URL of the Rotten Tomatoes movie page
    url = f"https://www.rottentomatoes.com/m/{processed_title}"
    logger.info(f"Constructed URL: {url}")  # Use logger instead of logging

    # Make the HTTP request to the URL
    logger.info(f"Making HTTP request to URL: {url}")  # Use logger instead of logging
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        logger.info("HTTP request successful")  # Use logger instead of logging
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the critics score
        critics_score_button = soup.find("rt-button", {"slot": "criticsScore"})
        critics_score_text = (
            critics_score_button.find("rt-text").get_text(strip=True)
            if critics_score_button
            else "N/A"
        )
        logger.info(
            f"Critics score extracted: {critics_score_text}"
        )  # Use logger instead of logging

        # Extract the audience score
        audience_score_button = soup.find("rt-button", {"slot": "audienceScore"})
        audience_score_text = (
            audience_score_button.find("rt-text").get_text(strip=True)
            if audience_score_button
            else "N/A"
        )
        logger.info(
            f"Audience score extracted: {audience_score_text}"
        )  # Use logger instead of logging

        result = f"Critics Score: {critics_score_text}\nAudience Score: {audience_score_text}"
        logger.info(f"Result: {result}")  # Use logger instead of logging
        return result
    else:
        logger.error(
            f"Failed to retrieve the page. Status code: {response.status_code}"
        )  # Use logger instead of logging
        return f"Failed to retrieve the page. Status code: {response.status_code}"
