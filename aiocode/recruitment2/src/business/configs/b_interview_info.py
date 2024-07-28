from services.s_dbs.config.s_interview_infomation import InterviewInformationService
from services.s_dbs.s_common import DistrictService
from utils.strutils import uuid2str


class InterviewInformationBusiness(object):

    @classmethod
    async def clear_cache(cls, company_id: str) -> None:
        """清除企业缓存"""
        company_id = uuid2str(company_id)
        await InterviewInformationService.clear_company_cache(company_id)

    @classmethod
    async def update_validated_data_district(cls, data: dict) -> dict:
        """
        填充省市区的名称
        # TODO 这个方法可以提出去当通用工具
        """
        province_id = data.get("province_id")
        city_id = data.get("city_id")
        town_id = data.get("town_id")
        ids = []
        if province_id:
            ids.append(province_id)
        if city_id:
            ids.append(city_id)
        if town_id:
            ids.append(town_id)

        _district_dict = await DistrictService.get_district(ids)

        if province_id:
            province = _district_dict.get(province_id)
            if province:
                data["province_name"] = province.get("name")
            else:
                data["province_name"] = None

        if city_id:
            city = _district_dict.get(city_id)
            if city:
                data["city_name"] = city.get("name")
            else:
                data["city_name"] = None

        if town_id:
            town = _district_dict.get(town_id)
            if town:
                data["town_name"] = town.get("name")
            else:
                data["town_name"] = None

        return data

    @classmethod
    async def create_obj(cls, company_id: str, user_id: str, form_data: dict) -> str:
        """
        创建面试联系人信息
        @:returns 创建对象id
        """
        linkman = form_data.pop("linkman", "")
        linkman_mobile = form_data.pop("linkman_mobile", "")
        # 处理行政区数据
        form_data = await cls.update_validated_data_district(form_data)
        ret = await InterviewInformationService.create_obj(
            company_id, user_id, linkman, linkman_mobile, **form_data
        )

        await cls.clear_cache(company_id)
        return ret

    @classmethod
    async def update_obj(cls, company_id: str, user_id: str, pk: str, form_data: dict) -> dict:
        """
        更新面试联系人信息
        """
        # 处理行政区数据
        form_data = await cls.update_validated_data_district(form_data)

        await InterviewInformationService.update_obj(
            company_id, user_id, pk, **form_data
        )

        await cls.clear_cache(company_id)

        return {"id": pk}

    @classmethod
    async def delete_obj(cls, company_id: str, user_id: str, pk: str) -> dict:
        await InterviewInformationService.delete_obj(
            company_id, user_id, pk
        )

        await cls.clear_cache(company_id)

        return {"msg": "删除成功"}

    @classmethod
    async def get_list(cls, company_id) -> list:
        """
        获取企业面试联系人列表 不分页
        :param company_id:
        :return:
        """
        # await InterviewInformationService.clear_company_cache(company_id)
        return await InterviewInformationService.cache_company_list(company_id)

    @classmethod
    async def sort_records(cls, company_id: str, record_ids: list) -> None:
        """
        面试联系人排序
        """
        await InterviewInformationService.sort_records(
            company_id, record_ids
        )

        # 清除缓存
        await cls.clear_cache(company_id)
