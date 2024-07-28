
import aiotask_context
import typing

from configs.basic import PROJECT_NAME
from constants import EventScene, EventStatus
from services import svc
from utils.client import HttpClient, SERVE_RETRY_MAX
from configs import config
from utils.json_util import json_dumps
from utils.strutils import uuid2str, gen_uuid
from utils.logger import app_logger

__all__ = ["DataReportBase"]

from utils.table_util import TableUtil

app_env = config.get("APP_ENV")

URL_MAP = {
    # POST  http://bd-inner-gateway-dev.2haohr.com/bd/dcas/report
    "local": "http://bd-inner-gateway-dev.2haohr.com/bd/dcas/report",
    "dev": "http://bd-inner-gateway-dev.2haohr.com/bd/dcas/report",
    "test": "http://bd-inner-gateway-test.2haohr.com/bd/dcas/report",
    "production": "http://bd-inner-gateway.2haohr.com/bd/dcas/report"
}


def covert_field(row: dict, f_map: dict, is_filter: bool = True) -> dict:
    """
    转换字典的key
    :param row:
    :param f_map: fields_map 映射字典
    :param is_filter: 是否过滤不在f_map中的字段
    :return:
    """
    new_row = dict()
    for k, v in row.items():
        if k in f_map:
            new_row[f_map[k]] = v
        elif not is_filter:
            new_row[k] = v
    return new_row


MAX_RETRY = 3   # http请求失败重试最大次数


