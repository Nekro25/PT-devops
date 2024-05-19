FROM python:3.12-slim

WORKDIR /tgBot

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "tg_bot.py"]
