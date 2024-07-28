# coding: utf-8
from datetime import datetime

from sqlalchemy import select

from drivers.mysql import db
from models.m_portals import tb_company_referral_config
from utils.sa_db import db_executor
from utils.strutils import uuid2str


class ReferralConfigService(object):

    @classmethod
    async def create_config(cls, company_id: str, user_id: str, validated_data: dict):
        """
        创建内推设置信息
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        validated_data.update(
            {
                "company_id": uuid2str(company_id),
                "add_by_id": uuid2str(user_id),
                "add_dt": datetime.now()
            }
        )
        await db_executor.single_create(
            db.default, tb_company_referral_config, validated_data
        )

    @classmethod
    async def update_config(cls, company_id: str, user_id: str, validated_data: dict):
        """
        更新内推设置信息
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        validated_data.update(
            {
                "update_by_id": uuid2str(user_id),
                "update_dt": datetime.now()
            }
        )
        await db_executor.update_data(
            db.default, tb_company_referral_config, validated_data,
            tb_company_referral_config.c.company_id == uuid2str(company_id)
        )

    @classmethod
    async def get_config(cls, company_id: str, fields: list):
        """
        获取内推设置信息
        @param company_id:
        @param fields:
        @return:
        """
        stmt = select(
            [tb_company_referral_config.c.get(field).label(field) for field in fields]
        ).where(
            tb_company_referral_config.c.company_id == uuid2str(company_id)
        )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, stmt)

        return result
