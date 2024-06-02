import redis

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from log import logger


redis_conn = redis.StrictRedis.from_url("redis://localhost:6379/0")


class DemoView(APIView):

    def get(self, request):
        redis_conn.incr('django', 1)
        logger.info(f"django: {redis_conn.get('django')}")
        logger.error("django: test error")
        return Response({"hello": "hello world"})


