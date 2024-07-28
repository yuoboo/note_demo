import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.sql.elements import and_
from drivers.mysql import db
from models.m_config import tb_eliminated_reason
from utils.sa_db import db_executor, Paginator
from utils.strutils import uuid2str
from utils.table_util import TableUtil

eliminated_reason_tbu = TableUtil(tb_eliminated_reason)


class EliminatedReasonService:

    @classmethod
    async def get_reasons_by_ids(cls, company_id: str, ids: list = None, fields: list = None):
        fields = eliminated_reason_tbu.filter_keys(fields)
        query = sa.select(
            [tb_eliminated_reason.c[field].label(field) for field in fields]
        ).where(
            and_(
                tb_eliminated_reason.c.company_id == company_id,
            )
        )
        if ids:
            query = query.where(tb_eliminated_reason.c.id.in_(ids))

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, query)
        return [dict(item) for item in items]

    @classmethod
    async def valid_reason_text(
            cls, company_id: str, reason: str, reason_step: int, record_id: str = None
    ) -> bool:
        """
        校验淘汰原因是否存在
        @:param record_id 排除id, 在校验是否存在时会将此id排除在外
        """
        query = sa.select([
            tb_eliminated_reason.c.id
        ]).where(
            and_(
                tb_eliminated_reason.c.is_delete == 0,
                tb_eliminated_reason.c.company_id == company_id,
                tb_eliminated_reason.c.reason_step == reason_step,
                tb_eliminated_reason.c.reason == reason
            )
        )
        if record_id:
            record_id = uuid2str(record_id)
            query.where(
                tb_eliminated_reason.c.id != record_id
            )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, query)
        return bool(result)

    @classmethod
    async def query_reason_exist(cls, company_id: str, pk: str) -> bool:
        """
        查询淘汰原因是否存在
        """
        query = sa.select(
            [tb_eliminated_reason.c.id]
        ).where(
            and_(
                tb_eliminated_reason.c.is_delete == 0,
                tb_eliminated_reason.c.company_id == company_id,
                tb_eliminated_reason.c.id == pk
            )
        )

        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, query)
        return bool(result)

    @classmethod
    async def get_all(cls, company_id: str, filter_deleted=True) -> list:
        """
        获取企业所有淘汰原因表
        @param company_id:
        @param filter_deleted: 是否过滤删除的淘汰原因
        @return:
        """
        company_id = uuid2str(company_id)
        engine = await db.default_db
        stmt = select(
            [tb_eliminated_reason.c.get(field).label(field) for field in tb_eliminated_reason.c.keys()]).where(
                tb_eliminated_reason.c.company_id == company_id,
        )
        if filter_deleted:
            stmt = stmt.where(tb_eliminated_reason.c.is_delete == 0)
        result_list = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in result_list]

    @classmethod
    async def ge_rowcount_by_ids(cls, company_id: str, record_ids: list) -> int:
        query = sa.select(
            [tb_eliminated_reason.c.id]
        ).where(
            and_(
                tb_eliminated_reason.c.is_delete == 0,
                tb_eliminated_reason.c.company_id == company_id,
                tb_eliminated_reason.c.id.in_(record_ids)
            )
        )
        engine = await db.default_db
        results = await db_executor.fetch_all_data(engine, query)

        return len(results)

    @classmethod
    async def get_count_by_reason_step(cls, company_id: str, reason_step: int) -> int:
        query = sa.select(
            [tb_eliminated_reason.c.id]
        ).where(
            and_(
                tb_eliminated_reason.c.is_delete == 0,
                tb_eliminated_reason.c.company_id == company_id,
                tb_eliminated_reason.c.reason_step == reason_step
            )
        )

        engine = await db.default_db
        results = await db_executor.fetch_all_data(engine, query)

        return len(results)

    @classmethod
    async def create_eliminated_reason(
            cls, company_id: str, user_id: str, reason_step: int, reason: str
    ) -> str:
        """
        创建淘汰原因
        """
        value = {
            "company_id": company_id,
            "reason": reason,
            "reason_step": reason_step,
            "add_by_id": user_id
        }

        engine = await db.default_db
        pk = await db_executor.single_create(
            engine, tb_eliminated_reason, value
        )
        return pk

    @classmethod
    async def update_eliminated_reason(cls, company_id: str, user_id: str, pk: str, reason: str):
        """
        更新淘汰原因
        """
        where_stmt = and_(
            tb_eliminated_reason.c.company_id == uuid2str(company_id),
            tb_eliminated_reason.c.id == uuid2str(pk),
            tb_eliminated_reason.c.is_delete == 0
        )
        value = {"reason": reason, "update_by_id": uuid2str(user_id)}
        engine = await db.default_db
        await db_executor.update_data(engine, tb_eliminated_reason, value, where_stmt)

    @classmethod
    async def delete_eliminated_reason(cls, company_id: str, user_id: str, pk: str):
        """
        删除淘汰原因
        """
        where_stmt = and_(
            tb_eliminated_reason.c.company_id == uuid2str(company_id),
            tb_eliminated_reason.c.id == uuid2str(pk),
            tb_eliminated_reason.c.is_delete == 0
        )
        value = {"is_delete": 1, "update_by_id": uuid2str(user_id)}
        engine = await db.default_db
        await db_executor.update_data(engine, tb_eliminated_reason, value, where_stmt)

    @classmethod
    async def update_reason_sort(cls, company_id: str, user_id: str, pk: str, order_no: int):
        """
        更新淘汰原因排序
        """
        where_stmt = and_(
            tb_eliminated_reason.c.company_id == uuid2str(company_id),
            tb_eliminated_reason.c.id == uuid2str(pk),
            tb_eliminated_reason.c.is_delete == 0
        )
        value = {"order_no": order_no, "update_by_id": uuid2str(user_id)}
        engine = await db.default_db
        await db_executor.update_data(engine, tb_eliminated_reason, value, where_stmt)

    @classmethod
    async def get_eliminated_reasons_with_page(
            cls, company_id: str, page: int, limit: int, reason_step: int
    ) -> list:
        """
        查询淘汰原因 带分页
        :param company_id:
        :param page: 页码
        :param limit: 每页限制
        :param reason_step: 所属阶级
        :return:
        """
        query = sa.select([
            tb_eliminated_reason.c.id.label("id"),
            tb_eliminated_reason.c.reason_step.label("reason_step"),
            tb_eliminated_reason.c.reason.label("reason"),
            tb_eliminated_reason.c.order_no.label("order_no"),
            tb_eliminated_reason.c.is_system.label("is_system")
        ]).where(
            and_(
                tb_eliminated_reason.c.is_delete == 0,
                tb_eliminated_reason.c.company_id == uuid2str(company_id)
            )
        ).order_by(
            tb_eliminated_reason.c.reason_step.asc(),
            tb_eliminated_reason.c.order_no.asc(),
            tb_eliminated_reason.c.add_dt.desc()
        )
        if reason_step:
            query = query.where(
                tb_eliminated_reason.c.reason_step == reason_step
            )
        engine = await db.default_db
        paginator = Paginator(engine, query, page, limit)
        return await paginator.data()

    @classmethod
    async def get_select_data(
            cls, company_id: str, fields: list, reason_step: int = None, include_deleted=False
    ) -> list:
        """
        返回企业所有的淘汰原因
        """
        query = sa.select(
            [tb_eliminated_reason.c.get(field).label(field) for field in fields]
        ).where(
            tb_eliminated_reason.c.company_id == company_id
        )
        if reason_step:
            query = query.where(
                tb_eliminated_reason.c.reason_step == reason_step
            )
        if not include_deleted:
            query = query.where(tb_eliminated_reason.c.is_delete == 0)
        query = query.order_by(     # "reason_step", "order_no", "-add_dt
            tb_eliminated_reason.c.reason_step.asc(),
            tb_eliminated_reason.c.order_no.asc(),
            tb_eliminated_reason.c.add_dt.desc()
        )
        engine = await db.default_db
        ret = await db_executor.fetch_all_data(engine, query)
        return [dict(r) for r in ret]


if __name__ == "__main__":
    import asyncio

    com_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    u_id = "362f7de6128e460589ef729e7cdda774"
    _id = "925808b06a8146cb9385044fc8de7646"
    # _id = '3a85077923674429bb3faec06d6254ec'

    async def _test():
        t1 = await EliminatedReasonService.query_reason_exist(
            com_id, _id
        )
        print(f"this is query exist: {t1}")

    asyncio.run(_test())
