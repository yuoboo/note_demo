# coding=utf-8
import asyncio
from collections import defaultdict
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import select, and_, join

from constants import ParticipantType
from drivers.mysql import db
from models.m_job_position import tb_job_position_type, tb_job_position, tb_job_position_participant_rel
from models.m_recruitment_team import tb_participant
from utils.sa_db import db_executor, Paginator
from utils.strutils import uuid2str
from utils.table_util import TableUtil

job_position_tbu = TableUtil(tb_job_position)


class JobPositionSelectService(object):
    """
    招聘职位查询服务类
    """

    @classmethod
    async def get_job_position_type_map(cls, reverse_key=False):
        exp = sa.select([
            tb_job_position_type.c.id.label('id'),
            tb_job_position_type.c.name.label('name'),
            tb_job_position_type.c.level.label('level'),
            tb_job_position_type.c.order.label('order'),
            tb_job_position_type.c.parent_id.label('parent_id'),
        ]).order_by(tb_job_position_type.c.level, tb_job_position_type.c.order)

        engine = await db.default_db
        rows = await db_executor.fetch_all_data(engine, exp)

        ret = dict()
        for _type in rows:
            _id = _type['id']
            if _type['parent_id']:
                _parent_name = ret.get(uuid2str(_type['parent_id']), '')
                ret[_id] = '{} / {}'.format(_parent_name, _type['name']) if _parent_name else _type['name']
            else:
                ret[uuid2str(_type['id'])] = _type['name']

        if reverse_key:
            ret = dict(zip(ret.values(), ret.keys()))

        return ret

    @classmethod
    async def get_position_type_referral_map(cls):
        """
        内推职位列表筛选只需要显示第二级， 这里需要将第三级处理成对应的第二级
        :return:
        """
        query = sa.select([
            tb_job_position_type.c.id.label("id"),
            tb_job_position_type.c.name.label("name"),
            tb_job_position_type.c.level.label("level"),
            tb_job_position_type.c.order.label("order"),
            tb_job_position_type.c.parent_id.label("parent_id")
        ]).order_by(
            tb_job_position_type.c.level, tb_job_position_type.c.order
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, query)

        ret = dict()
        for item in items:
            _dict = dict(item)
            _id = uuid2str(_dict["id"])
            if _dict["level"] == 2:
                ret[_id] = _dict
            elif _dict["level"] == 3:
                p_id = uuid2str(_dict["parent_id"])
                ret[_id] = ret.get(p_id)
        return ret

    @classmethod
    async def get_position_type_second_map(cls):
        """获取第二级类别的映射"""
        exp = sa.select([
            tb_job_position_type.c.id.label("id"),
            tb_job_position_type.c.name.label("name")
        ]).where(
            tb_job_position_type.c.level == 2
        ).order_by(
            tb_job_position_type.c.level, tb_job_position_type.c.order
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)

        return {item.name: item.id for item in items}

    @classmethod
    async def valid_position_ids(cls, company_id: str, job_position_ids: list) -> list:
        company_id = uuid2str(company_id)
        job_position_ids = [uuid2str(p_id) for p_id in job_position_ids]
        stmt = sa.select([tb_job_position.c.id]).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.id.in_(job_position_ids)
            )
        )
        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        return [item.c_id for item in result_list]

    @classmethod
    async def get_referral_position_by_filter(
            cls, company_id: str, ids: list = None, dep_ids: list = None,
            fields: list = None) -> list:
        """根据条件过滤内推职位信息"""
        query_keys = job_position_tbu.filter_keys(fields)

        exp = select(
            [tb_job_position.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.is_delete == 0
            )
        )
        if ids:
            exp = exp.where(tb_job_position.c.id.in_(ids))
        if dep_ids:
            exp = exp.where(tb_job_position.c.dep_id.in_(dep_ids))

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, exp)

        return [dict(r) for r in res]

    @classmethod
    async def get_position_by_ids(cls, company_id: str, ids: list) -> dict:
        """
        根据职位Ids获取职位信息
        """
        company_id = uuid2str(company_id)
        engine = await db.default_db
        stmt = sa.select(
            [
                tb_job_position.c.id.label("id"),
                tb_job_position.c.name.label("name"),
                tb_job_position.c.dep_name.label("dep_name")
            ]
        ).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.id.in_(ids)
            )
        )
        result_list = await db_executor.fetch_all_data(engine, stmt)
        id2info = {}
        for item in result_list:
            id2info[item.id] = {
                "id": item.id,
                "name": item.name,
                "dep_name": item.dep_name
            }

        return id2info

    @staticmethod
    def _get_select_stmt(company_id: str, fields: list = None, query_params: dict = None):
        """
        获取查询sql表达式
        @return:
        """
        query_params = query_params or {}
        fields = job_position_tbu.filter_keys(fields)
        exp = select(
            [tb_job_position.c[key].label(key) for key in fields]
        ).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.is_delete == 0
            )
        )
        ids = query_params.get("ids")
        if ids:
            exp = exp.where(tb_job_position.c.id.in_(ids))
        status = query_params.get("status")
        if status:
            exp = exp.where(tb_job_position.c.status == status)
        keyword = query_params.get("keyword")
        if keyword:
            exp = exp.where(tb_job_position.c.name.like(f'%{keyword}%'))

        return exp

    @classmethod
    async def get_positions_by_ids(
            cls, company_id: str, ids: list = None, fields: list = None, query_params: dict = None
    ):
        query_params = query_params or {}
        query_params["ids"] = ids
        stmt = cls._get_select_stmt(company_id, fields, query_params)
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in items]

    @classmethod
    async def get_positions_with_paging(
            cls, company_id: str, fields: list = None, query_params: dict = None
    ):
        stmt = cls._get_select_stmt(company_id, fields, query_params)
        p = query_params.get("p", 1)
        limit = query_params.get("limit", 20)
        engine = await db.default_db
        paginator = Paginator(engine, stmt, p, limit)
        data = await paginator.data()
        return data

    @classmethod
    async def get_position_by_ids_cache(cls, company_id: str, ids: list) -> dict:
        """
        根据职位Ids获取职位信息
        """
        company_id = uuid2str(company_id)
        engine = await db.default_db
        stmt = select([tb_job_position.c.get(field).label(field) for field in tb_job_position.c.keys()]).where(
            and_(
                tb_job_position.c.is_delete == 0,
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.id.in_(ids)
            )
        )
        result_list = await db_executor.fetch_all_data(engine, stmt)
        id2info = {}
        for item in result_list:
            id2info[item.id] = dict(item)
        return id2info

    @staticmethod
    def _handle_query_params(stmt, query_params: dict):
        # 管理范围过滤
        permission_ids = query_params.get("permission_ids", [])
        if permission_ids:
            stmt = stmt.where(
                tb_job_position.c.id.in_(permission_ids)
            )
        keyword = query_params.get("keyword")
        if keyword is not None:
            stmt = stmt.where(
                tb_job_position.c.name.like(f'%{keyword}%')
            )
        dep_ids = query_params.get("dep_ids", [])
        if dep_ids:
            stmt = stmt.where(
                tb_job_position.c.dep_id.in_(dep_ids)
            )
        status = query_params.get('status')
        if status is not None:
            stmt = stmt.where(
                tb_job_position.c.status == status
            )
        province_id = query_params.get("province_id")
        if province_id:
            stmt = stmt.where(
                tb_job_position.c.province_id == province_id
            )
        city_id = query_params.get("city_id")
        if city_id:
            stmt = stmt.where(
                tb_job_position.c.city_id == city_id
            )
        work_type = query_params.get("work_type", None)
        if work_type is not None:
            stmt = stmt.where(
                tb_job_position.c.work_type == work_type
            )
        position_ids = query_params.get("position_ids")
        if position_ids is not None:
            stmt = stmt.where(
                tb_job_position.c.id.in_(position_ids)
            )
        clear_total = query_params.get("clear_total")
        if clear_total is not None:
            stmt = stmt.where(
                tb_job_position.c.position_total > 0
            )
        is_delete = query_params.get("is_delete")
        if is_delete is not None:
            stmt = stmt.where(
                tb_job_position.c.is_delete == is_delete
            )
        # 是否有内推奖励
        is_referral_bonus = query_params.get('is_referral_bonus')
        if is_referral_bonus is not None:
            if is_referral_bonus == 1:
                stmt = stmt.where(
                    tb_job_position.c.referral_bonus != ''
                )
            else:
                stmt = stmt.where(
                    tb_job_position.c.referral_bonus == ''
                )

        return stmt

    @classmethod
    async def search_positions(cls, company_id: str, fields: list, query_params: dict):
        """
        获取指定条件的职位信息，如果需要根据管理范围过滤，
        请传permission_ids字段-管理范围内的职位ids.
        """
        company_id = uuid2str(company_id)
        query = sa.select([
            tb_job_position.c.get(field).label(field) for field in fields
        ]).where(
            and_(
                tb_job_position.c.is_delete == 0,
                tb_job_position.c.company_id == company_id,
            )
        ).order_by(
            # '-emergency_level', "-start_dt", 'name'
            tb_job_position.c.emergency_level.desc(),
            tb_job_position.c.start_dt.desc(),
            tb_job_position.c.name
        )

        query = cls._handle_query_params(query, query_params)

        engine = await db.default_db
        job_positions = await db_executor.fetch_all_data(engine, query)
        job_positions = [dict(item) for item in job_positions]

        return job_positions

    @classmethod
    async def search_positions_with_page(cls, company_id: str, page, fields: list, query_params: dict, limit: int = 10):
        """
        获取指定条件的职位信息，如果需要根据管理范围过滤，
        请传permission_ids字段-管理范围内的职位ids.
        """
        company_id = uuid2str(company_id)
        query = sa.select([
            tb_job_position.c.get(field).label(field) for field in fields
        ]).where(
            and_(
                tb_job_position.c.is_delete == 0,
                tb_job_position.c.company_id == company_id,
            )
        ).order_by(
            tb_job_position.c.status,
            tb_job_position.c.emergency_level.desc(),
            tb_job_position.c.start_dt.desc(),
            tb_job_position.c.name
        )

        query = cls._handle_query_params(query, query_params)

        engine = await db.default_db
        paginator = Paginator(engine, query, page, limit)
        job_positions = await paginator.data()

        return job_positions

    @classmethod
    async def query_position_total(cls, company_id: str, position_ids: list = None) -> list:
        """工作台统计计划招聘"""
        query = select([
            tb_job_position.c.id.label("job_position_id"),
            tb_job_position.c.position_total.label("position_total")
        ]).where(
            and_(
                tb_job_position.c.is_delete == 0,
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.status == 1
            )
        )
        if position_ids:
            query = query.where(
                tb_job_position.c.id.in_(position_ids)
            )

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine=engine, stmt=query)
        return [dict(r) for r in res]

    @classmethod
    async def get_job_positions_by_dep_ids(cls, company_id: str, dep_ids: list, fields: list) -> list:
        """
        根据部门id 获取招聘职位
        """
        fields = job_position_tbu.filter_keys(fields)
        exp = select(
            [tb_job_position.c[key].label(key) for key in fields]
        ).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.is_delete == 0,
                tb_job_position.c.dep_id.in_(dep_ids)
            )
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_job_positions_bys(cls, company_id: str, ids: list = None, fields: list = None) -> list:
        fields = job_position_tbu.filter_keys(fields)
        query = sa.select(
            [tb_job_position.c[field].label(field) for field in fields]
        ).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.is_delete == 0
            )
        )

        if ids:
            query = query.where(tb_job_position.c.id.in_(ids))

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, query)
        return [dict(item) for item in items]


