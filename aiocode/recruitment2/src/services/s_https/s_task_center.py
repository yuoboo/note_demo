import logging

from utils.client import HttpClient

from configs import config
from constants import RequestType, TaskStatus
from kits.exception import ServiceException

app_env = config.get("APP_ENV")
logger = logging.getLogger("services.task_center")
project_name = 'eebo.ehr.recruitment'


class TaskCenterData(object):
    def __init__(self, company_id, user_id, task_type, task_id=None):
        self.company_id = str(company_id).replace('-', '')
        self.user_id = str(user_id).replace('-', '')
        self.task_id = task_id
        self.task_type = task_type


class TaskCenterService(object):
    """
    任务中心
    """
    @classmethod
    def get_sp_api(cls):
        sp_api_config = {
            "local": "http://sp-inner-gateway-dev.2haohr.com",
            "dev": "http://sp-inner-gateway-dev.2haohr.com",
            "test": "http://sp-inner-gateway-test.2haohr.com",
            "production": "http://sp-inner-gateway.2haohr.com"
        }
        return sp_api_config[app_env]

    @classmethod
    def get_bp_api(cls):
        bp_api_config = {
            "local": "http://bp-inner-gateway-dev.2haohr.com",
            "dev": "http://bp-inner-gateway-dev.2haohr.com",
            "test": "http://bp-inner-gateway-test.2haohr.com",
            "production": "http://bp-inner-gateway.2haohr.com"
        }
        return bp_api_config[app_env]

    @classmethod
    async def call_task_center(cls, url, request_type, params=None):
        timeout = 60
        try:
            if request_type == RequestType.get:
                ret = await HttpClient.get(url, timeout=timeout)
            else:
                ret = await HttpClient.post(url, json_body=params, timeout=timeout)
        except Exception as e:
            logger.error("对接任务中心错误:%s", e, exc_info=True)
            return None, False
        else:
            if ret['code'] == 100:
                return ret['data'], True
            else:
                return ret['err_msg'], False

    @classmethod
    async def new_id(cls):
        """
        获取Task ID HTTP GET
       **请求**: http://ip:port/sp/tcenter/task/newtid
        请求返回{
            "code": 100,  		 # 100表示成功，其他请参考err_msg
            "err_msg": "dddddd"  # code非100时存在，说明错误原因
            "data": {
                "tid": 123456    # 获取到的task id  }
             }
        :return:
        """
        url = '{}/sp/tcenter/task/newtid'.format(cls.get_sp_api())
        data, is_success = await cls.call_task_center(url, RequestType.get)
        if is_success:
            tid = data.get('tid')
            return tid
        else:
            logger.error(u'从任务中心获取newid失败:%s', data, exc_info=True)
            raise ServiceException(-1, msg=u'内部错误')

    @classmethod
    async def add_task(cls, tc_data, title, task_args="", ext_args="", remark=None):
        """
        task_type: 任务主类型(1、导入；2、导出；3、打包下载；4、员工同步)
         新增任务 在业务中台产生一个任务 HTTP POST
        **请求**: http://ip:port/sp/tcenter/task/add
            body
                {"systemid": "eebo.ehr.attendance2",    	# 子系统
                "task_list": [{"tid": 1,        			# 任务ID，通过newtid获取
                                "ptid":0, 					# 父级任务ID，即此任务以来上一个任务，形成任务链
                                "type": 2,					# 任务主类型(1、导入；2、导出；3、打包下载；4、员工同步)
                                "title": "单任务标题",		# 任务标题
                                "args": "kdjkjfksd==", 		# 任务执行的参数
                                "ext_args": "dafasda==", 	# 任务执行扩展参数
                                "remark":"dddddd"  			# 任务描述
                                "support_retry"             # 支持重试True
                                "support_cancel"            # 支持取消True
                            },{"tid": 2,
                               "ptid": 0, 					# 父级任务ID，即此任务依赖上一个任务，上一个任务的输出，为这个任务的输入
                               "type": 2,					# 任务主类型
                               "title": "单任务标题",		# 任务标题
                               "ext_args": "dafasda==", 	# 任务执行扩展参数
                               "remark":"dddddd"  			# 任务描述
                               "support_retry"             # 支持重试True
                                "support_cancel"            # 支持取消True
                            }]
                }
        :return:
        """
        url = '{}/sp/tcenter/task/add'.format(cls.get_sp_api())

        params = {'systemid': project_name,
                  "task_list": [{"tid": tc_data.task_id, "ptid": 0,
                                 "type": tc_data.task_type, "title": title,
                                 "args": task_args, "ext_args": ext_args,
                                 "remark": remark,
                                 "support_retry": False,
                                 "support_cancel": False
                                 }]
                  }

        data, is_success = await cls.call_task_center(url, RequestType.post, params=params)
        if not is_success:
            logger.error(u'在任务中心新增任务失败:%s', data, exc_info=True)
            raise ServiceException(-1, msg=u'内部错误, 新增任务失败')
        return

    @classmethod
    async def add_task_record(cls, tc_data):
        """
        增加任务ID到用户，企业的映射  HTTP POST
        url : http://ip:port/bp/tcenter/task/add_record
        [
            {
               "userid": "12312121",      # 用户ID
               "companyid": "32324324"    # 企业ID
               "taskid": "555555"        # 任务ID
            },
        ]
        :return:
        """
        url = '{}/bp/tcenter/task/add_record'.format(cls.get_bp_api())
        params = [{"userid": str(tc_data.user_id), "companyid": str(tc_data.company_id), "taskid": tc_data.task_id}]
        data, is_success = await cls.call_task_center(url, RequestType.post, params=params)
        if not is_success:
            logger.error(u'在任务中心新增任务映射失败:%s', data, exc_info=True)
            raise ServiceException(-1, msg=u'内部错误, 新增任务映射失败')
        return

    @classmethod
    async def get_task(cls):
        """
        获取任务  HTTP GET
        url: http://ip:port/sp/tcenter/task/get_task?sysid=demo
        {
            "code": 100,
            "err_msg": "Ok",
            "data":
            {
                "tid": 1001,
                "ptid": 1000,
                "title": "任务标题",
                "type": 1,
                "args": "任务参数",
                "ext_args": "任务扩展参数",
                "remark": "任务描述"
            }
        }
        :return:
        """
        system_id = project_name
        url = '{}/sp/tcenter/task/get_task?sysid={}'.format(cls.get_sp_api(), system_id)
        data, is_success = await cls.call_task_center(url, RequestType.get)
        if not is_success:
            logger.error(u'在任务中心获取任务失败:%s', data, exc_info=True)
            raise ServiceException(-1, msg=u'内部错误, 获取任务失败:' + str(data))
        return

    @classmethod
    async def get_task_info(cls, tc_data):
        """
        此接口提供给任务中台使用,查询指定的任务ID的信息
        url: http://ip:port/sp/tcenter/task/batch
        http://ip:port/sp/tcenter/task/batch?tids=1234,3456,3445   #tids为指定的任务ID，多个ID用逗号分隔
        {
            "code": 100,
            "err_msg": "Ok",
            "data":[
            {
                "tid": 1001,
                "state": 0,
                "title": "任务标题",
                "type": 1,
                "output": "任务输出",
                "progress": "任务进度",
                "addtime": 152454545455,
                "remark": "任务描述"
            },
            {
                "tid": 1001,
                "state": 0,
                "title": "任务标题",
                "type": 1,
                "output": "任务输出",
                "progress": "任务进度",
                "addtime": 152454545455,
                "remark": "任务描述"
            }
            ]
        }
        :return:
        """
        url = '{}/sp/tcenter/task/batch?tids={}'.format(cls.get_sp_api(), tc_data.task_id)
        data, is_success = await cls.call_task_center(url, RequestType.get)
        if not is_success:
            logger.error(u'在任务中心查询指定的任务ID的信息失败:%s', data, exc_info=True)
            raise ServiceException(-1, msg=u'内部错误, 查询指定的任务ID的信息失败:' + str(data))
        return data

    @classmethod
    async def update_task_progress(cls, tc_data, progress):
        """
        任务进度更新回调
        url: http://ip:port/sp/tcenter/task/callback/progress
        请求：

        {
           "tid":12345,   # 任务ID
           "progress": 10, # 递进的进度值，非当前总进度值，如当前总进度为50，此次回调只更新10%
        }
        回复：
        {
            "code": 100,
            "err_msg": "dddddd"
            "data": {
                "state": 4  # 待取消，worker应立即终止此任务执行，并调用任务取消回调，将reason设置为4
            }
        }
        :param progress: 更新的进度值
        :return:
        """
        url = '{}/sp/tcenter/task/callback/progress'.format(cls.get_sp_api())
        params = {"tid": tc_data.task_id, "progress": progress}
        data, is_success = await cls.call_task_center(url, RequestType.post, params=params)
        state = None
        if not is_success:
            try:
                # 获取任务状态，如果为1： 任务等待调度中 2： 任务已调度，排队中，需要get_task取走任务后才能更新进度
                task_info = await cls.get_task_info(tc_data)
                state = task_info[0]['state']
                if state and state in (TaskStatus.wait, TaskStatus.queue):
                    await cls.get_task()
                    await cls.update_task_progress(tc_data, progress)
            except Exception as e:
                logger.error(u'在任务中心更新任务进度失败:%s', data, exc_info=True)
                raise ServiceException(-1, msg=u'更新任务进度失败:' + str(e))
        if data and isinstance(data, dict):
            state = data.get('state', None)
        elif state:
            state = state
        else:
            state = None
        if state and state == TaskStatus.to_cancel:
            # 待取消，调用回调接口取消，把reason置为5
            await cls.task_over_callback(tc_data, TaskStatus.canceled)
        return

    @classmethod
    async def task_over_callback(cls, tc_data, reason, duration=0, output=None, exp_stack=None):
        """
        当任务完成或者取消等情况出现后，调用回调通知任务调度中心
        url**: http://ip:port/sp/tcenter/task/callback/over
            {
                "tid":12345,
                "reason": 0,    				#4 任务待取消，0 执行成功，-1 执行失败
                "duration": 123, 				# 任务耗时时长
                "output":"afsdfads",			# reason=0时，为任务执行后的输出内容
                "exp_stack": "dafdsadfasdf"  	# state为-1时须存在
            }
        output字段说明：
            当任务执行成功时，此字段将返回给前端进行展示，对应格式要求为，且为string类型：
            {
                "download_url": "http://baidu.com",
                "redirect_url": "http://baidu.com"
                error_text: "error_text"      // 错误     的信息
            }

            exp_stack字段说明：
            当reason为-2时，需要遵循output字段规则，且为string类型：
            {
                "download_url": "http://baidu.com",
                "redirect_url": "http://baidu.com"
            }

            当reason为0时，此字段无值
            当reason为-1时，此字段为异常堆栈信息，此信息不回返回给前端展示，但可以在任务中心监控看到

        :return:
        """
        url = '{}/sp/tcenter/task/callback/over'.format(cls.get_sp_api())
        para = {
            "tid": tc_data.task_id,
            "reason": reason,
            "duration": duration,
            "output": output,
            "exp_stack": exp_stack
        }
        data, is_success = await cls.call_task_center(url, RequestType.post, para)
        if not is_success:
            logger.error(u'回调通知任务调度中心失败:%s', data, exc_info=True)
            raise ServiceException(-1, msg=u'内部错误, 回调任务失败')
        return data
