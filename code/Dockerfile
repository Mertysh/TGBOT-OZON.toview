FROM python:3.9.12-slim-buster

WORKDIR /code
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH=/root/.local/bin:$PATH

COPY . .
CMD python bot.py
