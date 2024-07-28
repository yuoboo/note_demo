# coding=utf-8
from celery import Celery

from configs import basic
from configs.celery import CELERY_CONFIG, CELERY_INCLUDE

project_name = basic.PROJECT_NAME
celery_app = Celery(
    project_name,
    broker=CELERY_CONFIG['CELERY_BROKER'],
    include=CELERY_INCLUDE
)

celery_app.conf.update(CELERY_CONFIG)

