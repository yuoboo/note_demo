import ujson

from services.s_dbs.config.s_custom_search import CustomSearchService


class CustomSearchBusiness(object):
    """
    自定义筛选条件配置业务
    """

    @classmethod
    async def create_or_update(cls, company_id: str, scene_type: int, user_type: int, add_by_id: str, config: str) -> bool:
        """
        创建或修改自定义筛选条件配置
        @param company_id: 企业id
        @param scene_type: 场景类型
        @param user_type: 用户类型
        @param add_by_id: 添加人id
        @param config: 配置内容
        @return:
        """
        await CustomSearchService.create_or_update(company_id, scene_type, user_type, add_by_id, config)
        return True

    @classmethod
    async def get(cls, company_id: str, scene_type: int, user_type: int, add_by_id: str) -> dict:
        """
        获取自定义筛选条件配置
        @param company_id: 企业id
        @param scene_type: 场景类型
        @param user_type: 用户类型
        @return:
        """
        result = await CustomSearchService.get(company_id, scene_type, user_type, add_by_id)
        return ujson.loads(result.get('config', None)) if result.get('config', None) else []
