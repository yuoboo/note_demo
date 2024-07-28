# coding=utf-8
import asyncio

from sqlalchemy import select, and_

from drivers.mysql import db
from models.m_config import tb_recruitment_channel
from utils.sa_db import db_executor, Paginator
from utils.strutils import uuid2str
from utils.table_util import TableUtil


recruitment_channel_tbu = TableUtil(tb_recruitment_channel)


class RecruitmentChannelService(object):

    @classmethod
    async def get_channels(cls, company_id: str, ids: list = None, fields: list = None) -> list:
        """
        获取招聘渠道 如果ids不存在返回企业所有数据
        """
        _keys = recruitment_channel_tbu.filter_keys(fields)
        exp = select(
            [tb_recruitment_channel.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_channel.c.company_id == company_id,
                tb_recruitment_channel.c.is_delete == 0
            )
        )
        if ids:
            exp = exp.where(tb_recruitment_channel.c.id.in_(ids))

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_channels_by_ids(cls, company_id: str, ids: list, fields: list = None) -> list:
        _keys = recruitment_channel_tbu.filter_keys(fields)
        exp = select(
            [tb_recruitment_channel.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_channel.c.company_id == company_id,
                tb_recruitment_channel.c.is_delete == 0,
                tb_recruitment_channel.c.id.in_(ids)
            )
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def find_channel_by_name(cls, company_id: str, name: str, exclude_id=None) -> str:
        """
        根据渠道名称获取招聘渠道
        """
        stmt = select([
            tb_recruitment_channel.c.id.label('id'),
            tb_recruitment_channel.c.name.label('name'),
        ]).where(
            and_(
                tb_recruitment_channel.c.company_id == uuid2str(company_id),
                tb_recruitment_channel.c.name == name
            )
        )
        if exclude_id:
            stmt = stmt.where(tb_recruitment_channel.c.id != uuid2str(exclude_id))
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, stmt)

        return result.get("id") if result else None

    @classmethod
    async def get_channel_list(cls, company_id: str, fields: list, pagination=False, **kwargs) -> dict:
        """
        获取招聘渠道列表
        """
        _keys = recruitment_channel_tbu.filter_keys(fields)

        stmt = select(
            [tb_recruitment_channel.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_channel.c.company_id == uuid2str(company_id),
                tb_recruitment_channel.c.is_delete == 0
            )
        ).order_by(
            tb_recruitment_channel.c.is_forbidden.asc(),
            tb_recruitment_channel.c.order_no.asc(),
            tb_recruitment_channel.c.all_system.asc(),
            tb_recruitment_channel.c.add_dt.desc()
        )

        keyword = kwargs.get("keyword")
        if keyword:
            stmt = stmt.where(tb_recruitment_channel.c.name.like(f'%{keyword}%'))
        ids = kwargs.get("ids")
        if ids:
            stmt = stmt.where(tb_recruitment_channel.c.id.in_(ids))
        filter_forbidden = kwargs.get("filter_forbidden")
        if filter_forbidden:
            stmt = stmt.where(tb_recruitment_channel.c.is_forbidden == 0)
        engine = await db.default_db
        if pagination:
            paginator = Paginator(engine, stmt, kwargs.get("p", 1), kwargs.get("limit", 10))
            ret = await paginator.data()
        else:
            ret = await db_executor.fetch_all_data(engine, stmt)

        return ret

    @classmethod
    async def create_channel(cls, company_id: str, user_id: str, validated_data: dict) -> str:
        """
        创建招聘渠道
        """
        engine = await db.default_db
        validated_data.update(
            {
                "company_id": uuid2str(company_id),
                "add_by_id": uuid2str(user_id),
            }
        )
        result = await db_executor.single_create(engine, tb_recruitment_channel, validated_data)

        return result

    @classmethod
    async def update_channel(cls, company_id: str, user_id: str, u_id: str, validated_data: dict):
        """
        更新招聘渠道信息
        """
        engine = await db.default_db
        validated_data["update_by_id"] = uuid2str(user_id)
        where_stmt = and_(
            tb_recruitment_channel.c.id == uuid2str(u_id),
            tb_recruitment_channel.c.company_id == uuid2str(company_id)
        )
        await db_executor.update_data(engine, tb_recruitment_channel, validated_data, where_stmt)


if __name__ == "__main__":
    async def helper():
        uid = await RecruitmentChannelService.create_channel(
            "b117d06d3c084c0e9e2970309c215d73", 'b117d06d3c084c0e9e2970309c215d73',
            {"name": "王八", "remark": "哈哈哈", "related_url": "www.baidu.com"}
        )
        print(uid)
        await RecruitmentChannelService.update_channel(
            "b117d06d3c084c0e9e2970309c215d73", 'b117d06d3c084c0e9e2970309c215d73', uid,
            {"name": "王八蛋", "remark": "哈哈哈11", "related_url": "www.baidu.com"}
        )

    asyncio.get_event_loop().run_until_complete(helper())
