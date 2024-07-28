# encoding=utf8
"""
自定义表头设置
候选人 人才库 面试日程 用的是同一个表头源， 有分类信息
招聘职位表头产品无法分类, 是独立的， 与前面三个不相同， 字段没有分类信息， 字段key也没有共用
"""

from collections import OrderedDict
from functools import cached_property

HEADER_POOL = (
    # 基础信息 group_key -> person_base_info
    {
        "field_name": "头像", "field_key": "head_img_url", "is_fixed": True, "sortable": False, "order": 100,
        "group_key": "person_base_info"
    },
    {
        "field_name": "姓名", "field_key": "candidate_name", "is_fixed": True, "sortable": False, "order": 101,
        "group_key": "person_base_info"
    },
    {
        "field_name": "性别", "field_key": "sex", "is_fixed": False, "sortable": True, "order": 102,
        "group_key": "person_base_info"
    },
    {
        "field_name": "年龄", "field_key": "age", "is_fixed": False, "sortable": True, "order": 103,
        "group_key": "person_base_info"
    },
    {
        "field_name": "工作年限", "field_key": "candidate_work_experience", "is_fixed": False, "sortable": True,
        "order": 104, "group_key": "person_base_info"
    },
    {
        "field_name": "学历", "field_key": "education", "is_fixed": False, "sortable": True, "order": 105,
        "group_key": "person_base_info"
    },
    {
        "field_name": "毕业院校", "field_key": "school", "is_fixed": False, "sortable": True, "order": 106,
        "group_key": "person_base_info"
    },
    {
        "field_name": "专业", "field_key": "profession", "is_fixed": False, "sortable": True, "order": 107,
        "group_key": "person_base_info"
    },
    {
        "field_name": "最近工作单位", "field_key": "latest_work_name", "is_fixed": False, "sortable": True, "order": 108,
        "group_key": "person_base_info"
    },
    {
        "field_name": "最近职位", "field_key": "latest_job", "is_fixed": False, "sortable": True, "order": 109,
        "group_key": "person_base_info"
    },
    {
        "field_name": "现居住地", "field_key": "residential_address", "is_fixed": False, "sortable": True, "order": 110,
        "group_key": "person_base_info"
    },
    {
        "field_name": "证件类型", "field_key": "credentials_type", "is_fixed": False, "sortable": True, "order": 111,
        "group_key": "person_base_info"
    },
    {
        "field_name": "证件号码", "field_key": "credentials_no", "is_fixed": False, "sortable": True, "order": 112,
        "group_key": "person_base_info"
    },

    # 联系信息
    {
        "field_name": "手机号码", "field_key": "mobile", "is_fixed": False, "sortable": True, "order": 201,
        "group_key": "contact_info"
    },
    {
        "field_name": "邮箱", "field_key": "email", "is_fixed": False, "sortable": True, "order": 202,
        "group_key": "contact_info"
    },

    # 求职意向
    {
        "field_name": "招聘职位", "field_key": "job_position", "is_fixed": False, "sortable": False, "order": 251,
        "group_key": "job_intention"
    },
    {
        "field_name": "用人部门", "field_key": "dep_name", "is_fixed": False, "sortable": True, "order": 252,
        "group_key": "job_intention"
    },
    {
        "field_name": "期望月薪", "field_key": "expected_salary", "is_fixed": False, "sortable": True, "order": 253,
        "group_key": "job_intention"
    },

    # 面试信息
    {
        "field_name": "面试轮次", "field_key": "interview_count", "is_fixed": False, "sortable": True, "order": 301,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试时间", "field_key": "interview_dt", "is_fixed": False, "sortable": True, "order": 302,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试官", "field_key": "interview_participant", "is_fixed": False, "sortable": True, "order": 303,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试方式", "field_key": "interview_way", "is_fixed": False, "sortable": True, "order": 304,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试地址", "field_key": "interview_address", "is_fixed": False, "sortable": True, "order": 305,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试联系人", "field_key": "interview_linkname", "is_fixed": False, "sortable": True, "order": 306,
        "group_key": "interview_info"
    },
    {
        "field_name": "签到情况", "field_key": "is_sign", "is_fixed": False, "sortable": True, "order": 307,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试邀约状态", "field_key": "invitation_status", "is_fixed": False, "sortable": True, "order": 308,
        "group_key": "interview_info"
    },
    {
        "field_name": "面试评价数量", "field_key": "interview_comment_count", "is_fixed": False, "sortable": True,
        "order": 309, "group_key": "interview_info"
    },
    {
        "field_name": "面试创建人", "field_key": "add_by_name", "is_fixed": False, "sortable": True, "order": 310,
        "group_key": "interview_info"
    },
    {
        "field_name": "候选人是否阅读面试邀约", "field_key": "read_invitation", "is_fixed": False, "sortable": True,
        "order": 311, "group_key": "interview_info"
    },
    {
        "field_name": "应聘登记表状态", "field_key": "form_status", "is_fixed": False, "sortable": True, "order": 312,
        "group_key": "interview_info"
    },

    # 录用信息
    {
        "field_name": "入职部门", "field_key": "offer_dep_name", "is_fixed": False, "sortable": True, "order": 401,
        "group_key": "employ_info"
    },
    {
        "field_name": "入职岗位", "field_key": "job_title_name", "is_fixed": False, "sortable": True, "order": 402,
        "group_key": "employ_info"
    },
    {
        "field_name": "录用审批单号", "field_key": "approval_no", "is_fixed": False, "sortable": True, "order": 403,
        "group_key": "employ_info"
    },
    {
        "field_name": "录用审批状态", "field_key": "approval_status", "is_fixed": False, "sortable": True, "order": 404,
         "group_key": "employ_info"
    },
    {
        "field_name": "Offer发送时间", "field_key": "offer_add_dt", "is_fixed": False, "sortable": True, "order": 405,
        "group_key": "employ_info"
    },
    {
        "field_name": "Offer状态", "field_key": "offer_status", "is_fixed": False, "sortable": True, "order": 406,
        "group_key": "employ_info"
    },
    {
        "field_name": "Offer发送人", "field_key": "offer_add_by", "is_fixed": False, "sortable": True, "order": 407,
        "group_key": "employ_info"
    },
    {
        "field_name": "候选人是否阅读Offer", "field_key": "is_read", "is_fixed": False, "sortable": True, "order": 408,
        "group_key": "employ_info"
    },
    {
        "field_name": "入职日期", "field_key": "hire_date", "is_fixed": False, "sortable": True, "order": 409,
        "group_key": "employ_info"
    },
    {
        "field_name": "是否发送入职登记表", "field_key": "entry_form_status", "is_fixed": False, "sortable": True,
        "order": 410, "group_key": "employ_info"
    },

    # 其他信息
    {
        "field_name": "候选人状态", "field_key": "candidate_record_status", "is_fixed": False, "sortable": True,
        "order": 501, "group_key": "other_info"
    },
    {
        "field_name": "最近转发", "field_key": "latest_forward_dt", "is_fixed": False, "sortable": True, "order": 502,
        "group_key": "other_info"
    },
    {
        "field_name": "招聘HR", "field_key": "participant", "is_fixed": False, "sortable": True, "order": 503,
        "group_key": "other_info"
    },
    {
        "field_name": "招聘渠道", "field_key": "recruitment_channel", "is_fixed": False, "sortable": True, "order": 504,
        "group_key": "other_info"
    },
    {
        "field_name": "招聘网页", "field_key": "recruitment_page_name", "is_fixed": False, "sortable": True, "order": 505,
        "group_key": "other_info"
    },
    {
        "field_name": "候选人添加人", "field_key": "add_by", "is_fixed": False, "sortable": True, "order": 506,
        "group_key": "other_info"
    },
    {
        "field_name": "候选人添加时间", "field_key": "add_dt", "is_fixed": False, "sortable": True, "order": 507,
        "group_key": "other_info"
    },
    {
        "field_name": "人才评测状态", "field_key": "talent_assessment_status", "is_fixed": False, "sortable": True,
        "order": 508, "group_key": "other_info"
    },
    {
        "field_name": "背景调查状态", "field_key": "bg_check_status", "is_fixed": False, "sortable": True, "order": 509,
        "group_key": "other_info"
    },

    {
        "field_name": "淘汰/放弃原因", "field_key": "eliminated_reason", "is_fixed": False, "sortable": True, "order": 510,
        "group_key": "other_info"
    },
    {
        "field_name": "淘汰/放弃时间", "field_key": "eliminated_dt", "is_fixed": False, "sortable": True, "order": 511,
        "group_key": "other_info"
    },
    {
        "field_name": "人才添加人", "field_key": "talent_add_by", "is_fixed": False, "sortable": True, "order": 512,
        "group_key": "other_info"
    },
    {
        "field_name": "入库时间", "field_key": "talent_join_dt", "is_fixed": False, "sortable": True, "order": 513,
        "group_key": "other_info"
    },
    {
        "field_name": "标签", "field_key": "candidate_tags", "is_fixed": False, "sortable": True, "order": 514,
        "group_key": "other_info"
    },
    {
        "field_name": "备注", "field_key": "remark", "is_fixed": False, "sortable": True, "order": 515,
        "group_key": "other_info"
    },
    {
        "field_name": "推荐人姓名", "field_key": "referee_name", "is_fixed": False, "sortable": True, "order": 516,
        "group_key": "other_info"
    },
    {
        "field_name": "推荐人手机号码", "field_key": "referee_mobile", "is_fixed": False, "sortable": True, "order": 517,
        "group_key": "other_info"
    }
)


