import asyncio
import datetime
import re

from business.configs.b_select_header import SelectHeaderBusiness
from constants import CandidateRecordStatus, ParticipantType, ListDisplayMode, CredentialType, SelectFieldFormType, \
    TalentAssessmentStatus, BgCheckStatus, OfferExamineStatus, OfferStatus
from services import svc
from services.s_dbs.config.s_eliminated_reason import EliminatedReasonService
from services.s_dbs.config.s_interview_infomation import InterviewInformationService
from services.s_dbs.s_candidate import CandidateRemarkService, CandidateTagService, CandidateService, \
    CandidateStandResumeService
from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordForwards
from services.s_dbs.s_common import SchoolService
from services.s_dbs.s_interview import InterviewQueryService, InterViewParticipantService
from services.s_dbs.s_offer_record import OfferSubmitRecord
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService
from services.s_dbs.s_wx_recruitment import RecruitmentPageRecord
from services.s_dbs.s_job_position import JobPositionSelectService, PositionParticipantService
from services.s_es.s_candidate_record_es import CandidateRecordESService
from services.s_https.s_common import get_bg_check_status, get_talent_assessment_status
from services.s_https.s_employee import DepartmentService
from services.s_https.s_ucenter import get_users
from utils.age import calculate_now_year
from utils.qiniu import get_thumb_urls
from utils.search_util import SearchParamsUtils
from utils.secureutils import user_decode
from utils.strutils import uuid2str, str2uuid2str


