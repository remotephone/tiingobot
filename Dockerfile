FROM python:3.14

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

# command to run on container start
CMD [ "python", "./tiingobot.py" ]