# 默认表头
default_config = {
    # 初筛
    "screen_to_be": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "latest_forward_dt",
                     "sex", "age",
                     "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                     "latest_job", "mobile", "email", "dep_name", "participant", "add_by", "candidate_tags", "remark"],

    # 初筛通过
    "screen_pass": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "latest_forward_dt", "sex",
                    "age", "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                    "latest_job", "mobile", "email", "dep_name", "participant", "add_by", "candidate_tags", "remark"],

    # 初筛淘汰
    "screen_out": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "eliminated_reason",
                   "latest_forward_dt", "sex", "age",
                   "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                   "latest_job", "mobile", "email", "dep_name", "participant", "add_by", "candidate_tags", "remark"],
    # 面试
    "interview_arranged": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "interview_count",
                           "interview_dt",
                           "interview_participant", "interview_way", "invitation_status", "add_by_name", "form_status",
                           "latest_forward_dt", "sex", "age", "candidate_work_experience", "education", "school",
                           "profession", "latest_work_name", "latest_job", "mobile", "email", "dep_name",
                           "participant", "add_by", "candidate_tags", "remark"],

    "interview_completed": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "interview_count",
                            "interview_dt", "interview_participant", "interview_way",
                            "interview_comment_count", "add_by_name", "form_status", "latest_forward_dt", "sex", "age",
                            "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                            "latest_job", "mobile", "email",
                            "dep_name", "participant", "add_by", "candidate_tags", "remark"],

    "interview_pass": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "interview_count",
                       "interview_dt", "interview_participant", "interview_way",
                       "interview_comment_count", "add_by_name", "form_status", "latest_forward_dt", "sex", "age",
                       "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                       "latest_job", "mobile", "email", "dep_name",
                       "participant", "add_by", "candidate_tags", "remark"],

    "interview_out": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "eliminated_reason",
                      "interview_count", "interview_dt", "interview_participant", "interview_way",
                      "interview_comment_count", "add_by_name", "form_status", "latest_forward_dt", "sex", "age",
                      "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                      "latest_job", "mobile", "email", "dep_name", "participant", "add_by", "candidate_tags", "remark"],
    # 录用
    "employ_intend": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "interview_dt",
                      "interview_comment_count", "expected_salary", "latest_forward_dt", "sex", "age",
                      "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                      "latest_job", "mobile", "email", "dep_name",
                      "participant", "add_by", "candidate_tags", "remark"],

    "employ_send_offer": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "offer_dep_name",
                          "job_title_name", "hire_date", "offer_status", "offer_add_dt", "offer_add_by", "latest_forward_dt", "sex",
                          "age", "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                          "latest_job", "mobile", "email", "participant", "add_by", "candidate_tags", "remark"],

    "employ_to_hire": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "offer_dep_name",
                       "job_title_name", "hire_date", "entry_form_status", "latest_forward_dt", "sex", "age",
                       "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                       "latest_job", "mobile", "email", "participant", "add_by", "candidate_tags", "remark"],

    "employ_hired": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "offer_dep_name",
                     "job_title_name", "hire_date", "entry_form_status", "latest_forward_dt", "sex", "age",
                     "candidate_work_experience", "education", "school", "profession", "latest_work_name",
                     "latest_job", "mobile", "email", "participant", "add_by", "candidate_tags", "remark"],

    "employ_give_up": ["head_img_url", "candidate_name", "job_position", "recruitment_channel", "eliminated_reason",
                       "offer_dep_name", "job_title_name", "hire_date",
                       "latest_forward_dt", "sex", "age", "candidate_work_experience", "education", "school",
                       "profession", "latest_work_name", "latest_job", "mobile", "email", "dep_name", "participant",
                       "add_by", "candidate_tags", "remark"],

    # 人才库
    "talent_list": ["head_img_url", "candidate_name", "sex", "age", "candidate_work_experience", "education", "school",
                    "profession",
                    "latest_work_name", "latest_job", "residential_address", "mobile", "email", "expected_salary",
                    "candidate_tags", "remark", "talent_add_by", "talent_join_dt", ],

    # 面试日程
    "interview_date": ["head_img_url", "candidate_name", "job_position", "candidate_record_status", "interview_count",
                       "interview_way",
                       "interview_dt", "interview_participant", "interview_comment_count", "is_sign",
                       "interview_address", "add_by_name", "sex", "age", "candidate_work_experience", "education",
                       "school", "profession", "latest_work_name", "latest_job", "mobile", "email", "dep_name",
                       "participant", "recruitment_channel", "add_by", "candidate_tags", "remark"],

    # 高级搜索候选人
    "advanced_search": ["head_img_url", "candidate_name", "job_position", "candidate_record_status",
                        "recruitment_channel",
                        "latest_forward_dt", "sex", "age", "candidate_work_experience", "education", "school",
                        "profession", "latest_work_name", "latest_job", "mobile", "email", "dep_name", "participant",
                        "add_by", "candidate_tags", "remark"],

    # 高级搜索人才
    "talent_search": ["head_img_url", "candidate_name", "sex", "age", "candidate_work_experience", "education",
                      "school", "profession",
                      "latest_work_name", "latest_job", "residential_address", "mobile", "email", "expected_salary",
                      "candidate_tags", "remark", "talent_add_by", "talent_join_dt"]
}


