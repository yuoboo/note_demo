# coding: utf-8
from kits.exception import APIValidationError
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService, recruitment_channel_tbu


class RecruitmentChannelBusiness(object):

    @classmethod
    async def channel_list(cls, company_id: str, query_params: dict):
        """
        获取招聘渠道列表
        """
        fields = ["id", "name", "remark", "is_system", "is_forbidden", "related_url", "all_system", "show_color"]
        data = await RecruitmentChannelService.get_channel_list(
            company_id, fields, pagination=True, **query_params
        )

        return data

    @classmethod
    async def create_channel(cls, company_id: str, user_id: str, validated_data: dict) -> dict:
        """
        添加招聘渠道
        """
        name = validated_data.get("name")
        if await RecruitmentChannelService.find_channel_by_name(company_id, name):
            raise APIValidationError(msg="招聘渠道名称已存在")
        u_id = await RecruitmentChannelService.create_channel(
            company_id, user_id, validated_data
        )

        return {"id": u_id}

    @classmethod
    async def update_channel(cls, company_id: str, user_id: str, u_id: str, validated_data: dict) -> dict:
        """
        添加招聘渠道
        """
        name = validated_data.get("name")
        # 启用、禁用不需要传name
        if name and await RecruitmentChannelService.find_channel_by_name(
                company_id, name, u_id
        ):
            raise APIValidationError(msg="招聘渠道名称已存在")
        await RecruitmentChannelService.update_channel(
            company_id, user_id, u_id, validated_data
        )

        return {"id": u_id}


class IntranetChannelBiz:

    @classmethod
    async def get_channel_info(cls, company_id: str, ids: list = None, fields: list = None) -> list:

        if fields:
            diff = set(fields) - set(recruitment_channel_tbu.tb_keys)
            if diff:
                raise APIValidationError(msg=f"不支持的字段: {diff}")

        return await RecruitmentChannelService.get_channels(
            company_id=company_id, ids=ids, fields=fields
        )
