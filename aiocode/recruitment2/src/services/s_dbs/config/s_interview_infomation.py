import datetime

from constants import redis_keys
from drivers.mysql import db
from utils.cache_kits import CacheKlass
from models.m_config import tb_interview_information
import sqlalchemy as sa
from sqlalchemy.sql.elements import and_

from utils.strutils import gen_uuid, uuid2str


class InterviewInformationService(CacheKlass):
    _company_list_cache_key = redis_keys.INTERVIEW_INFORMATION_LIST

    @classmethod
    async def get_company_data(cls, company_id: str) -> list:
        _sql = sa.select([
            tb_interview_information.c.id.label("id"),
            tb_interview_information.c.is_delete.label("is_delete"),
            tb_interview_information.c.linkman.label('linkman'),
            tb_interview_information.c.linkman_mobile.label("linkman_mobile"),
            tb_interview_information.c.address.label("address"),
            tb_interview_information.c.province_id.label("province"),
            tb_interview_information.c.province_name.label("province_name"),
            tb_interview_information.c.city_id.label("city_id"),
            tb_interview_information.c.city_name.label("city_name"),
            tb_interview_information.c.town_id.label("town_id"),
            tb_interview_information.c.town_name.label("town_name"),
            tb_interview_information.c.order_no.label("order_no")
        ]).where(
            and_(
                tb_interview_information.c.company_id == company_id,
                tb_interview_information.c.is_delete == 0
            )
        ).order_by(
            tb_interview_information.c.order_no,
            tb_interview_information.c.add_dt.asc()
        )
        engine = await db.default_db
        async with engine.acquire() as conn:
            ret = await conn.execute(_sql)
            ret = await ret.fetchall()

        return [dict(r) for r in ret]

    @classmethod
    async def get_user_data(cls, company_id: str, user_id: str):
        pass

    @classmethod
    async def create_obj(cls, company_id: str, user_id: str, linkman: str, linkman_mobile: str,
                         *, address: str = None,
                         province_id: int = None, province_name: str = None,
                         city_id: int = None, city_name: str = None,
                         town_id: int = None, town_name: str = None) -> str:
        """
        创建面试联系人
        :param company_id:
        :param user_id:
        :param linkman: 联系人姓名
        :param linkman_mobile: 联系电话
        :param address: 联系地址
        :param province_id:
        :param province_name: 省份
        :param city_id:
        :param city_name: 城市
        :param town_id:
        :param town_name: 区县
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        engine = await db.default_db
        _id = gen_uuid()
        async with engine.acquire() as conn:
            await conn.execute(
                sa.insert(tb_interview_information).values(
                    id=_id,
                    company_id=company_id,
                    linkman=linkman, linkman_mobile=linkman_mobile,
                    address=address, province_id=province_id, province_name=province_name,
                    city_id=city_id, city_name=city_name,
                    town_id=town_id, town_name=town_name,
                    add_by_id=user_id
                )
            )

        return _id

    @classmethod
    async def update_obj(cls, company_id: str, user_id: str, pk: str, **kwargs) -> None:
        """
        更新面试联系人
        """
        if not kwargs:
            return

        kwargs["update_by_id"] = uuid2str(user_id)
        kwargs["update_dt"] = datetime.datetime.now()

        # 过滤表字段
        _fields = [column.key for column in tb_interview_information.columns]
        u_kwargs = {k: v for k, v in kwargs.items() if k in _fields and k != "id"}

        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                sa.update(tb_interview_information).where(
                    and_(
                        tb_interview_information.c.company_id == company_id,
                        tb_interview_information.c.id == pk
                    )
                ).values(
                    **u_kwargs
                )
            )

    @classmethod
    async def delete_obj(cls, company_id: str, user_id: str, pk: str) -> None:
        """删除面试联系人信息"""
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        pk = uuid2str(pk)

        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                sa.update(tb_interview_information).where(
                    and_(
                        tb_interview_information.c.company_id == company_id,
                        tb_interview_information.c.id == pk
                    )
                ).values(
                    is_delete=1,
                    update_by_id=user_id,
                    update_dt=datetime.datetime.now()
                )
            )

    @classmethod
    async def sort_records(cls, company_id: str, record_ids: list) -> None:
        """
        排序
        :param company_id:
        :param record_ids: 记录ids
        :return:
        """
        company_id = uuid2str(company_id)

        engine = await db.default_db
        async with engine.acquire() as conn:
            for index, _pk in enumerate(record_ids):
                _pk = uuid2str(_pk)
                await conn.execute(
                    sa.update(tb_interview_information).where(
                        and_(
                            tb_interview_information.c.company_id == company_id,
                            tb_interview_information.c.id == _pk
                        )
                    ).values(
                        order_no=index
                    )
                )

