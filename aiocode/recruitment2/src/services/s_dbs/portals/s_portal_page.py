# coding: utf-8
from sqlalchemy import select, and_, join, func

from constants import RecruitmentPageStatus, EmpQrCodeType, JobPositionStatus
from drivers.mysql import db
from models.m_job_position import tb_job_position
from models.m_portals import tb_recruitment_portal_record
from models.m_portals import tb_recruit_portal_position
from models.m_portals import tb_referee_config
from models.m_portals import tb_share_position_qr_code
from utils.sa_db import db_executor
from utils.sa_db import Paginator
from utils.strutils import uuid2str
from utils.table_util import TableUtil


tb_recruitment_portal_record_tbu = TableUtil(tb_recruitment_portal_record)


class PortalPageService(object):
    """
    招聘网页服务类
    """
    async def is_used_intro(self, company_id: str, intro_id: str):
        """
        @desc 是否有使用企业介绍的门户网页
        """
        stmt = select([
            func.count(tb_recruitment_portal_record.c.id).label("count")
        ]).where(
            and_(
                tb_recruitment_portal_record.c.company_id == uuid2str(company_id),
                tb_recruitment_portal_record.c.company_introduction_id == intro_id,
                tb_recruitment_portal_record.c.is_delete == 0
            )
        )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, stmt)
        return result.get("count")

    @classmethod
    async def get_portal_page(cls, company_id: str, ids: list = None, fields: list = None) -> list:
        """
        获取招聘渠道 如果ids不存在返回企业所有数据
        """
        _keys = tb_recruitment_portal_record_tbu.filter_keys(fields)
        exp = select(
            [tb_recruitment_portal_record.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == company_id
            )
        )
        if ids:
            exp = exp.where(tb_recruitment_portal_record.c.id.in_(ids))

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def find_by_company(cls, company_id: str, fields: list) -> list:
        """
        查询企业招聘门户网页
        @param company_id:
        @param fields:
        @return:
        """
        stmt = select(
            [
                tb_recruitment_portal_record.c.get(field).label(field) for field in fields
            ]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == uuid2str(company_id),
                tb_recruitment_portal_record.c.is_valid == 1,
                tb_recruitment_portal_record.c.is_delete == 0,
                tb_recruitment_portal_record.c.status == RecruitmentPageStatus.on_line
            )
        )
        engine = await db.default_db
        data_list = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in data_list]

    async def page_detail(self, company_id: str, page_id: str, fields: list):
        """
        根据网页id获取门户详情
        @param company_id:
        @param page_id:
        @param fields:
        @return:
        """
        stmt = select(
            [
                tb_recruitment_portal_record.c.get(field).label(field) for field in fields
            ]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == uuid2str(company_id),
                tb_recruitment_portal_record.c.id == uuid2str(page_id)
            )
        )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, stmt)
        return result

    async def page_detail_by_id(self, page_id: str, fields: list):
        """
        根据网页id获取门户详情
        @param page_id:
        @param fields:
        @return:
        """
        stmt = select(
            [
                tb_recruitment_portal_record.c.get(field).label(field) for field in fields
            ]
        ).where(
            and_(
                tb_recruitment_portal_record.c.id == uuid2str(page_id)
            )
        )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, stmt)
        return result

    @classmethod
    async def get_pages_by_ids(cls, company_id: str, page_ids: list, fields: list):
        """
        根据ids获取网页信息
        @param company_id:
        @param page_ids:
        @param fields:
        @return:
        """
        page_ids = [uuid2str(page_id) for page_id in page_ids]
        stmt = select(
            [
                tb_recruitment_portal_record.c.get(field).label(field) for field in fields
            ]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == uuid2str(company_id),
                tb_recruitment_portal_record.c.id.in_(page_ids)
            )
        )
        engine = await db.default_db
        result = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in result]

    @classmethod
    async def get_page_by_id(cls, page_id: str, fields: list):
        """
        根据网页id获取门户详情
        @param page_id:
        @param fields:
        @return:
        """
        stmt = select(
            [
                tb_recruitment_portal_record.c.get(field).label(field) for field in fields
            ]
        ).where(
            and_(
                tb_recruitment_portal_record.c.id == uuid2str(page_id)
            )
        )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, stmt)
        return result


portal_position_tbu = TableUtil(tb_recruit_portal_position)


