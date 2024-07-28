from business.commons.data_report.b_data_report import DataReportBase
from constants import EventScene
from models.m_job_position import tb_job_position
from services import svc
from services.s_dbs.s_job_position import PositionParticipantService, JobPositionSelectService
from utils.strutils import uuid2str
from utils.timeutils import to_string


class JobPositionReport(DataReportBase):

    ev_scene = EventScene.SR

    dt_fmt = "%Y-%m-%d %H:%M:%S"

    table_cls = tb_job_position

    async def get_ev_data(self, company_id: str, ids: list, **kwargs) -> list:
        query_fields = self.get_model_fields()

        data = await svc.job_position_search.get_positions_by_ids(
            company_id=company_id, ids=ids, fields=query_fields
        )

        # 获取 hr_participant_ids, emp_participant_ids
        participants = await PositionParticipantService.get_participants_by_position_ids(
            job_position_ids=[d["id"] for d in data], fields=["id", "participant_type", "participant_refer_id"]
        )
        for d in data:
            _filter = list(filter(lambda x: x["job_position_id"] == d["id"], participants))
            d["hr_participant_ids"] = [p["participant_refer_id"] for p in _filter if p["participant_type"] == 1]
            d["emp_participant_ids"] = [p["participant_refer_id"] for p in _filter if p["participant_type"] == 2]
        return data


class AddJobPositionReportBiz(JobPositionReport):
    """
    添加招聘需求  数据上报
    """

    fields_map = {
        "id": "job_position_id",
        "job_title_id": "job_title_id",
        "dep_id": "dep_id",
        "work_type": "work_type",
        "work_place_id": "work_place_id",
        "province_id": "province_id",
        "city_id": "city_id",
        "town_id": "town_id",
        "position_total": "position_total",
        "reason": "reason",
        "latest_entry_date": "latest_entry_date",  # date 2021/2/28
        "emergency_level": "emergency_level",
        "secret_position": "secret_position",  # bool
        "hr_participant_ids": "hr_participant_ids",  # []
        "emp_participant_ids": "emp_participant_ids",  # []
        "add_by_id": "add_by_id",
        "add_dt": "add_dt",  # 2021/2/28
        "start_dt": "start_dt",  # 2021/2/28
    }

    ev_code = "RE00100"

    async def handle_row(self, company_id: str, row: dict) -> dict:

        row["id"] = uuid2str(row.get("id"))
        row["job_title_id"] = uuid2str(row.get("job_title_id"))
        row["work_place_id"] = uuid2str(row.get("work_place_id"))
        row["secret_position"] = bool(row.get("secret_position"))
        row["hr_participant_ids"] = [uuid2str(r) for r in row.get("hr_participant_ids", [])]
        row["emp_participant_ids"] = [uuid2str(r) for r in row.get('emp_participant_ids', [])]
        row["add_by_id"] = uuid2str(row.get("add_by_id"))
        row["dep_id"] = uuid2str(row.get("dep_id")) or ""

        if row.get("latest_entry_date"):
            row["latest_entry_date"] = to_string(row["latest_entry_date"], self.dt_fmt)

        if row.get("add_dt"):
            row["add_dt"] = to_string(row["add_dt"], self.dt_fmt)

        row["start_dt"] = to_string(row["start_dt"]) if row.get("start_dt") else None
        return row


class UpdateJobPositionReportBiz(JobPositionReport):
    """
    修改招聘需求 数据上报
    """
    fields_map = {
        "id": "job_position_id",
        "job_title_id": "job_title_id",
        "dep_id": "dep_id",
        "work_type": "work_type",
        "work_place_id": "work_place_id",
        "province_id": "province_id",
        "city_id": "city_id",
        "town_id": "town_id",
        "position_total": "position_total",
        "reason": "reason",
        "latest_entry_date": "latest_entry_date",  # date 2021/2/28
        "emergency_level": "emergency_level",
        "secret_position": "secret_position",  # bool
        "hr_participant_ids": "hr_participant_ids",   # []
        "emp_participant_ids": "emp_participant_ids",   # []
        "start_dt": "start_dt",  # 2021/2/28
        "update_by_id": "update_by_id",
        "update_dt": "update_dt"  # datetime
    }

    ev_code = "RE00102"

    async def handle_row(self, company_id: str, row: dict) -> dict:

        row["id"] = uuid2str(row.get("id"))
        row["job_title_id"] = uuid2str(row.get("job_title_id"))
        row["work_place_id"] = uuid2str(row.get("work_place_id"))
        row["secret_position"] = bool(row.get("secret_position"))
        row["hr_participant_ids"] = [uuid2str(r) for r in row.get("hr_participant_ids", [])]
        row["emp_participant_ids"] = [uuid2str(r) for r in row.get('emp_participant_ids', [])]
        row["update_by_id"] = uuid2str(row.get("update_by_id"))
        row["dep_id"] = uuid2str(row.get("dep_id")) or ""
        row["start_dt"] = to_string(row["start_dt"]) if row.get("start_dt") else None

        if row.get("latest_entry_date"):
            row["latest_entry_date"] = to_string(row["latest_entry_date"], self.dt_fmt)

        if row.get("update_dt"):
            row["update_dt"] = to_string(row["update_dt"], self.dt_fmt)

        return row

