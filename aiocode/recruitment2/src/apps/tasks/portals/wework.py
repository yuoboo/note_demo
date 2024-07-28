# coding: utf-8
import asyncio
import logging

from business.b_wework import WeWorkBusiness
from celery_worker import celery_app

logger = logging.getLogger('app')


@celery_app.task
def update_wework_external_contact(external_user_id, company_id):
    async def _helper():
        await WeWorkBusiness.add_external_contact(external_user_id, company_id=company_id)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())
