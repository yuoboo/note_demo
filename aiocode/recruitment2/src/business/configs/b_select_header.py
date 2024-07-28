
from constants import SelectFieldUserType, SelectFieldFormType
from services.s_dbs.config.s_select_header import SelectHeaderService
from kits.exception import APIValidationError
from business.configs import SelectConfig, JobPositionHeader, JobPositionStopHeader
from utils.strutils import uuid2str


class SelectHeaderBusiness(object):
    """
    选择表头
    """
    select_config = SelectConfig()

    ungroup_header = {
        5: JobPositionHeader,
        6: JobPositionStopHeader
    }

    # 需要排除的分类
    exclude_group_map = {
        3: ("employ_info",),  # 面试日程
        4: ("interview_info", "employ_info"),  # 人才库列表
        10: ("interview_info", "employ_info"),
        11: ("interview_info", "employ_info"),
        12: ("interview_info", "employ_info"),
        20: ("employ_info",),
        21: ("employ_info",),
        22: ("employ_info",),
        23: ("employ_info",),
        41: ("interview_info", "employ_info"),  # 高级搜索 人才
    }

    # 需要排除分类中的部分字段
    exclude_field_map = {
        4: ("job_position", "dep_name", "candidate_record_status", "latest_forward_dt", "participant",
            "recruitment_channel", "recruitment_page_name", "add_by",
            "add_dt", "talent_assessment_status", "bg_check_status", "eliminated_reason", "eliminated_dt",
            "referee_name", "referee_mobile"),

        41: ("job_position", "dep_name", "candidate_record_status", "latest_forward_dt", "participant",
             "recruitment_channel", "recruitment_page_name", "add_by",
             "add_dt", "talent_assessment_status", "bg_check_status", "eliminated_reason", "eliminated_dt",
             "referee_name", "referee_mobile")
    }

    # 员工端需要排除最近转发时间和备注字段
    employee_exclude_fields = ("latest_forward_dt", "remark")

    @classmethod
    async def clear_user_cache(cls, company_id: str, user_id: str) -> None:
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        await SelectHeaderService.clear_user_cache(company_id=company_id, user_id=user_id)

    @classmethod
    async def get_header_fields(cls, company_id: str, user_id: str, scene_type: int,
                                user_type: int = SelectFieldUserType.hr
                                ) -> dict:
        """
        根据场景返回表头信息
        :param company_id:
        :param user_id:
        :param scene_type: 场景编码
        :param user_type: 用户类型
        :return:
        """
        return await cls._get_user_header_dict(company_id, user_id, scene_type, user_type)

    @classmethod
    async def update_user_header_fields(cls, company_id: str, user_id: str, fields: list, scene_type: int,
                                        user_type: int = SelectFieldUserType.hr
                                        ) -> dict:
        """更新用户表头信息"""
        if len(fields) < 4:
            raise APIValidationError(msg="显示字段不能小于4个")

        fixed_fields = await cls.get_fixed_fields(company_id, scene_type, user_type)
        for field in fixed_fields:
            if field["field_key"] not in fields:
                raise APIValidationError(msg=f"字段{field['name']}不能删除")

        await SelectHeaderService.update_select_fields(company_id, user_id, fields, scene_type, user_type)

        # 清除缓存
        await cls.clear_user_cache(company_id, user_id)

        return await cls._get_user_header_dict(company_id, user_id, scene_type, user_type)

    @classmethod
    async def _get_user_header_dict(cls, company_id: str, user_id: str, scene_type: int,
                                    user_type: int) -> dict:
        """
        获取用户自定义表头信息
        :param company_id:
        :param user_id: 用户id, 如果是员工端请使用emp_id
        :param scene_type:
        :param user_type:
        :return:
        """
        selected_fields = await cls.get_selected_fields_list(
            company_id, user_id, scene_type, user_type, with_default=False
        )

        # 为分组场景直接返回
        if scene_type in cls.ungroup_header:
            return cls.ungroup_header[scene_type].get_header_info(company_id, selected_fields)

        # 分组类型
        return {
            "selected_fields": await cls._get_select_header(company_id, selected_fields, scene_type, user_type),
            "system_fields": await cls._get_unselected_header(company_id, selected_fields, scene_type, user_type)
        }

    @classmethod
    async def _get_select_header(cls, company_id: str, selected_fields: list, scene_type: int,
                                 user_type: int = SelectFieldUserType.hr
                                 ) -> list:
        """
        获取已选字段信息, 没有则返回默认表头
        :param company_id:
        :param selected_fields:  已选字段
        :param scene_type:
        :param user_type:
        :return:
        """
        ret = []

        fields_pool = await cls.fields_pool_for_scene_type(company_id, scene_type, user_type)
        pool_dict = dict(zip([i["field_key"] for i in fields_pool], fields_pool))
        if selected_fields:
            custom_fields = await cls.get_custom_fields(company_id)
            custom_dict = dict(zip([c["field_key"] for c in custom_fields], custom_fields))

            for s in selected_fields:
                if s in pool_dict:
                    ret.append(pool_dict[s])
                elif s in custom_dict:
                    ret.append(custom_dict[s])
        else:
            # 返回默认表头 + 自定义字段
            default_fields = await cls.get_default_fields_list(scene_type, user_type)
            custom_fields = await cls.get_custom_fields(company_id)
            ret = [pool_dict[d] for d in default_fields if d in pool_dict]
            ret.extend(custom_fields)

        return ret

    @classmethod
    async def get_custom_fields(cls, company_id: str) -> list:
        """
        返回企业已启用的自定义字段列表
        """
        # todo 返回自定义字段列表
        return []

    @classmethod
    async def _get_unselected_header(cls, company_id: str, selected_fields: list,
                                     scene_type: int, user_type: int) -> list:
        """
        返回系统未选表头信息
        :param company_id:
        :param scene_type:
        :param user_type:
        :return:
        """
        fields_pool = await cls.fields_pool_for_scene_type(company_id, scene_type, user_type)
        if selected_fields:
            custom_fields = await cls.get_custom_fields(company_id)
            fields_pool.extend(custom_fields)
        else:
            selected_fields = await cls._default_fields_for_scene(scene_type, user_type)

        unselected = filter(
            lambda x: x["field_key"] not in selected_fields, fields_pool
        )
        return list(unselected)

    @classmethod
    async def fields_pool_for_scene_type(cls, company_id: str, scene_type: int = None,
                                         user_type: int = SelectFieldUserType.hr) -> list:
        """
        返回对应场景可选表头字段， 过滤分组和字段 还有灰度企业设置校验, 过滤员工端字段
        不包括 未分组场景(招聘列表 和 停止招聘列表 )
        :param company_id:
        :param scene_type:  没有场景id 则返回所有系统字段， 此时不会排除过滤分组和过滤字段
        :param user_type:  用户类型 用来过滤员工端字段
        :return:
        """
        if scene_type:
            exclude_group = cls.exclude_group_map.get(scene_type, [])
            exclude_fields = cls.exclude_field_map.get(scene_type, [])
            if user_type == SelectFieldUserType.employee:
                exclude_fields.extend(cls.employee_exclude_fields)

            fields = cls.select_config.system_fields(
                company_id=company_id, ex_group=exclude_group, ex_fields=exclude_fields
            )
        else:
            fields = cls.select_config.system_fields(company_id)
        return fields

    @classmethod
    async def _get_scene_type_dict(cls) -> dict:
        if not hasattr(cls, "_select_form_type_dict"):
            _value = SelectFieldFormType.values_
            setattr(cls, "_select_form_type_dict", dict(zip(_value.values(), _value.keys())))
        return getattr(cls, "_select_form_type_dict")

    @classmethod
    async def _default_fields_for_scene(cls, scene_type: int, user_type: int) -> list:
        """
        根据场景编码和用户类型返回系统默认字段 不包含未分组
        """
        _dict = await cls._get_scene_type_dict()
        ctype = _dict.get(scene_type)
        if ctype in cls.select_config.default_field_dict:
            default_fields = cls.select_config.default_field_dict[ctype]
            if user_type == SelectFieldUserType.employee:
                return list(filter(lambda x: x not in cls.employee_exclude_fields, default_fields))
            return default_fields
        return []

    @classmethod
    async def get_default_fields_list(cls, scene_type: int, user_type: int) -> list:
        """
        根据场景编码和用户类型返回系统默认字段， 包括未分组类型
        """
        if scene_type in cls.ungroup_header:
            _cls = cls.ungroup_header[scene_type]
            return list(_cls.default_fields)
        return await cls._default_fields_for_scene(scene_type, user_type)

    @classmethod
    async def user_header_fields_by_scene(cls, company_id: str, user_id: str, scene_type: int,
                                          user_type: int = SelectFieldUserType.hr) -> dict:
        """
        从缓存获取用户的选择表头信息
        """
        _user = await SelectHeaderService.cache_user_list(company_id, user_id)
        _user = list(filter(lambda x: x["scene_type"] == scene_type and x["user_type"] == user_type, _user))

        return _user[0] if _user else dict()

    @classmethod
    async def get_fixed_fields(cls, company_id: str, scene_type: int, user_type: int) -> list:
        """
        根据场景类型和用户类型获取固定字段
        """
        if not scene_type:
            return []

        if scene_type in cls.ungroup_header:
            sys_fields = cls.ungroup_header[scene_type].field_pool
            _default = cls.ungroup_header[scene_type].default_fields

        else:
            _default = await cls._default_fields_for_scene(scene_type, user_type)
            sys_fields = await cls.fields_pool_for_scene_type(company_id, scene_type, user_type)

        return list(filter(lambda x: x['is_fixed'] and x["field_key"] in _default, sys_fields))

    @classmethod
    async def get_selected_fields_list(cls, company_id: str, user_id: str, scene_type: int,
                                       user_type: int = SelectFieldUserType.hr,
                                       with_default=True) -> list:
        """
        返回用户已选表头
        :param company_id:
        :param user_id:
        :param scene_type:
        :param user_type:
        :param with_default: 是否返回默认配置
        :return:
        """
        fields_dict = await cls.user_header_fields_by_scene(company_id, user_id, scene_type, user_type)
        _fields = fields_dict.get("fields", "")
        if not _fields and with_default:
            return await cls.get_default_fields_list(scene_type, user_type)

        return _fields.split(',') if _fields else []

    @classmethod
    async def get_scene_fields_pool(cls, company_id: str, scene_type: int,
                                    user_type: int = SelectFieldUserType.hr) -> list:
        """
        根据场景编码获取选择字段池, 返回该场景所有系统可选字段, 不包括自定义字段
        """
        if scene_type in cls.ungroup_header:
            return cls.ungroup_header[scene_type].get_field_pool(company_id)

        return await cls.fields_pool_for_scene_type(company_id, scene_type, user_type)

    @classmethod
    async def get_selected_fields_detail_list(cls, company_id: str, user_id: str, scene_type: int,
                                              user_type: int = SelectFieldUserType.hr) -> list:
        """
        返回用户已选字段的详情 包括为分组和自定义字段
        """
        selected_fields = await cls.get_selected_fields_list(company_id, user_id, scene_type, user_type)
        fields_pool = await cls.get_scene_fields_pool(company_id, scene_type, user_type)
        pool_dict = dict(zip([p["field_key"] for p in fields_pool], fields_pool))

        # 获取自定义字段池
        cus_fields = await cls.get_custom_fields(company_id)

        pool_dict.update({c["field_key"]: c for c in cus_fields})

        return [pool_dict[_s] for _s in selected_fields if _s in pool_dict]

    @classmethod
    async def format_dict_header(cls, fields: list, is_sort=False) -> list:
        """
        将列表数据分类分组
        :param fields:
        :param is_sort: 是否需要排序
        :return:
        """
        ret = cls.select_config.group_map_blank
        if is_sort:
            fields = sorted(fields, key=lambda x: x.get("sort"))

        for f in fields:
            group_key = f["group_key"]
            if group_key in ret:
                ret[group_key]["items"].append(f)
        return ret.values()


