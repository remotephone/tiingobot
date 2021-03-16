FROM python:3.8

WORKDIR /code

COPY tiingobot/requirements.txt .

RUN pip install -r requirements.txt

COPY tiingobot/src/ .

# command to run on container start
CMD [ "python", "./tiingobot.py" ]