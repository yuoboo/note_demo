import logging

from services.s_https.s_task_center import TaskCenterData, TaskCenterService


class TaskCenterBusiness(object):
    @classmethod
    async def add(cls, company_id, user_id, task_type, title, remark):
        try:
            tc_data = TaskCenterData(company_id, user_id, task_type)
            tc_data.task_id = await TaskCenterService.new_id()
            await TaskCenterService.add_task(tc_data, title, task_args='none', remark=remark)
            await TaskCenterService.add_task_record(tc_data)
            await TaskCenterService.get_task()
            return tc_data
        except Exception as e:
            logging.error(u'对接任务中心失败，company_id:%s, error:%s', company_id, str(e))
            return 0
