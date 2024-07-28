# coding: utf-8
import asyncio
import json
import logging
from datetime import datetime

from business import biz
from celery_worker import celery_app
from constants import TaskStatus
from services.s_https.s_task_center import TaskCenterService, TaskCenterData

logger = logging.getLogger('app')


@celery_app.task
def portals_export_task_center(company_id, user_id, task_type, task_id, data):
    async def _helper():
        start_time = datetime.now()
        print(company_id, user_id, task_type, task_id)
        tc_data = TaskCenterData(company_id, user_id, task_type, task_id)
        try:
            download_url = await biz.portal_delivery.export_referral_record(company_id, data)
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            await TaskCenterService.update_task_progress(tc_data, 100)
            output = {"download_url": download_url, "redirect_url": ""}
            await TaskCenterService.task_over_callback(tc_data, TaskStatus.success, duration=duration,
                                                       output=json.dumps(output))
        except Exception as e:
            logging.error(u'导出错误，company_id:%s, error:%s', company_id, str(e))
            await TaskCenterService.update_task_progress(tc_data, 100)
            err_msg = json.dumps({"error_text": u'下载失败'})
            await TaskCenterService.task_over_callback(tc_data, TaskStatus.half_fail, duration=0, output=err_msg,
                                                       exp_stack=err_msg)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())
