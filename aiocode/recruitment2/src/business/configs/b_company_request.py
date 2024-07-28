from datetime import datetime
from celery_worker import celery_app

from error_code import Code as ErrorCode
from kits.exception import APIValidationError
# from utils.status_code import ErrorCode

from configs import config
from services.s_dbs.config.s_company_request import CompanyRequestService


class CompanyRequestBusiness(object):
    @classmethod
    async def open(cls, company_id: str, user_id: str) -> bool:
        """
        开通招聘
        """
        if await CompanyRequestService.check_company_request(company_id):
            raise APIValidationError(ErrorCode.config_company_request_open)

        # 创建开通记录
        await CompanyRequestService.create(company_id, user_id)

        # 初始化招聘渠道
        # 初始化招聘职位
        # 初始化应聘登记表

        # 发起异步开通招聘
        celery_app.send_task("apps.tasks.configs.company_request.open_async_task", args=(company_id, user_id))
        return True

    @classmethod
    async def open_async(cls, company_id: str, user_id: str) -> bool:
        """
        异步开通招聘
        """
        # 初始化offer模板
        # 初始化面试模板
        # 初始化淘汰模板
        # 初始化面试签到码
        # 初始化面试联系人
        # 初始化福利标签
        # 初始化企业介绍
        # 初始化淘汰原因
        # 初始化面试联系人
        # 初始化标准简历模板
        # 初始化面试团队
        return True

    @classmethod
    async def get_info(cls, company_id: str):
        """
        获取开通信息
        """
        query = await CompanyRequestService.get(company_id)
        if query is None:
            raise APIValidationError(ErrorCode.config_company_request_open)

        data = {
            "is_open": False,
            "is_new": False,
            "open_dt": query.get('add_dt')
        }
        if query:
            env2open_dt = {
                "local": datetime.strptime("2020-08-05 10:00", "%Y-%m-%d %H:%M"),
                "dev": datetime.strptime("2020-08-05 10:00", "%Y-%m-%d %H:%M"),
                "test": datetime.strptime("2020-08-13 17:00", "%Y-%m-%d %H:%M"),
                "production": datetime.strptime("2020-09-05 14:00", "%Y-%m-%d %H:%M")
            }
            new_open_dt = env2open_dt.get(config.get('ENV'))

            data = {
                "is_open": True,
                "is_new": query.get('add_dt') > new_open_dt,
                "open_dt": query.get('add_dt')

            }
        return data
