from drivers.mysql import db
from models.m_data_report import tb_data_report
from utils.sa_db import db_executor
from utils.strutils import uuid2str


class DataReportService:

    @staticmethod
    async def insert_data(
            task_id: str,
            company_id: str, user_id: str,
            data: dict,
            ev_scene: int,
            ev_code: int,
            status,
            exec_msg: str = ""):

        engine = await db.default_db
        await db_executor.single_create(engine, tb_data_report, {
            "id": task_id,
            "company_id": company_id,
            "add_by_id": uuid2str(user_id),
            "ev_scene": ev_scene,
            "ev_data": data,
            "ev_code": ev_code,
            "status": status,
            "exec_msg": exec_msg
        })