class JobPositionUpdateService(object):
    """
    招聘职位更新服务类
    """

    @classmethod
    async def set_position_referral_bonus(
            cls, company_id: str, user_id: str, job_position_ids: list, referral_bonus: str
    ):
        """
        设置招聘职位内推奖金
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        job_position_ids = [uuid2str(p_id) for p_id in job_position_ids]
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                sa.update(tb_job_position).where(
                    and_(
                        tb_job_position.c.company_id == company_id,
                        tb_job_position.c.id.in_(job_position_ids)
                    )
                ).values(
                    update_by_id=user_id,
                    update_dt=datetime.now(),
                    referral_bonus=referral_bonus
                )
            )

    @classmethod
    async def delete_dep_info(cls, company_id: str, position_ids: list):
        """
        删除用人部门信息
        @param company_id:
        @param position_ids:
        @return:
        """
        position_ids = [uuid2str(_id) for _id in position_ids]
        where_stmt = and_(
            tb_job_position.c.company_id == uuid2str(company_id),
            tb_job_position.c.id.in_(position_ids)
        )
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_job_position, {"dep_id": None, "dep_name": None}, where_stmt
        )

    @classmethod
    async def update_dep_info(cls, company_id: str, dep_id: str, dep_name: str):
        where_stmt = and_(
            tb_job_position.c.company_id == uuid2str(company_id),
            tb_job_position.c.dep_id == uuid2str(dep_id)
        )
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_job_position, {"dep_name": dep_name}, where_stmt
        )

class JobPositionCreateService(object):
    """
    招聘职位创建服务类
    """
    pass


class JobPositionTypeService(object):

    @classmethod
    async def get_job_position_type_map(cls, reverse_key=False):
        """
        获取职位类型映射
        :returns dict {"uuid": "完成名称"}
        """

        engine = await db.default_db
        exp = select([
            tb_job_position_type.c.id.label('id'),
            tb_job_position_type.c.name.label('name'),
            tb_job_position_type.c.level.label('level'),
            tb_job_position_type.c.order.label('order'),
            tb_job_position_type.c.parent_id.label('parent_id'),
        ]).order_by(tb_job_position_type.c.level, tb_job_position_type.c.order)
        res = dict()
        async with engine.acquire() as conn:
            result = await conn.execute(exp)
            rows = await result.fetchall()
            for row in rows:
                _id = uuid2str(row["id"])
                if row["parent_id"]:
                    _parent_name = res.get(uuid2str(row["parent_id"]), "")
                    res[_id] = "{} / {}".format(_parent_name, row["name"]) if _parent_name else row["name"]
                else:
                    res[uuid2str(row["id"])] = row["name"]

        if reverse_key:
            res = dict(zip(res.values(), res.keys()))

        return res

    @classmethod
    async def get_job_position_type_ids_map(cls):
        """
        返回所有类型与子类型的映射字典
        :return: dict --> {"uuid": ["所有子类的id,包括子类的子类及自身"]}
        """
        engine = await db.default_db
        exp = select([
            tb_job_position_type.c.id.label('id'),
            tb_job_position_type.c.name.label('name'),
            tb_job_position_type.c.parent_id.label('parent_id'),
        ]).order_by(tb_job_position_type.c.level.desc(), tb_job_position_type.c.order.desc())
        res = defaultdict(list)

        async with engine.acquire() as conn:
            result = await conn.execute(exp)
            rows = await result.fetchall()
            for row in rows:
                _id = uuid2str(row["id"])
                _parent_id = uuid2str(row["parent_id"]) if row["parent_id"] else None

                if _id in res:
                    res[_id].append(_id)
                else:
                    res[_id] = [_id]

                if _parent_id:
                    res[_parent_id] += res[_id]

        return res

    @classmethod
    async def get_position_types(cls):
        """
        返回招聘职位类型树
        """
        exp = select([
            tb_job_position_type.c.id.label("id"),
            tb_job_position_type.c.name.label("name"),
            tb_job_position_type.c.level.label("level"),
            tb_job_position_type.c.parent_id.label("parent_id"),
        ]).order_by(
            tb_job_position_type.c.level,
            tb_job_position_type.c.order
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]


class PositionParticipantService(object):
    @classmethod
    async def get_position_ids_by_participants(cls, company_id: str, participant_ids: list, **kwargs):
        # TODO 需要给tb_tb_job_position_participant_rel表加上company_id
        participant_ids = [uuid2str(p_id) for p_id in participant_ids]
        stmt = select(
            [
                tb_job_position_participant_rel.c.job_position_id.label("job_position_id"),
                tb_job_position_participant_rel.c.participant_id.label("participant_id")
            ]
        ).where(
            and_(
                # tb_job_position_participant_rel.c.company_id == uuid2str(company_id),
                tb_job_position_participant_rel.c.participant_id.in_(participant_ids),
                tb_job_position_participant_rel.c.is_delete == 0
            )
        )
        position_ids = kwargs.get("position_id")
        if position_ids:
            stmt = stmt.where(tb_job_position_participant_rel.c.job_position_id.in_(position_ids))
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)
        p_id2position_ids = defaultdict(list)
        for item in res:
            p_id2position_ids.setdefault(item["participant_id"], []).append(item["job_position_id"])

        return p_id2position_ids

    @classmethod
    async def get_participant_by_position_ids(
            cls, job_position_ids: list, fields: list, participant_type: int = ParticipantType.HR
    ):
        tbs_1 = join(
            tb_job_position_participant_rel,
            tb_participant,
            tb_job_position_participant_rel.c.participant_id == tb_participant.c.id
        )

        columns = [tb_participant.c.get(field).label(field) for field in fields]
        columns.extend([tb_job_position_participant_rel.c.job_position_id.label('job_position_id')])
        stmt = sa.select(columns).where(
            and_(
                tb_job_position_participant_rel.c.job_position_id.in_(job_position_ids),
                tb_job_position_participant_rel.c.is_delete == 0,
                tb_participant.c.participant_type == participant_type
            )
        ).order_by(tb_job_position_participant_rel.c.add_dt).select_from(tbs_1)

        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        id2info = defaultdict(list)
        for item in result_list:
            id2info.setdefault(item["job_position_id"], []).append(dict(item))

        return id2info

    @classmethod
    async def get_participants_by_position_ids(cls, job_position_ids: list, fields: list) -> list:
        tbs_1 = join(
            tb_job_position_participant_rel,
            tb_participant,
            tb_job_position_participant_rel.c.participant_id == tb_participant.c.id
        )

        columns = [tb_participant.c.get(field).label(field) for field in fields]
        columns.extend([tb_job_position_participant_rel.c.job_position_id.label('job_position_id')])
        stmt = sa.select(columns).where(
            and_(
                tb_job_position_participant_rel.c.job_position_id.in_(job_position_ids),
                tb_job_position_participant_rel.c.is_delete == 0
            )
        ).order_by(tb_job_position_participant_rel.c.add_dt).select_from(tbs_1)

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in items]


if __name__ == "__main__":
    async def helper():
        res = await JobPositionSelectService.search_positions("b117d06d3c084c0e9e2970309c215d73", ["id", "name"], {})
        print(res)


    asyncio.run(helper())
