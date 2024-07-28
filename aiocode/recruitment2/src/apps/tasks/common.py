# coding: utf-8
import asyncio
import logging

from business.b_events import SubscriptionEventBusiness
from celery_worker import celery_app
from services.s_https.s_common import get_ip

logger = logging.getLogger('app')


@celery_app.task
def get_ip_task():
    async def _helper():
        ip = await get_ip()
        logger.warning(f'celery服务器IP: {ip}')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())


@celery_app.task
def subscription_event_task(data):
    async def _helper():
        logger.info(f'接收到回调用事件 data: {data}')
        await SubscriptionEventBusiness.handle_events(
            data.get("from"), data.get("ev_type"),
            data.get("event_id"), data.get("data")
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())
