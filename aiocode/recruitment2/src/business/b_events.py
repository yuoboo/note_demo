# coding: utf-8
import logging

from business.b_wework import WeWorkBusiness
from business.commons.data_report import DataReportBiz
from constants import WEWORK_2HAOHR_STATE
from constants.redis_keys import COMPANY_DEPT_TREE_KEY, COMPANY_DEPT_LIST_KEY
from drivers.redis import redis_db
from services import svc
from services.s_dbs.s_job_position import JobPositionUpdateService, JobPositionSelectService
from services.s_https.s_person_ucenter import PersonUCenterService
from utils.strutils import uuid2str

logger = logging.getLogger('app')


class SubscriptionEventBusiness(object):
    """
    订阅事件业务处理类
    """

    @classmethod
    async def orgs_events(cls, ev_type: int, data: dict):
        """
        部门信息变更事件
        @param ev_type:
        @param data:
        @return:
        """
        type_code = data.get("type")
        body_data = data.get("body") or {}
        company_id = body_data.get("company_id")
        if ev_type == 55010:
            # 删除部门相关的全局缓存
            redis_cli = await redis_db.default_redis
            dept_list_key = COMPANY_DEPT_LIST_KEY.format(company_id=uuid2str(company_id))
            dept_tree_key = COMPANY_DEPT_TREE_KEY.format(company_id=uuid2str(company_id))
            await redis_cli.delete(dept_list_key)
            await redis_cli.delete(dept_tree_key)

            # 删除不用人部门信息
            if type_code == "dept_delete":
                dep_ids = body_data.get("ids")
                job_positions = await JobPositionSelectService.get_job_positions_by_dep_ids(
                    company_id=company_id, dep_ids=dep_ids, fields=["id"]
                )
                position_ids = [p["id"] for p in job_positions]
                if position_ids:
                    await JobPositionUpdateService.delete_dep_info(
                        company_id, position_ids
                    )

                    # 这里不能使用send_task, send_task在celery中无效
                    await DataReportBiz.update_job_position.send_data(
                        company_id=company_id, ev_ids=position_ids
                    )

            # 更新用人部门信息
            if type_code == "dept_full_name_update":
                change_dept_list = body_data.get("change_dept")
                for item in change_dept_list:
                    await JobPositionUpdateService.update_dep_info(
                        company_id, item.get("id"), item.get("full_name")
                    )

    @classmethod
    async def callback_gateway_events(cls, ev_type: int, data: dict):
        if ev_type == 10014:
            # 企业微信回调
            change_type = data.get('ChangeType', None)
            if change_type in ['add_external_contact']:
                suite_id = data.get('SuiteId')
                corp_id = data.get('AuthCorpId')
                external_user_id = data.get('ExternalUserID')
                state = data.get('State')

                if state == WEWORK_2HAOHR_STATE:
                    info = await PersonUCenterService.wework_get_core_suite_info(
                        suite_id=suite_id,
                        corp_id=corp_id
                    )
                    company_id = info.get('company_id', None)
                    if company_id:
                        await WeWorkBusiness.add_external_contact(external_user_id, company_id=company_id)
            elif change_type in ['del_external_contact', 'del_follow_user']:
                suite_id = data.get('SuiteId')
                corp_id = data.get('AuthCorpId')
                external_user_id = data.get('ExternalUserID')
                info = await PersonUCenterService.wework_get_core_suite_info(
                    suite_id=suite_id,
                    corp_id=corp_id
                )
                company_id = info.get('company_id', None)
                if company_id:
                    await WeWorkBusiness.add_external_contact(external_user_id, company_id=company_id)

    @classmethod
    async def sms_events(cls, ev_type: int, data: dict):
        """
        短信发送回调事件
        @param ev_type:
        @param data:
        @return:
        """
        if ev_type == 30110:
            biz_id = data.pop("biz_id", "")
            await svc.activate_record.fill_notify_result(biz_id, data, 1)

    @classmethod
    async def handle_events(cls, ev_from: str, ev_type: int, event_id: str, data: dict):
        """
        @param ev_from: 发布事件的系统
        @param ev_type: 事件类型编码
        @param event_id: 事件ID
        @param data:
        @return:
        """
        project_name = ev_from.split('.')[-1]
        func_name = getattr(cls, f'{project_name}_events')
        if func_name:
            await func_name(ev_type, data)
        logger.info(f"订阅事件, from:{ev_from},ev_type:{ev_type},event_id:{event_id}, data:{data}")
