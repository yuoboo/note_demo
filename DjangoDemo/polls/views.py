import logging
import redis

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# from log import logger
logger = logging.getLogger(__name__)

redis_conn = redis.StrictRedis.from_url("redis://localhost:6379/0")


class DemoView(APIView):

    def get(self, request):
        redis_conn.incr('django', 1)
        logger.info(f"view: {redis_conn.get('django')}")
        logger.error("view: test error")
        try:
            x = 1 / 0
        except ZeroDivisionError as e:
            logger.exception('ZeroDivisionError: %s', e)
        return Response({"hello": "hello world"})