class SelectConfig(object):

    default_field_dict = default_config

    custom_group_key = "custom_info"
    custom_group_title = "自定义属性"

    @cached_property
    def system_fields_pool(self):
        return list(HEADER_POOL)

    @cached_property
    def group_map_blank(self):
        return OrderedDict([
            ("person_base_info", {"group_key": "person_base_info", "group_title": "基本信息", "items": []}),
            ("contact_info", {"group_key": "contact_info", "group_title": "联系信息", "items": []}),
            ("job_intention", {"group_key": "job_intention", "group_title": "求职意向", "items": []}),
            ("interview_info",
                {"group_key": "interview_info", "group_title": "面试信息", "items": []}),
            ("employ_info", {"group_key": "employ_info", "group_title": "录用信息", "items": []}),
            ("other_info", {"group_key": "other_info", "group_title": "其他信息", "items": []}),
            (self.custom_group_key,
             {"group_key": self.custom_group_key, "group_title": self.custom_group_title, "items": []})
        ])

    def system_fields(self, company_id=None, ex_group=None, ex_fields=None):  # pylint: disable=unused-argument
        """
        获取系统分类表头字段
        :param company_id: 用来判断是否灰度企业(已废弃灰度企业判断)
        :param ex_group: 排除的分组 (key, ...)
        :param ex_fields: 排除的某些字段 (key, ...)
        :return: list
        """
        ex_group = ex_group or []
        ex_fields = ex_fields or []

        ret = self.system_fields_pool
        if ex_group:
            ret = filter(lambda x: x["group_key"] not in ex_group, ret)     # pylint: disable=deprecated-lambda
        if ex_fields:
            ret = filter(lambda x: x["field_key"] not in ex_fields, ret)    # pylint: disable=deprecated-lambda

        return list(ret)

    def is_fixed_fields(self, ex_group=None, ex_field=None):
        """
        获取固定字段
        :param ex_group: 需要排除的分类
        :param ex_field: 需要排除的字段
        :return: list
        """

        ex_group = ex_group or []
        ex_field = ex_field or []

        return list(filter(      # pylint: disable=deprecated-lambda
            lambda x: x["is_fixed"], self.system_fields(ex_group=ex_group, ex_fields=ex_field)
        ))