class PortalPositionsService(object):
    """
    网页职位服务类
    """
    @staticmethod
    def _handle_query_params(stmt, query_params: dict):
        """
        @desc 过滤
        """
        job_name = query_params.get("job_name")
        if job_name:
            stmt = stmt.where(
                tb_recruit_portal_position.c.name.like(f'%{job_name}%')
            )
        secondary_cate = query_params.get("secondary_cate")
        if secondary_cate:
            stmt = stmt.where(
                tb_recruit_portal_position.c.secondary_cate == secondary_cate
            )
        dep_ids = query_params.get("dep_ids", [])
        if dep_ids:
            stmt = stmt.where(
                tb_recruit_portal_position.c.dep_id.in_(dep_ids)
            )

        province_id = query_params.get("province_id")
        if province_id:
            stmt = stmt.where(
                tb_recruit_portal_position.c.province_id == province_id
            )

        has_bonus = query_params.get("has_bonus")
        if has_bonus is not None:
            if has_bonus:
                stmt = stmt.where(
                    tb_job_position.c.referral_bonus != ""
                )
            else:
                stmt = stmt.where(
                    tb_job_position.c.referral_bonus == ""
                )

        city_id = query_params.get("city_id")
        if city_id:
            stmt = stmt.where(
                tb_recruit_portal_position.c.city_id == city_id
            )

        town_id = query_params.get("town_id")
        if town_id:
            stmt = stmt.where(
                tb_recruit_portal_position.c.town_id == town_id
            )

        work_type = query_params.get("work_type")
        if work_type is not None:
            stmt = stmt.where(
                tb_recruit_portal_position.c.work_type == work_type
            )

        return stmt

    @classmethod
    def _get_search_stmt(
            cls, company_id: str, portal_page_id: str, fields: list, position_fields: list, query: dict = None
    ):
        query = query or {}

        tbs = join(
            tb_recruit_portal_position, tb_job_position,
            tb_job_position.c.id == tb_recruit_portal_position.c.job_position_id
        )
        s_fields = [tb_job_position.c.get(field).label(field) for field in position_fields]
        s_fields.extend([tb_recruit_portal_position.c.get(field).label(field) for field in fields])

        stmt = select(s_fields).where(
            and_(
                tb_recruit_portal_position.c.company_id == uuid2str(company_id),
                tb_recruit_portal_position.c.recruitment_page_id == uuid2str(portal_page_id),
                tb_recruit_portal_position.c.is_delete == 0,
                tb_job_position.c.status == JobPositionStatus.START
            )
        ).order_by(tb_recruit_portal_position.c.sort).select_from(tbs)

        stmt = cls._handle_query_params(stmt, query)
        return stmt

    @classmethod
    async def get_portal_positions(
            cls, company_id: str, portal_page_id: str, fields: list, position_fields: list, query: dict = None
    ):
        """
        获取内推网页的招聘职位
        @param company_id:
        @param portal_page_id: 内推网页id
        @param fields: 网页职位字段
        @param position_fields: 职位字段
        @param query: 查询条件
        """
        stmt = cls._get_search_stmt(company_id, portal_page_id, fields, position_fields, query)
        engine = await db.default_db
        data_list = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in data_list]

    @classmethod
    async def get_portal_positions_by_paging(
            cls, company_id: str, portal_page_id: str, fields: list,
            position_fields: list, p: int, limit: int, query: dict = None
    ):
        """
        @desc 分页获取内推职位列表
        """
        stmt = cls._get_search_stmt(company_id, portal_page_id, fields, position_fields, query)
        engine = await db.default_db
        paginator = Paginator(engine, stmt, p, limit)
        ret = await paginator.data()
        return ret

    @classmethod
    async def get_positions_by_page_id(cls, company_id: str, page_id: str, fields: list = None) -> list:
        """
        查询招聘网页职位信息
        """
        fields = portal_position_tbu.filter_keys(fields)
        exp = select(
            [tb_recruit_portal_position.c[key].label(key) for key in fields]
        ).where(
            and_(
                tb_recruit_portal_position.c.company_id == company_id,
                tb_recruit_portal_position.c.is_delete == 0,
                tb_recruit_portal_position.c.recruitment_page_id == page_id
            )
        )

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_portal_positions_by_ids(
            cls, company_id: str, record_ids: list, fields: list, job_position_ids: list = None,
            need_join: bool = False, position_fields: list = None
    ):
        """
        根据门户职位IDs获取门户职位
        @param company_id:
        @param record_ids:
        @param fields:
        @param job_position_ids:
        @param need_join:
        @param position_fields:
        @return:
        """
        record_ids = [uuid2str(record_id) for record_id in record_ids]
        fields = [tb_recruit_portal_position.c.get(field).label(field) for field in fields]
        if need_join:
            fields.extend([tb_job_position.c.get(field).label(field) for field in position_fields])

        stmt = select(fields).where(
            and_(
                tb_recruit_portal_position.c.company_id == uuid2str(company_id),
                tb_recruit_portal_position.c.id.in_(record_ids)
            )
        )
        if job_position_ids is not None:
            stmt = stmt.where(tb_recruit_portal_position.c.job_position_id.in_(job_position_ids))

        if need_join:
            tbs = join(
                tb_recruit_portal_position, tb_job_position,
                tb_job_position.c.id == tb_recruit_portal_position.c.job_position_id
            )
            stmt = stmt.select_from(tbs).order_by(tb_job_position.c.status.asc())
        engine = await db.default_db
        data = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in data] if data else []

    async def get_position_qrcode(self, company_id: str, refer_id: str, position_id: str):
        """
        @desc 获取网页职位分享小程序码
        """
        stmt = select([
            tb_share_position_qr_code.c.qrcode_url.label("qrcode_url")
        ]).where(
            and_(
                tb_share_position_qr_code.c.company_id == uuid2str(company_id),
                tb_share_position_qr_code.c.refer_id == uuid2str(refer_id),
                tb_share_position_qr_code.c.position_record_id == uuid2str(position_id),
            )
        )

        engine = await db.default_db
        data = await db_executor.fetch_one_data(engine, stmt)
        return data.get('qrcode_url', '')

    async def create_position_qrcode(self, company_id: str, refer_id: str, position_id, qrcode_url: str):
        """
        @desc 创建网页职位分享小程序码
        """
        data = {
            "company_id": uuid2str(company_id),
            "refer_id": uuid2str(refer_id),
            "position_record_id": uuid2str(position_id),
            "qrcode_url": qrcode_url
        }
        engine = await db.default_db
        result = await db_executor.single_create(engine, tb_share_position_qr_code, data)

        return result

    @classmethod
    async def get_portal_position_by_id(
            cls, company_id: str, pk: str, fields: list = None
    ) -> dict:
        """查询招聘门户关联职位"""
        query_keys = portal_position_tbu.tb_keys
        if fields:
            query_keys = [field for field in fields if field in query_keys]

        exp = select(
            [tb_recruit_portal_position.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_recruit_portal_position.c.company_id == company_id,
                tb_recruit_portal_position.c.id == pk,
                tb_recruit_portal_position.c.is_delete == 0
            )
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def get_portal_position_by_id_only(cls, pk: str, fields: list = None) -> dict:
        """
        @param pk:
        @param fields:
        @return:
        """
        query_keys = portal_position_tbu.tb_keys
        if fields:
            query_keys = [field for field in fields if field in query_keys]

        exp = select(
            [tb_recruit_portal_position.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_recruit_portal_position.c.id == pk,
                tb_recruit_portal_position.c.is_delete == 0
            )
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def update_portal_position_bonus(cls, company_id: str, user_id: str, position_ids: list, referral_bonus: str):
        _where = and_(
            tb_recruit_portal_position.c.company_id == company_id,
            tb_recruit_portal_position.c.job_position_id.in_(position_ids)
        )
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_recruit_portal_position, where_stmt=_where,
            values={"referral_bonus": referral_bonus, "update_by_id": user_id}
        )


class ReferralEmployeeService(object):
    """
    @desc 内推人服务
    """
    async def get_employee(self, company_id: str, employee_id: str):
        """
        @desc 获取内推人信息
        """
        stmt = select([
            tb_referee_config.c.id.label("id"),
            tb_referee_config.c.employee_id.label("employee_id"),
            tb_referee_config.c.qrcode_type.label("qrcode_type"),
            tb_referee_config.c.qrcode_url.label("qrcode_url")
        ]).where(
            and_(
                tb_referee_config.c.company_id == uuid2str(company_id),
                tb_referee_config.c.employee_id == uuid2str(employee_id)
            )
        )

        engine = await db.default_db
        data = await db_executor.fetch_one_data(engine, stmt)

        default_data = {
            "id": "",
            "employee_id": employee_id,
            "qrcode_type": EmpQrCodeType.UseHr,
            "qrcode_url": ""
        }
        default_data.update(data)
        return default_data

    async def create_employee(self, company_id: str, employee_data: dict):
        """
        @desc 添加内推人
        """
        employee_data.update(
            {
                "company_id": uuid2str(company_id)
            }
        )
        engine = await db.default_db
        result = await db_executor.single_create(engine, tb_referee_config, employee_data)

        return result

    async def update_employee(self, company_id: str, employee_data: dict):
        """
        @desc 添加内推人
        """
        employee_id = employee_data.get("employee_id")
        where_stmt = and_(
            tb_referee_config.c.company_id == uuid2str(company_id),
            tb_referee_config.c.employee_id == uuid2str(employee_id)
        )
        engine = await db.default_db
        res = await db_executor.update_data(
            engine, tb_referee_config, employee_data, where_stmt
        )

        return res