class CandidateRecordSearchBusiness(object):
    """
    应聘记录搜索业务
    """
    @classmethod
    async def _get_job_position_ids_by_dep_ids(cls, company_id: str, dep_ids: list) -> list:
        """
        通过 部门ids 获取职位ids
        @param company_id: 企业id
        @param dep_ids: 部门列表
        @return:
        """
        if not dep_ids:
            return []

        dep_all_ids = await DepartmentService.get_all_dep_ids(company_id, dep_ids)
        search_params = {
            "is_delete": False,
            "dep_ids": dep_all_ids
        }
        job_positions = await JobPositionSelectService.search_positions(company_id, ['id'], search_params)
        return [job_position.get('id') for job_position in job_positions]

    @classmethod
    async def _get_job_position_ids_by_participant_id(cls, company_id: str, participant_ids: list) -> list:
        """
        通过 招聘hr ids 获取职位ids
        @param company_id:
        @param participant_ids:
        @return:
        """
        if not participant_ids:
            return []

        results = await PositionParticipantService.get_position_ids_by_participants(
            company_id, participant_ids
        )
        position_ids = []
        for key, value in results.items():
            position_ids.extend(value)
        return list(set(position_ids))

    @classmethod
    async def _pre_search(cls,
                          company_id: str,
                          user_id: str,
                          search_params: dict,
                          user_type: int = ParticipantType.HR):
        """
        搜索前置处理
        @param company_id:
        @param user_id:
        @param search_params:
        @param user_type: 用户类型
        @return:
        """
        param_utils = SearchParamsUtils(search_params)

        if user_type == ParticipantType.HR:
            manage_scope_task = svc.manage_scope.hr_manage_scope(company_id=company_id, user_id=user_id)
        else:
            manage_scope_task = svc.manage_scope.emp_manage_scope(company_id=company_id, emp_id=user_id)
        tasks = [
            manage_scope_task,
            cls._get_job_position_ids_by_dep_ids(company_id, param_utils.get_array('dep_ids', is_format_uuid=True)),
            cls._get_job_position_ids_by_participant_id(company_id, param_utils.get_array('participant_id', is_format_uuid=True))
        ]

        manage_scope, dep_job_position_ids, participant_job_position_ids = await asyncio.gather(*tasks)

        if dep_job_position_ids:
            search_params['dep_job_position_ids'] = dep_job_position_ids

        if participant_job_position_ids:
            search_params['participant_job_position_ids'] = participant_job_position_ids

        search_params['permission_job_position_ids'] = manage_scope.get('position_ids', [])
        search_params['permission_candidate_record_ids'] = manage_scope.get('record_ids', [])
        search_params['permission_user_ids'] = [user_id]
        temp_user = manage_scope.get('user_id', None)
        if temp_user:
            search_params['permission_user_ids'].extend([temp_user])

        return search_params

    @classmethod
    async def _post_search(cls,
                           company_id: str,
                           user_id: str,
                           search_params: dict,
                           data: list,
                           user_type: int = ParticipantType.HR) -> list:
        """
        后置搜索处理
        @param company_id: 企业id
        @param user_id: 用户id
        @param search_params:
        @param list: 数据
        @param user_type: 用户类型
        @return:
        """
        param_utils = SearchParamsUtils(search_params)

        fill_biz = CandidateRecordDataFillBusiness(
            company_id,
            param_utils.get_array('permission_user_ids'),
            search_params=search_params,
            data=data,
            user_type=user_type
        )
        await fill_biz.fill_data()
        return fill_biz.result_data

    @classmethod
    async def process_query_config(
            cls, company_id: str, user_id: str, search_params: dict, user_type: int = ParticipantType.HR
    ) -> list:
        """
        获取招聘中列表统计信息
        """
        search_params = await cls._pre_search(
            company_id, user_id, search_params=search_params, user_type=user_type)
        param_utils = SearchParamsUtils(search_params)

        status_config = {
            '初筛': [
                CandidateRecordStatus.PRIMARY_STEP1,
                CandidateRecordStatus.PRIMARY_STEP2
            ],
            '面试': [
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP3
            ],
            '录用': [
                CandidateRecordStatus.EMPLOY_STEP1,
                CandidateRecordStatus.EMPLOY_STEP2,
                CandidateRecordStatus.EMPLOY_STEP3
            ]
        }

        interview_count = param_utils.get_value('interview_count')
        if interview_count:
            status_list1 = [
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP3
            ]
            search_params['status'] = status_list1

            search_params2 = search_params.copy()
            search_params2.pop('interview_count')
            status_list2 = [
                CandidateRecordStatus.PRIMARY_STEP1,
                CandidateRecordStatus.PRIMARY_STEP2,
                CandidateRecordStatus.EMPLOY_STEP1,
                CandidateRecordStatus.EMPLOY_STEP2,
                CandidateRecordStatus.EMPLOY_STEP3
            ]
            search_params2['status'] = status_list2
            tasks = [
                CandidateRecordESService.get_status_total(
                    company_id, search_params),
                CandidateRecordESService.get_status_total(
                    company_id, search_params2)
            ]
            status, status2 = await asyncio.gather(*tasks)
            status.update(status2)

        else:
            status_list = [
                CandidateRecordStatus.PRIMARY_STEP1,
                CandidateRecordStatus.PRIMARY_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP3,
                CandidateRecordStatus.EMPLOY_STEP1,
                CandidateRecordStatus.EMPLOY_STEP2,
                CandidateRecordStatus.EMPLOY_STEP3
            ]
            search_params['status'] = ','.join([str(status) for status in status_list])
            status = await CandidateRecordESService.get_status_total(
                company_id, search_params)

        configs = []
        for son in status_config:
            son_configs = []
            for item in status_config[son]:
                config = {
                    'status': item,
                    'title': CandidateRecordStatus.attrs_.get(item),
                    'value': status.get(item, 0)
                }
                son_configs.append(config)
            configs.append({
                "title": son,
                "configs": son_configs
            })

        return configs

    @classmethod
    async def search(
            cls, company_id: str, user_id: str, search_params: dict, user_type: int = ParticipantType.HR
    ) -> dict:
        """
        获取招聘中列表信息
        """
        search_params = await cls._pre_search(
            company_id, user_id, search_params=search_params, user_type=user_type)

        param_utils = SearchParamsUtils(search_params)
        count, data = await CandidateRecordESService.get_list(
            company_id, search_params)

        data = await cls._post_search(
            company_id, user_id, search_params=search_params, data=data, user_type=user_type)

        limit = param_utils.get_int('limit', 10)
        p = param_utils.get_int('p', 1)
        return {
            'limit': limit,
            'p': p,
            'total_count': count,
            'offset': (p - 1) * limit,
            'totalpage': (count + limit - 1) // limit,
            'objects': data
        }


