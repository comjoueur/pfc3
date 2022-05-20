FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /home/pfc2

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