class DataReportBase:
    """
    数据上报基类，具体上报场景直接继承此基类
    """
    fields_map = dict()

    # filter_fields 需要配置fields_map才会生效
    # 是否需要过滤掉不在fields_map里面的字段，很多业务场景取出来的数据有很多不需要上报的字段
    filter_fields = True

    ev_scene = EventScene.SR  # 事件发送场景， 默认为统计报表 预留拓展
    ev_code = ""    # 事件编码, 如果是发送多个事件的数据 此参数无效

    system_name = "eebo.ehr.recruitment"

    table_cls = None

    @property
    def _table_tbu(self):
        assert self.table_cls is not None, "请指定 table_cls 属性"
        return TableUtil(self.table_cls)

    def get_model_fields(self, fields: list = None) -> list:
        """
        从 field_map 中过滤出 model 字段
        使用此方法必须配置 model_cls 属性
        """
        if fields:
            return self._table_tbu.filter_keys(fields, is_filter=True)

        if self.fields_map:
            return self._table_tbu.filter_keys(list(self.fields_map), is_filter=True)
        return []

    async def get_ev_data(self, company_id: str, ids: list, **kwargs) -> list:
        """通过ids获取上报数据 需要返回 list"""
        raise NotImplementedError

    def send_task(self, company_id: str, user_id: str = '', ev_data: list = None, ev_ids: list = None,
                  ev_scene: int = EventScene.SR, ev_code: str = '',
                  is_retry: bool = False, max_retry: int = MAX_RETRY,
                  **kwargs):
        """
        异步执行上报， 参数说明请见 send_data
        此方法只适用于 api接口条用，不能在celery中调用
        """
        _app = aiotask_context.get("app")
        _app.add_task(
            self.send_data(
                company_id=company_id,
                user_id=user_id,
                ev_data=ev_data,
                ev_ids=ev_ids,
                ev_scene=ev_scene,
                ev_code=ev_code,
                is_retry=is_retry,
                max_retry=max_retry,
                **kwargs)
        )

    async def send_data(self, company_id: str, user_id: str = '',
                        ev_data: typing.List[dict] = None,
                        ev_ids: list = None,
                        ev_scene: int = EventScene.SR,
                        ev_code: str = "",
                        is_retry: bool = False, max_retry: int = MAX_RETRY,
                        **kwargs):
        """
        发送上报数据
        :param company_id:
        :param user_id:
        :param ev_data: 上报数据列表(列表里面为字典), ev_data的优先级大于ev_ids, 在有ev_data参数时不会使用ev_ids
        :param ev_ids: 上报数据需要的ids， 此参数会传给 get_ev_data 方法, 所以需要重写此方法
        :param ev_scene:  事件分类  EventScene
        :param ev_code: 事件编码
        :param is_retry:  是否启动失败重试
        :param max_retry: 最大重试次数， 在is_retry为True时有效
        :param kwargs:  需要传给 get_ev_data 的额外参数
        :return:
        """
        app_logger.info(
            f"[data_report] send_data: company_id-{company_id}, ev_data-{ev_data}, ev_ids-{ev_ids}"
        )
        ev_data = ev_data or []
        ev_ids = ev_ids or []
        ev_scene = ev_scene or self.ev_scene
        ev_code = ev_code or self.ev_code
        max_retry = max_retry if is_retry else SERVE_RETRY_MAX

        task_id = gen_uuid()
        try:
            # 通过 ev_ids 获取数据
            if not ev_data and ev_ids:
                ev_data = await self.get_ev_data(company_id, ev_ids, **kwargs)

            # 准备数据
            ev_data = await self.prepare_data(company_id, ev_data, **kwargs)

            # 校验，清洗数据
            ev_data = await self._handle_data(company_id, ev_data)
            if not ev_data:
                raise Exception("数据为空！")
        except Exception as e:
            await svc.data_report.insert_data(
                task_id=task_id,
                company_id=company_id,
                user_id=user_id,
                data=json_dumps({"ev_data": ev_data, "ev_ids": ev_ids}),
                ev_scene=ev_scene,
                ev_code=ev_code,
                status=EventStatus.S_ERROR,
                exec_msg=f"上报前报错:{str(e)}"
            )
            return

        _data = {
            "id": task_id,
            "company_id": uuid2str(company_id),
            "ev_type": ev_code,
            "system_name": self.system_name,
            "data": ev_data
        }

        http_url = URL_MAP.get(app_env)

        # 发送数据
        res = await HttpClient.post(
            http_url, data=json_dumps(_data),
            headers={"Content-Type": "application/json"},
            max_retry=max_retry
        )

        if res and res.get('code') == 200:
            await svc.data_report.insert_data(
                task_id=task_id,
                company_id=company_id,
                user_id=user_id,
                data=json_dumps({"ev_data": ev_data, "ev_ids": ev_ids}),
                ev_scene=ev_scene,
                ev_code=ev_code,
                status=EventStatus.SUCCESS,
                exec_msg=f'获取响应成功:{res}'
            )
        else:
            await svc.data_report.insert_data(
                task_id=task_id,
                company_id=company_id,
                user_id=user_id,
                data=json_dumps({"ev_data": ev_data, "ev_ids": ev_ids}),
                ev_scene=ev_scene,
                ev_code=ev_code,
                status=EventStatus.R_ERROR,
                exec_msg=f'获取响应失败:{res}'
            )

    async def prepare_data(self, company_id: str, ev_data: list, **kwargs) -> list:
        return ev_data

    async def handle_row(self, company_id: str, row: dict) -> dict:
        """
        此方法在 字段key转换之前执行
        处理行数据
        """
        return row

    async def _handle_data(self, company_id: str, data: list) -> list:
        """
        处理数据
        """
        res = []
        for row in data:
            row = await self.handle_row(company_id, row)

            # 转换字段
            if self.fields_map:
                row = covert_field(row, self.fields_map, is_filter=self.filter_fields)
            res.append(row)
        return res


if __name__ == '__main__':
    # 数据都准备好了 不需要额外操作 可以直接使用data_report
    _report = DataReportBase()
    _report.send_task(
        company_id="f79b05ee3cc94514a2f62f5cd6aa8b6e",
        user_id="362f7de6128e460589ef729e7cdda774",
        ev_data=[{"id": "01c5a0d370474779a3f59e8d2e9fe3d1"}]
    )

    # 业务数据需要重新清洗或者组装， 重写
    _report = DataReportBase()
    _report.send_task(
        company_id="f79b05ee3cc94514a2f62f5cd6aa8b6e",
        user_id="362f7de6128e460589ef729e7cdda774",
        ev_ids=["01c5a0d370474779a3f59e8d2e9fe3d1", "0733de96e9e94b1e8bdde0029a1a3637"]
    )

