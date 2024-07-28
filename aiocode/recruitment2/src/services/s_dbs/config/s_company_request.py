import datetime

import sqlalchemy as sa
from drivers.mysql import db
from models.m_config import tb_company_request
from utils.strutils import gen_uuid


class CompanyRequestService(object):
    @classmethod
    async def check_company_request(cls, company_id: str):
        """
        检查企业是否开通
        :return: True 已开通, False 未开通
        """
        query = sa.select([sa.exists().where(tb_company_request.c.company_id == company_id)])
        engine = await db.default_db
        async with engine.acquire() as conn:
            ret = await conn.execute(query)
            result = await ret.fetchone()
        return result[0]

    @classmethod
    async def create(cls, company_id: str, user_id: str):
        """
        创建企业开通信息
        """
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                sa.insert(tb_company_request).values(
                    id=gen_uuid(),
                    company_id=company_id,
                    add_by_id=user_id,
                    add_dt=datetime.datetime.now()
                )
            )

    @classmethod
    async def get(cls, company_id: str) -> object:
        """
        获取企业开通信息
        """
        _sql = sa.select([
            tb_company_request.c.id.label("id"),
            tb_company_request.c.company_id.label("company_id"),
            tb_company_request.c.add_by_id.label('add_by_id'),
            tb_company_request.c.add_dt.label('add_dt'),
            tb_company_request.c.interview_count.label('interview_count')
        ]).where(
            tb_company_request.c.company_id == company_id
        )
        engine = await db.default_db
        async with engine.acquire() as conn:
            ret = await conn.execute(_sql)
            ret = await ret.fetchall()

        results = [dict(r) for r in ret]
        if len(results) > 0:
            return results[0]
        return None


if __name__ == "__main__":
    import asyncio

    async def _helper():
        service = CompanyRequestService()
        assert await service.check_company_request('abc') == False
        assert await service.check_company_request('ab164df86d10491f90ccbece63cc865e') == True
    asyncio.run(_helper())