select_config = SelectConfig()


#############################################
#   不分类模式
#############################################


class SelectHeaderBase(object):
    field_pool = OrderedDict()
    default_fields = ()

    @classmethod
    def get_field_pool(cls, company_id):    # pylint: disable=unused-argument
        return cls.field_pool

    @classmethod
    def _get_header(cls, company_id, selected: list = None):
        selected = selected or cls.default_fields
        field_pool = cls.get_field_pool(company_id)

        pool_dict = dict(zip([p["field_key"] for p in field_pool], field_pool))
        selected_header = [pool_dict[s] for s in selected if s in pool_dict]

        _diff = set(pool_dict).difference(set(selected))
        unselected_header = [v for v in field_pool if v["field_key"] in _diff]
        return selected_header, unselected_header

    @classmethod
    def get_header_info(cls, company_id, selected: list = None):
        """
        获取表头信息
        @:return  dict --> {"selected_fields": ['已选字段信息'], "system_fields": ['未选字段信息']}
        """
        selected, unselected = cls._get_header(company_id, selected)
        return {
            "selected_fields": selected,
            "system_fields": unselected
        }


class JobPositionHeader(SelectHeaderBase):
    """
    招聘职位选择表头
    """
    field_pool = (
        {"field_name": "职位名称", "field_key": "name", "is_fixed": True, "sortable": True, "order": 1},
        {"field_name": "关联岗位", "field_key": "job_title_name", "is_fixed": False, "sortable": True, "order": 2},
        {"field_name": "用人部门", "field_key": "dep_name", "is_fixed": False, "sortable": True, "order": 3},
        {"field_name": "工作城市", "field_key": "city_name", "is_fixed": False, "sortable": True, "order": 4},
        {"field_name": "招聘人数", "field_key": "position_total", "is_fixed": False, "sortable": True, "order": 5},
        {"field_name": "已入职人数", "field_key": "join_total", "is_fixed": False, "sortable": True, "order": 6},
        {"field_name": "招聘进度", "field_key": "progress_total", "is_fixed": False, "sortable": True, "order": 7},
        {"field_name": "启动日期", "field_key": "start_dt", "is_fixed": False, "sortable": True, "order": 8},
        {"field_name": "截止日期", "field_key": "deadline", "is_fixed": False, "sortable": True, "order": 9},
        {"field_name": "最迟到岗时间", "field_key": "latest_entry_date", "is_fixed": False, "sortable": True, "order": 10},
        {"field_name": "招聘HR", "field_key": "participants_hr", "is_fixed": False, "sortable": True, "order": 11},
        {"field_name": "面试官", "field_key": "participants_employee", "is_fixed": False, "sortable": True, "order": 12},
        {"field_name": "职位类型", "field_key": "job_position_type_name", "is_fixed": False, "sortable": True, "order": 13},
        {"field_name": "工作性质", "field_key": "work_type", "is_fixed": False, "sortable": True, "order": 14},
        {"field_name": "工作地点", "field_key": "work_place_name", "is_fixed": False, "sortable": True, "order": 15},
        {"field_name": "招聘原因", "field_key": "reason", "is_fixed": False, "sortable": True, "order": 16},
        {"field_name": "工作经验要求", "field_key": "work_experience", "is_fixed": False, "sortable": True, "order": 17},
        {"field_name": "学历要求", "field_key": "education", "is_fixed": False, "sortable": True, "order": 18},
        {"field_name": "年龄要求", "field_key": "age_range", "is_fixed": False, "sortable": True, "order": 19},
        {"field_name": "语言要求", "field_key": "language_level", "is_fixed": False, "sortable": True, "order": 20},
        {"field_name": "薪资范围", "field_key": "salary_range", "is_fixed": False, "sortable": True, "order": 21},
        {"field_name": "紧急程度", "field_key": "emergency_level", "is_fixed": False, "sortable": True, "order": 22},
        # {"field_name": "参与内推", "field_key": "support_recommendation", "is_fixed": False, "sortable": True, "order": 23},
        {"field_name": "职位描述", "field_key": "position_description", "is_fixed": False, "sortable": True, "order": 24},
        {"field_name": "应聘登记表", "field_key": "employment_form_name", "is_fixed": False, "sortable": True, "order": 25},
        {"field_name": "创建人", "field_key": "add_by_name", "is_fixed": False, "sortable": True, "order": 26},
        {"field_name": "创建时间", "field_key": "add_dt", "is_fixed": False, "sortable": True, "order": 27}
    )
    default_fields = ("name", "job_title_name", "dep_name", "city_name", "position_total", "join_total",
                      "progress_total", "start_dt", "deadline", "latest_entry_date", "participants_hr",
                      "participants_employee", "job_position_type_name", "work_type", "work_place_name", "reason",
                      "work_experience", "education", "age_range", "language_level", "salary_range", "emergency_level",
                      "employment_form_name", "add_by_name", "add_dt")


