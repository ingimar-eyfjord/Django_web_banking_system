FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y libpq-dev python3-dev python-dev python-psycopg2 python3-psycopg2 gcc

ADD requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

EXPOSE 8000

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]