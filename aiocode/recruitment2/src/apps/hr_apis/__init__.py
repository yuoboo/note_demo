# coding: utf-8
import time

from celery_worker import celery_app
from services.s_https.s_common import get_ip
from services.s_https.s_employee import DepartmentService
from utils.api_auth import BaseView
import logging

from utils.ehr_request import EhrRequest

logger2 = logging.getLogger('celery.task')
logger = logging.getLogger('app')


class Ping(BaseView):

    async def get(self, request):
        return self.data("pong")


class IpView(BaseView):

    async def get(self, request):
        ip = await get_ip()
        logger.warning(f'web服务器IP: {ip}')
        celery_app.send_task("apps.tasks.common.get_ip_task")
        return self.data(ip)


class Redis01Test(BaseView):

    async def get(self, request):
        company_id = "ec9ab455f91c46c9abaf47d508182972"
        t1 = time.perf_counter()
        res1 = await DepartmentService.get_com_list(company_id)
        t2 = time.perf_counter()
        res2 = await DepartmentService.get_com_tree(company_id)
        t3 = time.perf_counter()

        data = {
            "list": t2-t1,
            "data1": res1,
            "tree": t3-t2,
            "data2": res2
        }
        return self.data(data)


class Redis02Test(BaseView):

    async def get(self, request):
        company_id = "ec9ab455f91c46c9abaf47d508182972"
        t1 = time.perf_counter()
        query_data = {"company_id": company_id}
        result1 = await EhrRequest("orgs").intranet("department/list").get(
            data=query_data
        )
        res1 = result1.get("data") or [] if result1 else []
        t2 = time.perf_counter()
        result2 = await EhrRequest("orgs").intranet("department/tree").get(
            data={"company_id": company_id}
        )
        res2 = result2.get("data") or [] if result2 else []
        t3 = time.perf_counter()

        data = {
            "list": t2-t1,
            "data1": res1,
            "tree": t3-t2,
            "data2": res2
        }
        return self.data(data)
