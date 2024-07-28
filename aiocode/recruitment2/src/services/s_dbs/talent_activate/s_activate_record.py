from datetime import datetime, timedelta

import sqlalchemy as sa
import ujson
from sqlalchemy import join, and_

from constants import TalentActivateStatus
from drivers.mysql import db
from models.m_candidate_record import tb_candidate_record
from models.m_talent_activate import tb_talent_activate_record
from utils.sa_db import db_executor, Paginator
from utils.strutils import uuid2str, gen_uuid
from utils.time_cal import get_date_min_datetime, get_date_max_datetime


class ActivateRecordService(object):

    @classmethod
    async def create_records(
            cls, company_id: str, user_id: str, task_id: str, candidates_ids: list, validated_data: dict
    ) -> dict:
        """

        @param company_id:
        @param user_id:
        @param task_id:
        @param candidates_ids:
        @param validated_data:
        @return:
        """
        values = []
        candidate_id2activate_id = {}
        portal_page_id = uuid2str(validated_data.get("portal_page_id")) or ""
        activate_status = TalentActivateStatus.Doing if portal_page_id else TalentActivateStatus.Null
        for candidate_id in candidates_ids:
            _id = gen_uuid()
            data = {
                "id": _id,
                "task_id": uuid2str(task_id),
                "company_id": uuid2str(company_id),
                "add_by_id": uuid2str(user_id),
                "candidate_id": uuid2str(candidate_id),
                "activate_status": activate_status,
                "sms_template_id": uuid2str(validated_data.get("sms_template_id")),
                "email_template_id": uuid2str(validated_data.get("email_template_id")),
                "portal_page_id": portal_page_id,
                "page_position_id": uuid2str(validated_data.get("page_position_id")) or "",
                "notify_way": validated_data.get("notify_way"),
                "send_email_id": uuid2str(validated_data.get("send_email_id")) or ""
            }
            values.append(data)
            candidate_id2activate_id[candidate_id] = _id
        await db_executor.batch_create(db.default, tb_talent_activate_record, values)

        return candidate_id2activate_id

    @staticmethod
    def _filter_stmt(stmt, query_params):
        conditions = []
        candidate_status = query_params.get("candidate_status")
        if candidate_status:
            conditions.append(tb_candidate_record.c.status.in_(candidate_status))
        activate_status = query_params.get("activate_status")
        if activate_status is not None:
            conditions.append(
                tb_talent_activate_record.c.activate_status == int(activate_status)
            )
        candidate_ids = query_params.get("candidate_ids")
        if candidate_ids:
            conditions.append(
                tb_talent_activate_record.c.candidate_id.in_(candidate_ids)
            )
        start_dt = query_params.get("start_dt")
        if start_dt:
            start_dt = get_date_min_datetime(start_dt)
            conditions.append(
                tb_talent_activate_record.c.add_dt >= start_dt
            )
        end_dt = query_params.get("end_dt")
        if end_dt:
            end_dt = get_date_max_datetime(end_dt)
            conditions.append(tb_talent_activate_record.c.add_dt <= end_dt)
        add_by_ids = query_params.get("add_by_ids")
        if add_by_ids:
            add_by_ids = [uuid2str(_id) for _id in add_by_ids]
            conditions.append(tb_talent_activate_record.c.add_by_id.in_(add_by_ids))
        portal_page_id = query_params.get("portal_page_id")
        if portal_page_id:
            conditions.append(
                tb_talent_activate_record.c.portal_page_id == uuid2str(portal_page_id)
            )
        if conditions:
            stmt = stmt.where(and_(*conditions))

        return stmt

    @classmethod
    async def record_list_with_page(cls, company_id: str, query_params: dict, fields: list):
        """
        获取激活记录列表
        @param company_id:
        @param query_params:
        @param fields:
        @return:
        """
        outer_join = join(
            tb_talent_activate_record, tb_candidate_record,
            tb_talent_activate_record.c.candidate_record_id == tb_candidate_record.c.id,
            isouter=True
        )
        select_fields = [tb_talent_activate_record.c.get(field).label(field) for field in fields]
        select_fields.extend(
            [
                tb_candidate_record.c.status.label("candidate_status"),
                tb_candidate_record.c.add_dt.label("delivery_dt")
            ]
        )
        stmt = sa.select(select_fields).where(
            tb_talent_activate_record.c.company_id == uuid2str(company_id)
        ).select_from(outer_join).order_by(tb_talent_activate_record.c.add_dt.desc())
        stmt = cls._filter_stmt(stmt, query_params)
        paginator = Paginator(
            db.default, stmt, query_params.get("p") or 1, query_params.get("limit") or 10
        )
        return await paginator.data()

    @classmethod
    async def record_list_without_page(cls, company_id: str, fields: list):
        """
        获取激活记录列表
        @param company_id:
        @param fields:
        @return:
        """
        select_fields = [tb_talent_activate_record.c.get(field).label(field) for field in fields]
        stmt = sa.select(select_fields).where(
            tb_talent_activate_record.c.company_id == uuid2str(company_id)
        ).order_by(tb_talent_activate_record.c.add_dt.desc())
        items = await db_executor.fetch_all_data(db.default, stmt)

        return [dict(item) for item in items]

    @classmethod
    async def candidate_activate_records(
            cls, company_id: str, candidate_id: str, fields: list, params: dict
    ):
        """
        候选人激活记录
        @param company_id:
        @param candidate_id:
        @param fields:
        @param params:
        @return:
        """
        stmt = sa.select(
            [tb_talent_activate_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_talent_activate_record.c.company_id == uuid2str(company_id),
                tb_talent_activate_record.c.candidate_id == uuid2str(candidate_id)
            )
        )
        start_dt = params.get("start_dt")
        if start_dt:
            start_dt = get_date_min_datetime(start_dt)
            stmt = stmt.where(tb_talent_activate_record.c.add_dt >= start_dt)

        items = await db_executor.fetch_all_data(db.default, stmt)
        return [dict(item) for item in items]

    @classmethod
    async def update_view_status(cls, company_id: str, record_id: str):
        """
        更新激活记录访问状态
        @param company_id:
        @param record_id:
        @return:
        """
        where_stmt = and_(
            tb_talent_activate_record.c.company_id == uuid2str(company_id),
            tb_talent_activate_record.c.id == uuid2str(record_id)
        )
        update_values = {"is_read": 1, "latest_read_dt": datetime.now()}
        await db_executor.update_data(
            db.default, tb_talent_activate_record, update_values, where_stmt
        )

    @classmethod
    async def get_activate_record_by(cls, company_id: str, _id: str, fields: list):
        """
        获取激活记录
        @param company_id:
        @param _id:
        @param fields:
        @return:
        """
        stmt = sa.select(
            [tb_talent_activate_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_talent_activate_record.c.company_id == uuid2str(company_id),
                tb_talent_activate_record.c.id == uuid2str(_id)
            )
        )
        return await db_executor.fetch_one_data(db.default, stmt)

    @classmethod
    async def update_activate_status(
            cls, company_id: str, record_id: str, user_id: str,
            activate_status: int = TalentActivateStatus.Success,
            candidate_record_id: str = ""
    ):
        """
        更新激活记录激活状态
        @param company_id:
        @param record_id:
        @param user_id:
        @param activate_status:
        @param candidate_record_id:
        @return:
        """
        where_stmt = and_(
            tb_talent_activate_record.c.company_id == uuid2str(company_id),
            tb_talent_activate_record.c.id == uuid2str(record_id)
        )
        update_values = {
            "activate_status": activate_status, "update_by_id": user_id, "update_dt": datetime.now()
        }
        if candidate_record_id:
            update_values.update(
                {
                    "candidate_record_id": candidate_record_id
                }
            )
        await db_executor.update_data(
            db.default, tb_talent_activate_record, update_values, where_stmt
        )

    @classmethod
    async def update_activate_status_by_timer(cls):
        """
        定时激活应聘记录的状态
        @return:
        """
        add_dt_deadline = datetime.now() - timedelta(days=30)
        where_stmt = and_(
            tb_talent_activate_record.c.activate_status == TalentActivateStatus.Doing,
            tb_talent_activate_record.c.add_dt <= add_dt_deadline
        )
        update_values = {
            "activate_status": TalentActivateStatus.Failed, "update_dt": datetime.now()
        }
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_talent_activate_record, update_values, where_stmt
        )

    @classmethod
    async def fill_sms_content(cls, record_id: str, content: str):
        where_stmt = tb_talent_activate_record.c.id == record_id
        update_values = {
            "sms_content": content
        }
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_talent_activate_record, update_values, where_stmt
        )

    @classmethod
    async def fill_notify_result(cls, record_id: str, callback_data: dict, notify_type: int):
        """
        更新通知状态回调
        @param record_id:
        @param callback_data:
        @param notify_type: 1-短信 2邮件
        @return:
        """
        callback_data = callback_data or {}
        where_stmt = tb_talent_activate_record.c.id == record_id
        update_values = {
            "sms_response": ujson.dumps(callback_data)
        }
        if notify_type == 2:
            update_values = {
                "email_response": ujson.dumps(callback_data)
            }
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_talent_activate_record, update_values, where_stmt
        )
