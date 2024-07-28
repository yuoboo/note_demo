import asyncio
import logging

from business import biz
from celery_worker import celery_app
from services.s_dbs.talent_activate.s_activate_record import ActivateRecordService

logger = logging.getLogger('app')


@celery_app.task
def activate_notify_candidates(
        company_id: str, user_id: str, task_id: str, candidate_id2activate_id: dict,
        validated_data: dict, is_try: bool = False
):
    async def _helper():
        await biz.activate_record.active_notify_candidates(
            company_id, user_id, task_id, candidate_id2activate_id, validated_data, is_try
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())


@celery_app.task
def fail_talent_activate_status():
    """
    定时更新激活记录的激活状态，每天凌晨1点执行
    @return:
    """
    async def _helper():
        await ActivateRecordService.update_activate_status_by_timer()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())
