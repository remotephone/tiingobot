FROM python:3.8-slim

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

# command to run on container start
CMD [ "python", "./tiingobot.py" ]