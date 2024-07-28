# coding: utf-8
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.sql.elements import and_

from drivers.mysql import db
from models.m_config import tb_company_intro
from utils.sa_db import Paginator
from utils.strutils import uuid2str, gen_uuid


class CompanyIntroService(object):
    """
    企业介绍服务
    """

    @classmethod
    async def get_company_intro_by_id(cls, company_id: str, record_id: str) -> dict:
        engine = await db.default_db
        async with engine.acquire() as conn:
            result = await conn.execute(
                sa.select([tb_company_intro]).where(
                    and_(
                        tb_company_intro.c.company_id == uuid2str(company_id),
                        tb_company_intro.c.id == uuid2str(record_id),
                        tb_company_intro.c.is_delete == False
                    )
                )
            )
            obj = await result.fetchone()
        data = {}
        if obj:
            data.update(
                {
                    "id": obj.c_id,
                    "company_name": obj.c_company_name,
                    "company_scale_id": obj.c_company_scale_id,
                    "industry_id": obj.c_industry_id,
                    "second_industry_id": obj.c_second_industry_id,
                    "contacts": obj.c_contacts,
                    "contact_number": obj.c_contact_number,
                    "contact_email": obj.c_contact_email,
                    "company_address": obj.c_company_address,
                    "address_longitude": obj.c_address_longitude,
                    "address_latitude": obj.c_address_latitude,
                    "company_desc": obj.c_company_desc,
                    "welfare_tag": obj.c_welfare_tag.split(',') if obj.c_welfare_tag else [],
                    "logo_url": obj.c_logo_url,
                    "image_url": obj.c_image_url.split(",") if obj.c_image_url else [],
                    "qrcode_type": obj.c_qrcode_type,
                    "qrcode_url": obj.c_wechat_qrcode,
                    "is_default": obj.c_is_default
                }
            )
        return data

    @classmethod
    async def create_company_info(cls, company_id: str, user_id: str, validated_data: dict) -> str:
        """
        创建企业介绍
        """
        u_id = gen_uuid()
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                tb_company_intro.insert().values(
                    id=u_id,
                    company_id=uuid2str(company_id),
                    company_scale_id=validated_data.get("company_scale_id") or 0,
                    industry_id=validated_data.get("industry_id") or 0,
                    second_industry_id=validated_data.get("second_industry_id") or 0,
                    company_name=validated_data.get("company_name"),
                    contacts=validated_data.get("contacts") or "",
                    contact_number=validated_data.get("contact_number") or "",
                    contact_email=validated_data.get("contact_email") or "",
                    company_address=validated_data.get("company_address") or "",
                    address_longitude=validated_data.get("address_longitude") or 0,
                    address_latitude=validated_data.get("address_latitude") or 0,
                    company_desc=validated_data.get("company_desc") or "",
                    welfare_tag=validated_data.get("welfare_tag") or "",
                    logo_url=validated_data.get("logo_url") or "",
                    image_url=validated_data.get("image_url") or "",
                    qrcode_url=validated_data.get("qrcode_url") or "",
                    qrcode_type=validated_data.get("qrcode_type", 0),
                    qrcode_user_id=validated_data.get("qrcode_user_id", ""),
                    add_by_id=uuid2str(user_id),
                    add_dt=datetime.now()
                )
            )
        return u_id

    @classmethod
    async def update_company_intro(cls, company_id: str, user_id: str, record_id: str, validated_data: dict) -> str:
        """
        更新企业介绍
        """
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                tb_company_intro.update().where(
                    and_(
                        tb_company_intro.c.company_id == uuid2str(company_id),
                        tb_company_intro.c.id == uuid2str(record_id)
                    )
                ).values(
                    update_by_id=uuid2str(user_id),
                    update_dt=datetime.now(),
                    **validated_data
                )
            )

        return record_id

    @classmethod
    async def company_intro_list(cls, company_id: str, page=1, limit=999, **kwargs) -> dict:
        """
        获取企业介绍
        """
        stmt = select(
            [
                tb_company_intro.c.id.label("id"),
                tb_company_intro.c.company_name.label("company_name"),
                tb_company_intro.c.company_scale_id.label("company_scale_id"),
                tb_company_intro.c.industry_id.label("industry_id"),
                tb_company_intro.c.second_industry_id.label("second_industry_id"),
                tb_company_intro.c.contacts.label("contacts"),
                tb_company_intro.c.contact_number.label("contact_number"),
                tb_company_intro.c.contact_email.label("contact_email"),
                tb_company_intro.c.company_address.label("company_address"),
                tb_company_intro.c.address_longitude.label("address_longitude"),
                tb_company_intro.c.address_latitude.label("address_latitude"),
                tb_company_intro.c.company_desc.label("company_desc"),
                tb_company_intro.c.logo_url.label("logo_url"),
                tb_company_intro.c.qrcode_type.label("qrcode_type"),
                tb_company_intro.c.qrcode_url.label("qrcode_url"),
                tb_company_intro.c.qrcode_user_id.label("qrcode_user_id"),
                tb_company_intro.c.image_url.label("image_url"),
                tb_company_intro.c.welfare_tag.label("welfare_tag"),
            ]
        ).where(
            and_(
                tb_company_intro.c.company_id == uuid2str(company_id),
                tb_company_intro.c.is_delete == False
            )
        ).order_by(
            tb_company_intro.c.order_no.asc(),
            tb_company_intro.c.add_dt.desc()
        )
        engine = await db.default_db
        paginator = Paginator(engine, stmt, page, limit)
        ret = await paginator.data()

        return ret