class JobPositionStopHeader(SelectHeaderBase):
    field_pool = (
        {"field_name": "职位名称", "field_key": "name", "is_fixed": True, "sortable": True, "order": 1},
        {"field_name": "关联岗位", "field_key": "job_title_name", "is_fixed": False, "sortable": True, "order": 2},
        {"field_name": "用人部门", "field_key": "dep_name", "is_fixed": False, "sortable": True, "order": 3},
        {"field_name": "工作城市", "field_key": "city_name", "is_fixed": False, "sortable": True, "order": 4},
        {"field_name": "招聘人数", "field_key": "position_total", "is_fixed": False, "sortable": True, "order": 5},
        {"field_name": "已入职人数", "field_key": "join_total", "is_fixed": False, "sortable": True, "order": 6},
        {"field_name": "招聘进度", "field_key": "progress_total", "is_fixed": False, "sortable": True, "order": 7},
        {"field_name": "停止招聘日期", "field_key": "stop_dt", "is_fixed": False, "sortable": True, "order": 8},
        {"field_name": "停止招聘原因", "field_key": "stop_reason", "is_fixed": False, "sortable": True, "order": 9},
        {"field_name": "启动日期", "field_key": "start_dt", "is_fixed": False, "sortable": True, "order": 10},
        {"field_name": "截止日期", "field_key": "deadline", "is_fixed": False, "sortable": True, "order": 11},
        {"field_name": "最迟到岗时间", "field_key": "latest_entry_date", "is_fixed": False, "sortable": True, "order": 12},
        {"field_name": "招聘HR", "field_key": "participants_hr", "is_fixed": False, "sortable": True, "order": 13},
        {"field_name": "面试官", "field_key": "participants_employee", "is_fixed": False, "sortable": True, "order": 14},
        {"field_name": "职位类型", "field_key": "job_position_type_name", "is_fixed": False, "sortable": True, "order": 15},
        {"field_name": "工作性质", "field_key": "work_type", "is_fixed": False, "sortable": True, "order": 16},
        {"field_name": "工作地点", "field_key": "work_place_name", "is_fixed": False, "sortable": True, "order": 17},
        {"field_name": "招聘原因", "field_key": "reason", "is_fixed": False, "sortable": True, "order": 18},
        {"field_name": "工作经验要求", "field_key": "work_experience", "is_fixed": False, "sortable": True, "order": 19},
        {"field_name": "学历要求", "field_key": "education", "is_fixed": False, "sortable": True, "order": 20},
        {"field_name": "年龄要求", "field_key": "age_range", "is_fixed": False, "sortable": True, "order": 21},
        {"field_name": "语言要求", "field_key": "language_level", "is_fixed": False, "sortable": True, "order": 22},
        {"field_name": "薪资范围", "field_key": "salary_range", "is_fixed": False, "sortable": True, "order": 23},
        {"field_name": "紧急程度", "field_key": "emergency_level", "is_fixed": False, "sortable": True, "order": 24},
        # {"field_name": "参与内推", "field_key": "support_recommendation", "is_fixed": False, "sortable": True, "order": 25},
        {"field_name": "职位描述", "field_key": "position_description", "is_fixed": False, "sortable": True, "order": 26},
        {"field_name": "停止招聘人", "field_key": "stop_by_name", "is_fixed": False, "sortable": True, "order": 27},
        {"field_name": "应聘登记表", "field_key": "employment_form_name", "is_fixed": False, "sortable": True, "order": 28},
        {"field_name": "创建人", "field_key": "add_by_name", "is_fixed": False, "sortable": True, "order": 29},
        {"field_name": "创建时间", "field_key": "add_dt", "is_fixed": False, "sortable": True, "order": 30}
    )
    default_fields = (
        "name", "job_title_name", "dep_name", "city_name", "position_total", "join_total",
        "progress_total", "stop_dt", "stop_reason", "start_dt", "deadline", "latest_entry_date",
        "participants_hr", "participants_employee", "job_position_type_name", "work_type",
        "work_place_name", "reason", "work_experience", "education", "age_range", "language_level",
        "salary_range", "emergency_level", "employment_form_name", "add_by_name", "add_dt"
    )