class CandidateRecordDataFillBusiness(object):
    """
    应聘记录数据填充业务
    """
    CARD_PUBLIC_FIELD = [
        'id', 'candidate_id', 'candidate_record_id', 'candidate_name', 'candidate_form_id', 'email',
        'candidate_record_status', 'job_position', 'dep_name', 'recruitment_channel', 'remark',
        'form_status', 'talent_assessment_status', 'bg_check_status', 'approval_status',
        'latest_forward_dt', 'candidate_tags', 'sex', 'avatar', 'school_label', 'talent_is_join',
        'talent_join_dt', 'school', 'candidate_work_experience', 'education', 'age', 'expected_city',
        'expected_salary', 'mobile', 'referee_mobile', 'referee_name', 'recruitment_channel',
        'wework_external_contact',
    ]
    LIST_PUBLIC_FIELD = [
        'id', 'candidate_id', 'candidate_record_id', 'candidate_record_status', 'mobile', 'avatar',
        'referee_mobile', 'referee_name', 'recruitment_channel', 'candidate_form_id', 'email',
        'talent_assessment_status', 'sex', 'wework_external_contact', 'talent_is_join'
    ]
    # 应聘记录阶段所使用字段关系配置
    CONFIG_PRIMARY_STEP1 = {
        'default': LIST_PUBLIC_FIELD,
        'card': CARD_PUBLIC_FIELD + [
            'latest_work_name', 'latest_job', 'profession'
        ]
    }
    CONFIG_PRIMARY_STEP2 = CONFIG_PRIMARY_STEP1
    CONFIG_PRIMARY_STEP3 = {
        'default': LIST_PUBLIC_FIELD,
        'card': CARD_PUBLIC_FIELD + [
            'latest_work_name', 'latest_job', 'profession', 'eliminated_reason'
        ]
    }
    # 面试阶段
    CONFIG_INTERVIEW_STEP1 = {
        'default': LIST_PUBLIC_FIELD,
        'card': CARD_PUBLIC_FIELD + [
            'interview_count', 'interview_dt', 'interview_way', 'invitation_status',
            'interview_participant', 'interview_comment_count', 'is_sign'
        ]
    }
    CONFIG_INTERVIEW_STEP2 = CONFIG_INTERVIEW_STEP1
    CONFIG_INTERVIEW_STEP3 = {
        'default': LIST_PUBLIC_FIELD,
        'card': CARD_PUBLIC_FIELD + [
            'interview_count', 'interview_dt', 'interview_way', 'invitation_status',
            'interview_participant', 'interview_comment_count'
        ]
    }
    CONFIG_INTERVIEW_STEP4 = {
        'default': LIST_PUBLIC_FIELD,
        'card': CARD_PUBLIC_FIELD + [
            'interview_count', 'interview_dt', 'interview_way', 'invitation_status',
            'interview_participant', 'interview_comment_count', 'eliminated_reason'
        ]
    }
    # 录用阶段
    CONFIG_EMPLOY_STEP1 = {
        'default': LIST_PUBLIC_FIELD + ['offer_id'],
        'card': CARD_PUBLIC_FIELD + [
            'job_title_name', 'offer_dep_name', 'hire_date', 'offer_status',
            'offer_add_by', 'offer_add_dt', 'offer_id'
        ]
    }
    CONFIG_EMPLOY_STEP2 = CONFIG_EMPLOY_STEP1
    CONFIG_EMPLOY_STEP3 = {
        'default': LIST_PUBLIC_FIELD + ['intention_emp_id', 'offer_id'],
        'card': CARD_PUBLIC_FIELD + [
            'job_title_name', 'offer_dep_name', 'hire_date', 'offer_status',
            'offer_add_by', 'offer_add_dt', 'offer_id', 'intention_emp_id'
        ]
    }
    CONFIG_EMPLOY_STEP4 = {
        'default': LIST_PUBLIC_FIELD + ['employee_id', 'offer_id'],
        'card': CARD_PUBLIC_FIELD + [
            'job_title_name', 'offer_dep_name', 'hire_date', 'offer_status',
            'offer_add_by', 'offer_add_dt', 'offer_id', 'employee_id'
        ]
    }
    CONFIG_EMPLOY_STEP5 = {
        'default': LIST_PUBLIC_FIELD + ['offer_id'],
        'card': CARD_PUBLIC_FIELD + [
            'job_title_name', 'offer_dep_name', 'hire_date', 'offer_status',
            'offer_add_by', 'offer_add_dt', 'offer_id', 'eliminated_reason'
        ]
    }

    CONFIG_STATUS = {
        CandidateRecordStatus.PRIMARY_STEP1: CONFIG_PRIMARY_STEP1,
        CandidateRecordStatus.PRIMARY_STEP2: CONFIG_PRIMARY_STEP2,
        CandidateRecordStatus.PRIMARY_STEP3: CONFIG_PRIMARY_STEP3,

        CandidateRecordStatus.INTERVIEW_STEP1: CONFIG_INTERVIEW_STEP1,
        CandidateRecordStatus.INTERVIEW_STEP2: CONFIG_INTERVIEW_STEP2,
        CandidateRecordStatus.INTERVIEW_STEP3: CONFIG_INTERVIEW_STEP3,
        CandidateRecordStatus.INTERVIEW_STEP4: CONFIG_INTERVIEW_STEP4,

        CandidateRecordStatus.EMPLOY_STEP1: CONFIG_EMPLOY_STEP1,
        CandidateRecordStatus.EMPLOY_STEP2: CONFIG_EMPLOY_STEP2,
        CandidateRecordStatus.EMPLOY_STEP3: CONFIG_EMPLOY_STEP3,
        CandidateRecordStatus.EMPLOY_STEP4: CONFIG_EMPLOY_STEP4,
        CandidateRecordStatus.EMPLOY_STEP5: CONFIG_EMPLOY_STEP5
    }

    # 应聘记录阶段所使用字段表关系配置
    CONFIG_TABLES = {
        'default': ['mobile', 'form_status', 'offer_add_dt', 'latest_job', 'add_by', 'expected_salary',
                    'candidate_record_id', 'sex', 'latest_work_name', 'education',
                    'offer_status', 'profession', 'school', 'candidate_record_status', 'age',
                    'candidate_work_experience', 'interview_count', 'candidate_name', 'candidate_id', 'email',
                    'id', 'eliminated_dt', 'residential_address', 'add_dt', 'entry_form_status', 'intention_emp_id',
                    'candidate_form_id', 'employee_id', 'referee_name', 'referee_mobile', 'job_title_name',
                    'offer_add_by', 'offer_id', 'offer_dep_name', 'is_read', 'hire_date'],
        'candidate': ['talent_join_dt', 'avatar', 'talent_is_join', 'talent_add_by', 'wework_external_contact'],
        'stand_resume': ['expected_city', 'credentials_type', 'credentials_no', 'bg_check_status'],
        'interview': ['interview_id', 'is_sign', 'invitation_status', 'interview_dt', 'interview_way',
                      'group_interview_id', 'add_by_name', 'read_invitation', 'interview_address',
                      'interview_linkname', 'interview_comment_count', 'interview_participant'],
        'job_position': ['dep_name', 'job_position'],
        'job_position_participant': ['participant'],
        'candidate_record_forwards': ['latest_forward_dt'],
        'talent_assessment_status': ['talent_assessment_status'],
        'remark': ['remark'],
        'approval': ['approval_no', 'approval_status'],
        'tag': ['candidate_tags'],
        'eliminated_reason': ['eliminated_reason'],
        'recruitment_channel': ['recruitment_channel'],
        'recruitment_page': ['recruitment_page_name']
    }

    async def _get_fields(self, status: int, display: int, scene_type: int):
        config = self.CONFIG_STATUS.get(status, {})
        if display == ListDisplayMode.CARD:
            return config.get('card')
        fields = config.get('default')

        ret = await SelectHeaderBusiness.get_selected_fields_list(
            self.company_id, self.user_ids[0], scene_type, user_type=self.user_type
        )

        fields.extend(ret)

        return list(set(fields))

    def _analyse_table_fields(self, fields: list) -> dict:
        """
        分析表和字段
        """
        results = {}
        for table, table_fields in self.CONFIG_TABLES.items():
            temp_fields = list(set(fields).intersection(set(table_fields)))
            if temp_fields:
                results[table] = temp_fields
        # 处理自定义字段
        custom_fields = [field for field in fields if field.startswith("field_")]
        if custom_fields:
            stand_resume_fields = results.get('stand_resume', [])
            stand_resume_fields.extend(custom_fields)
            results['stand_resume'] = stand_resume_fields
        return results

    def __init__(self, company_id: str, user_ids: list, search_params: dict,
                 data: list, user_type: int = ParticipantType.HR):
        self.company_id = company_id
        self.user_ids = user_ids
        self.search_params = SearchParamsUtils(search_params)
        self.data = data
        self.result_data = [{'id': item.get('id'), 'candidate_id': item.get('candidate_id')} for item in data]
        self.user_type = user_type

    async def fill_data(self):
        fields = await self._get_fields(
            self.search_params.get_int('status', CandidateRecordStatus.PRIMARY_STEP1),
            self.search_params.get_int('display', ListDisplayMode.CARD),
            self.search_params.get_int('scene_type', SelectFieldFormType.screen_to_be)
        )

        fill_table = self._analyse_table_fields(fields)

        tasks = []
        for table_name, table_fields in fill_table.items():
            fill_func = getattr(self, 'fill_%s' % table_name)
            tasks.append(
                fill_func(table_fields)
            )

        await asyncio.gather(*tasks)

    async def fill_default(self, table_fields: list):
        mapping_config = {
            'candidate_record_id': 'id',
            'candidate_record_status': 'status',
            'candidate_name': 'name',
            'add_by': 'add_by_id',
            'hire_date': 'offer_hire_dt',
            'entry_form_status': 'entry_sign_id'
        }
        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            for field in table_fields:
                if field == 'expected_salary':
                    salary_min = org_item.get('salary_min', None)
                    salary_max = org_item.get('salary_max', None)
                    if salary_max is None and salary_min is None:
                        item['expected_salary'] = []
                    else:
                        if salary_min is None:
                            salary_min = -1
                        if salary_max is None:
                            salary_max = -1
                        item['expected_salary'] = [salary_min, salary_max]
                elif field == 'latest_work_name':
                    latest_company = org_item.get('latest_company', [])
                    item['latest_work_name'] = latest_company[0] if latest_company else ''
                elif field == 'age':
                    birthday = org_item.get('birthday', None)
                    if birthday:
                        item['age'] = calculate_now_year(birthday)
                    else:
                        item['age'] = None
                elif field == 'candidate_work_experience':
                    work_experience = org_item.get('work_experience', None)
                    if work_experience:
                        item['candidate_work_experience'] = calculate_now_year(work_experience)
                    else:
                        item['candidate_work_experience'] = None
                elif field in mapping_config.keys():
                    item[field] = org_item.get(mapping_config.get(field), None)
                else:
                    item[field] = org_item.get(field, None)

        if 'school' in table_fields:
            school_names = list(set([item.get('school') for item in self.data if item.get('school', None)]))
            school_datas = await SchoolService.get_school_by_ids(school_names)
            school_list = {}
            for school in school_datas:
                school_list[school.name] = school.label

            for idx, org_item in enumerate(list(self.data)):
                item = self.result_data[idx]
                school_label = school_list.get(org_item.get('school'), None)
                if school_label:
                    if school_label == 1:
                        item['school_label'] = ['985工程', '211工程']
                    elif school_label == 2:
                        item['school_label'] = ['211工程']
                    elif school_label == 4:
                        item['school_label'] = ['虚假大学']
                else:
                    item['school_label'] = []

        user_ids = []
        if 'add_by' in table_fields:
            user_ids.extend(list(set([item.get('add_by') for item in self.result_data
                                      if item.get('add_by', None) and item.get('add_by') != '00000000000000000000000000000000'])))
        if 'offer_add_by' in table_fields:
            user_ids.extend(list(set([item.get('offer_add_by') for item in self.result_data
                                      if item.get('offer_add_by', None) and item.get('offer_add_by') != '00000000000000000000000000000000'])))

        if 'add_by' in table_fields or 'offer_add_by' in table_fields:
            user_datas = await get_users(user_ids)
            results = {}
            for user in user_datas:
                results[uuid2str(user.get('id', None))] = user.get('nickname')
            for item in self.result_data:
                if 'add_by' in table_fields:
                    user_id = item.get('add_by', None)
                    if user_id and user_id != '00000000000000000000000000000000':
                        item['add_by'] = results.get(user_id)
                    else:
                        item['add_by'] = None
                if 'offer_add_by' in table_fields:
                    user_id = item.get('offer_add_by', None)
                    if user_id and user_id != '00000000000000000000000000000000':
                        item['offer_add_by'] = results.get(user_id)
                    else:
                        item['offer_add_by'] = None

        # 产品恶心的逻辑， 当 offer 状态为 0 时， 不显示 offer_add_dt 和 offer_add_by
        for item in self.result_data:
            if item.get('offer_status', None) == OfferStatus.none:
                item['offer_add_by'] = None
                item['offer_add_dt'] = None

    async def fill_candidate(self, table_fields: list):
        mapping_config = {
            'talent_is_join': 'talent_is_join',
            'wework_external_contact': 'wework_external_contact'
        }
        candidate_ids = list(set([item.get('candidate_id') for item in self.result_data]))

        datas = await CandidateService.get_candidates(
            company_id=self.company_id, candidate_ids=candidate_ids)

        results = {}
        for candidate in datas:
            results[candidate.id] = dict(candidate)

        avatar_map = {}
        if 'avatar' in table_fields:
            avatar_keys = []
            for key, item in results.items():
                if item.get('avatar', None):
                    avatar_keys.append(item.get('avatar', None))
            if avatar_keys:
                avatar_map = await get_thumb_urls(avatar_keys)

        for idx, org_item in enumerate(list(self.result_data)):
            item = self.result_data[idx]
            result = results.get(item.get('candidate_id', None), {})
            if result:
                for field in table_fields:
                    if field == 'talent_join_dt':
                        talent_join_dt = result.get('talent_join_dt', '')
                        if talent_join_dt and talent_join_dt > datetime.datetime(2016, 1, 1):
                            item['talent_join_dt'] = talent_join_dt
                        else:
                            item['talent_join_dt'] = None
                    elif field == 'talent_add_by':
                        talent_add_by = result.get('talent_join_by_id', '')
                        if talent_add_by and talent_add_by != '00000000000000000000000000000000':
                            item['talent_add_by'] = talent_add_by
                        else:
                            item['talent_add_by'] = None
                    elif field == 'avatar':
                        if result.get('avatar', None):
                            item['avatar'] = avatar_map.get(result['avatar']) or ''
                        else:
                            item['avatar'] = None
                    elif field in mapping_config.keys():
                        item[field] = result.get(mapping_config.get(field), None)
                    else:
                        item[field] = result.get(field, None)

        if 'talent_add_by' in table_fields:
            user_ids = list(set([item.get('talent_add_by') for item in self.result_data if item.get('talent_add_by', None)]))
            user_datas = await get_users(user_ids)
            results = {}
            for user in user_datas:
                results[uuid2str(user.get('id', None))] = user.get('nickname')
            for item in self.result_data:
                user_id = item.get('talent_add_by', None)
                if user_id and user_id != '00000000000000000000000000000000':
                    item['talent_add_by'] = results.get(user_id)
                else:
                    item['talent_add_by'] = None

    async def fill_stand_resume(self, table_fields: list):
        candidate_record_ids = list(set([item.get('id') for item in self.result_data]))

        results = await CandidateStandResumeService.get_stand_resume_data(
            company_id=self.company_id, candidate_record_ids=candidate_record_ids)

        bg_check_status = []
        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(item.get('id', None), {})
            for field in table_fields:
                if field == 'credentials_no':
                    item['credentials_no'] = user_decode(result.get('credentials_no', None))
                else:
                    item[field] = result.get(field, None)

            if 'bg_check_status' in table_fields:
                credentials_type = result.get('credentials_type', None)
                if credentials_type and credentials_type == CredentialType.ID:
                    credentials_no = user_decode(result.get('credentials_no', None))
                    if credentials_no:
                        bg_check_status.append({
                            'id': item.get('id', None),
                            'name': org_item.get('name', None),
                            'credentials_no': credentials_no
                        })

        # 处理背调状态
        if 'bg_check_status' in table_fields:
            bg_check_status_data = await get_bg_check_status(self.company_id, bg_check_status)
            for idx, org_item in enumerate(list(self.data)):
                item = self.result_data[idx]
                result = bg_check_status_data.get(item.get('id', None), BgCheckStatus.unsent)
                item['bg_check_status'] = result

    async def fill_interview(self, table_fields: list):
        mapping_config = {
            'interview_id': 'id',
            'add_by_name': 'add_by_id'
        }
        candidate_record_ids = list(set([item.get('id') for item in self.result_data]))
        is_interview_pariticipant = False
        interview_pariticipant_results = {}

        interview_information_task = None
        interview_information_results = {}

        if set(['interview_address', 'interview_linkname']).intersection(table_fields):
            interview_information_task = InterviewInformationService.get_company_data(self.company_id)
        if set(['interview_comment_count', 'interview_participant']).intersection(table_fields):
            is_interview_pariticipant = True

        interview_task = InterviewQueryService.get_interviews_by_cdr_ids(
            self.company_id, candidate_record_ids,
            fields=['id', 'candidate_record_id', 'interview_information_id', 'add_by_id', 'is_sign',
                    'invitation_status', 'interview_dt', 'interview_way', 'group_interview_id',
                    'read_invitation'], is_latest=True, is_delete=False
        )

        if interview_information_task:
            interview_datas, interview_information_datas = await asyncio.gather(
                interview_task, interview_information_task
            )
            for interview_information in interview_information_datas:
                interview_information_results[interview_information.get('id')] = interview_information
        else:
            interview_datas = await interview_task

        results = {}
        for interview in interview_datas:
            results[interview.get('candidate_record_id')] = interview

        if is_interview_pariticipant:
            interview_ids = [interview.get('id') for interview in interview_datas]
            if interview_ids:
                interview_pariticipant_results = await InterViewParticipantService.get_participant_by_interview_ids(
                    self.company_id, interview_ids
                )

        for idx, org_item in enumerate(list(self.result_data)):
            item = self.result_data[idx]
            result = results.get(item.get('id', None), {})
            item['interview_id'] = result.get('id', None)
            for field in table_fields:
                if field == 'interview_dt':
                    item['interview_dt'] = result.get('interview_dt', '')
                elif field in ['interview_address', 'interview_linkname']:
                    interview_information = interview_information_results.get(result.get('interview_information_id', None), {})
                    item['interview_address'] = interview_information.get('address', None)
                    item['interview_linkname'] = interview_information.get('linkman', None)
                elif field == 'interview_comment_count':
                    participants = interview_pariticipant_results.get(result.get('id', None), [])
                    count = 0
                    is_show_comment = False
                    for participant in participants:
                        is_comment = participant.is_comment
                        if is_comment:
                            count = count + 1
                        participant_refer_id = participant.participant_refer_id
                        if participant_refer_id in self.user_ids and not is_comment:
                            is_show_comment = True

                    item['interview_comment_count'] = count
                    item['interview_is_comment'] = is_show_comment
                elif field == 'interview_participant':
                    participants = interview_pariticipant_results.get(result.get('id', None), [])
                    item['interview_participant'] = []
                    for p in participants:
                        p_dict = {
                            "id": p.id,
                            "participant_refer_id": p.participant_refer_id,
                            "name": p.name,
                            "interview_type": p.participant_type,
                            "participant_id": p.participant_id
                        }
                        if p.participant_type == 1:
                            item['interview_participant'].insert(0, p_dict)
                        else:
                            item['interview_participant'].append(p_dict)
                elif field in mapping_config.keys():
                    item[field] = result.get(mapping_config.get(field), None)
                else:
                    item[field] = result.get(field, None)

        if 'add_by_name' in table_fields:
            user_ids = list(set([item.get('add_by_name') for item in self.result_data
                                 if item.get('add_by_name', None) and item.get('add_by_name') != '00000000000000000000000000000000']))
            user_datas = await get_users(user_ids)
            results = {}
            for user in user_datas:
                results[uuid2str(user.get('id', None))] = user.get('nickname')
            for item in self.result_data:
                user_id = item.get('add_by_name', None)
                if user_id and user_id != '00000000000000000000000000000000':
                    item['add_by_name'] = results.get(user_id)
                else:
                    item['add_by_name'] = None

    async def fill_job_position(self, table_fields: list):
        job_position_ids = list(set([item.get('job_position_id') for item in self.data]))
        results = await JobPositionSelectService.get_position_by_ids_cache(self.company_id, job_position_ids)
        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(org_item.get('job_position_id', None), {})
            for field in table_fields:
                if field == 'dep_name':
                    item[field] = result.get('dep_name', None)
                elif field == 'job_position':
                    item[field] = {
                        'dep_id': str2uuid2str(result.get('dep_id', None)),
                        'dep_name': result.get('dep_name', None),
                        'id': str2uuid2str(result.get('id', None)),
                        'job_title_id': str2uuid2str(result.get('job_title_id', None)),
                        'job_title_name': result.get('job_title_name', None),
                        'name': result.get('name', None),
                        'status': result.get('status', None),
                        'work_place_id': str2uuid2str(result.get('work_place_id', None)),
                        'work_place_name': result.get('work_place_name', None),
                        'work_type': result.get('work_type', None)
                    }

    async def fill_job_position_participant(self, table_fields: list):
        job_position_ids = list(set([item.get('job_position_id') for item in self.data]))
        results = await PositionParticipantService.get_participant_by_position_ids(
            job_position_ids, ["id", "name", "participant_refer_id"]
        )
        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(org_item.get('job_position_id', None), {})
            for field in table_fields:
                if field == 'participant':
                    item[field] = {
                        'participants_hr': [{
                            'id': r.get('id', None),
                            'name': r.get('name', None),
                            'participant_refer_id': r.get('participant_refer_id', None)
                        } for r in result],
                        'participants_employee': []
                    }

    async def fill_candidate_record_forwards(self, table_fields: list):
        candidate_record_ids = list(set([item.get('id') for item in self.result_data]))
        results = await CandidateRecordForwards.get_forward_records_for_me(
            self.company_id,
            candidate_record_ids,
            self.user_ids
        )

        for idx, org_item in enumerate(list(self.result_data)):
            item = self.result_data[idx]
            result = results.get(item.get('id', None), {})
            if result:
                log_desc = result.get('log_desc')
                comment = result.get('comment')
                basic_log_desc = re.findall(r'.+于\d{4}-\d{2}-\d{2} \d{2}:\d{2}转发', log_desc)
                if len(basic_log_desc) == 1:
                    basic_log_desc = basic_log_desc[0]
                else:
                    basic_log_desc = ""
                item['latest_forward_dt'] = {
                    'basic_log_desc': basic_log_desc,
                    'log_desc': log_desc,
                    'comment': comment
                }
            else:
                item['latest_forward_dt'] = {}

    async def fill_remark(self, table_fields: list):
        candidate_id = list(set([item.get('candidate_id') for item in self.result_data]))

        results = await CandidateRemarkService.get_latest_remark(
            company_id=self.company_id, candidate_ids=candidate_id)
        for idx, org_item in enumerate(list(self.result_data)):
            item = self.result_data[idx]
            result = results.get(item.get('candidate_id', None), {})
            if result:
                item['remark'] = [{
                    'id': result.get('id', None),
                    'text': result.get('text', None)
                }]
            else:
                item['remark'] = []

    async def fill_talent_assessment_status(self, table_fields: list):
        talent_assessment_status = []
        for item in self.data:
            name = item.get('name', None)
            mobile = item.get('mobile', None)
            if name and mobile:
                talent_assessment_status.append({
                    'id': item.get('id', None),
                    'name': name,
                    'mobile': mobile
                })

        talent_assessment_status_data = await get_talent_assessment_status(self.company_id, talent_assessment_status)
        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = talent_assessment_status_data.get(item.get('id', None), TalentAssessmentStatus.unsent)
            item['talent_assessment_status'] = result

    async def fill_approval(self, table_fields: list):
        mapping_config = {
            'approval_no': 'submit_no',
        }
        candidate_record_ids = list(set([item.get('id') for item in self.result_data]))

        results = await OfferSubmitRecord.get_offer_submit_by_candidate_record_ids(
            self.company_id, candidate_record_ids)

        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(org_item.get('id', {}), {})
            item['approval_id'] = result.get('submit_id', None)
            for field in table_fields:
                if field == 'approval_status':
                    status = result.get('status', OfferExamineStatus.UN_SEND)
                    item['approval_status'] = OfferExamineStatus.attrs_[status]
                elif field in mapping_config.keys():
                    item[field] = result.get(mapping_config.get(field), None)
                else:
                    item[field] = result.get(field, None)

    async def fill_tag(self, table_fields: list):
        tag_ids = []
        for org_item in self.data:
            tag_ids.extend(org_item.get('tag_list', []))

        tag_data = await CandidateTagService.get_tags(self.company_id, list(set(tag_ids)))

        tags = {}
        for tag in tag_data:
            tags[tag.id] = {
                'id': tag.id,
                'name': tag.name
            }

        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            results = []
            for tag in org_item.get('tag_list', []):
                tag_name = tags.get(tag, None)
                if tag_name:
                    results.append(tag_name)

            item['candidate_tags'] = results

    async def fill_eliminated_reason(self, table_fields: list):
        datas = await EliminatedReasonService.get_all(company_id=self.company_id, filter_deleted=False)
        results = {}
        for data in datas:
            results[data.get('id')] = data

        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(org_item.get('eliminated_reason_id', None), {})
            if result:
                item['eliminated_reason'] = result.get('reason', None)
            else:
                item['eliminated_reason'] = None

    async def fill_recruitment_channel(self, table_fields: list):
        datas = await RecruitmentChannelService.get_channel_list(
            company_id=self.company_id, fields=[])

        results = {}
        for data in datas:
            results[data.id] = data

        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(org_item.get('recruitment_channel_id', None), None)
            if result:
                item['recruitment_channel'] = {
                    'id': result.id,
                    'name': result.name,
                    'show_color': result.show_color,
                    'is_system': result.is_system
                }
            else:
                item['recruitment_channel'] = None

    async def fill_recruitment_page(self, table_fields: list):
        candidate_record_ids = list(set([item.get('id') for item in self.data]))

        datas = await RecruitmentPageRecord.get_candidate_record_all(
            self.company_id, candidate_record_ids)

        results = {}
        for data in datas:
            results[data.get('candidate_record_id')] = data

        for idx, org_item in enumerate(list(self.data)):
            item = self.result_data[idx]
            result = results.get(org_item.get('id', None), None)
            if result:
                item['recruitment_page_id'] = result.id
                item['recruitment_page_name'] = result.name
            else:
                item['recruitment_page_id'] = None
                item['recruitment_page_name'] = None
