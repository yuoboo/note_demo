# FROM python:3.8.6-buster
FROM registry.2haohr.com/library/python:3.8.6-buster

ADD src /data/wwwRoot

WORKDIR /data/wwwRoot

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt
