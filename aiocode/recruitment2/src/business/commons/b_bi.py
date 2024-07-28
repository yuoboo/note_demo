import asyncio

from constants import CandidateRecordStatus
from services import JobPositionSelectService
from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordService
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService
from services.s_https.s_bi import BIService
from services.s_https.s_ucenter import get_company_for_id
from utils.logger import app_logger
from utils.time_cal import time_stamp

__all__ = ["bi_biz"]


class BIBusiness(object):

    @staticmethod
    def _transfer_map(item: dict, fields_map: dict) -> dict:
        """
        转换字段映射, 统一数据格式
        :param item: dict
        :param fields_map: dict
        """
        assert isinstance(fields_map, dict), "param fields_map must be dict"
        res = {}
        for k, _k in fields_map.items():
            v = item.get(k, None)
            if v == "":
                # 将空串统一为 None
                res[_k] = None

            elif isinstance(v, bool):
                # 统一 bool -> 0 or 1
                res[_k] = 1 if v else 0
            else:
                res[_k] = v
        return res

    async def get_format_dict(self, company_id: str, data: list, event_type: str,
                              event_time: int = None, fields_map: dict = None, exe_type: str = "overwrite"):
        """
        组装上报数据
        :param company_id:
        :param data: 上报数据
        :param event_type: 上报事件类型
        :param event_time: 事件产生时间
        :param exe_type: 事件类型 目前固定overwrite
        :param fields_map: 格式化数据的字段map
        :return: 组装完之后的数据
        """
        event_time = event_time or time_stamp()
        # 格式化数据
        if fields_map:
            data = list(map(lambda x: self._transfer_map(x, fields_map), data))
            # data = cls.format_bi_data(data, fields_map)

        company_ = await get_company_for_id(company_id)

        return {
            "event_time": event_time,  # 事件产生时间戳
            "get_time": event_time,  # 事件分发平台回查时间戳
            "push_time": time_stamp(),  # 组装数据完成推到BI的时间
            "exe_type": exe_type,  # 事件类型 目前固定overwrite
            "event": event_type,  # 事件名
            "company_id": company_id,
            "group_id": None,  # 集团id
            "is_paid": 1 if company_.get("is_paid") else 0,  # 是否付费
            "comp_type": None,  # 企业类型  #企业版本：1:普通版、2：招聘版、3：启航版 、4集团版
            "properties": data  # 上报数据
        }

    async def send_job_position_to_bi(self, company_id: str, position_ids: list):
        """
        上报招聘职位信息到BI
        """
        _list = await JobPositionSelectService.get_positions_by_ids(
            company_id=company_id, ids=position_ids,
            fields=["id", "is_delete", "add_dt", "update_dt", "name", "position_total", "start_dt", "stop_dt", "status"]
        )

        if _list:
            event_type = "recruitment_demand_detail"
            _map = {
                "id": "id",
                "is_delete": "is_delete",
                "add_dt": "add_dt",
                "update_dt": "update_dt",
                "name": "position_name",
                "position_total": "position_total",
                "start_dt": "start_dt",
                "stop_dt": "stop_dt",
                "status": "recruitment_status",
                "emp_id": "emp_id"
            }
            data = await self.get_format_dict(company_id, _list, event_type, fields_map=_map)
            return await BIService.send_data_to_bi(data)
        else:
            app_logger.info("send_to_bi [job_position]: no data, company_id-{}, position_ids-{}".format(
                company_id, position_ids)
            )

    @staticmethod
    async def _fill_name(company_id: str, data: list):
        """
        填充job_position_name, recruitment_channel_name
        """
        position_ids = [_d["job_position_id"] for _d in data]
        channel_ids = [_d["recruitment_channel_id"] for _d in data]
        positions, channels = await asyncio.gather(
            JobPositionSelectService.get_positions_by_ids(company_id, ids=position_ids, fields=["id","name"]),
            RecruitmentChannelService.get_channels_by_ids(company_id, channel_ids, fields=["id", "name"])
        )
        position_map = {p["id"]: p["name"] for p in positions}
        channel_map = {c["id"]: c["name"] for c in channels}

        for d in data:
            d["job_position_name"] = position_map.get(d.get("job_position_id"), "")
            d["recruitment_channel_name"] = channel_map.get(d.get("recruitment_channel_id"), "")
        return data

    async def send_candidate_record_to_bi(self, company_id: str, candidate_record_ids: list):
        """
        上报应聘记录数据到BI
        目前只上报已入职的应聘记录信息
        """
        _list = await CandidateRecordService.get_candidate_records_by_ids(
            company_id, candidate_record_ids, status=[CandidateRecordStatus.EMPLOY_STEP4],
            fields=["id", "is_delete", "add_dt", "update_dt", "employee_id", "entry_dt", "job_position_id",
                    "recruitment_channel_id"]
        )

        if _list:
            # job_position_name, recruitment_channel_name
            _list = await self._fill_name(company_id, _list)
            event_type = "recruitment_entry_detail"
            _map = {
                "id": "id",
                "is_delete": "is_delete",
                "add_dt": "add_dt",
                "update_dt": "update_dt",
                "employee_id": "emp_id",
                "entry_dt": "entry_dt",
                "job_position_id": "position_id",
                "job_position_name": "position_name",
                "recruitment_channel_id": "channel_id",
                "recruitment_channel_name": "channel_name"
            }

            data = await self.get_format_dict(company_id, _list, event_type, fields_map=_map)
            return await BIService.send_data_to_bi(data)
        else:
            app_logger.info("send_to_bi [candi_record]: no data, company_id-{}, cr_ids-{}".format(
                company_id, candidate_record_ids
            ))

    async def send_channel_name_to_bi(self, company_id: str, channel_ids: list):
        """
        上报招聘渠道名称信息
        目前只上报已入职的应聘记录信息
        """
        _list = await CandidateRecordService.get_candidate_record_by_channel_id(company_id, channel_ids)
        return await self.send_candidate_record_to_bi(company_id, [_l["id"] for _l in _list])


bi_biz = BIBusiness()
