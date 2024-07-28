import logging
import traceback

from configs import config
from constants import OfferStatus
from drivers.es import es
from elasticsearch_dsl import Search, Q

from kits import ToModel
from misc.notifier import Notifier
from utils import esutils
from utils.search_util import SearchParamsUtils
from utils.strutils import uuid2str


logger = logging.getLogger('app')


class OldCandidateRecordESService:
    INDEX = 'recruitment_search'

    @classmethod
    def basic_search(cls,
                     company_id: str,
                     permission_job_position_ids: list,
                     permission_candidate_record_ids: list,
                     status: list = None,
                     job_position_ids: list = None,
                     add_date: list = None):
        """
        基础搜索
        @param company_id: 企业id
        @param permission_job_position_ids: 用户权限/招聘职位ids
        @param permission_candidate_record_ids: 用户权限/应聘记录ids
        @param status: 筛选条件/状态列表[状态1, 状态2]， 为空则不筛选
        @param job_position_ids: 筛选条件/职位ids[职位1, 职位2]， 为空则不筛选
        @param add_date: 筛选条件/添加日期[开始日期, 结束日期]， 为空则不筛选
        @return:
        """
        search = Search()

        query = Q(
            "term", candidate_parent="candidate_record") & Q(
            "term", c_company_id=company_id) & Q(
            "term", c_is_delete=False)

        if permission_job_position_ids or permission_candidate_record_ids:
            query = query & (
                    Q("terms", c_job_position_id=permission_job_position_ids) |
                    Q("terms", c_id=permission_candidate_record_ids)
            )

        if job_position_ids:
            query = query & Q("terms", c_job_position_id=job_position_ids)

        if status:
            query = query & Q("terms", c_status=status)

        if add_date and len(add_date) == 2:
            query = query & Q("range", c_add_dt=cls.format_date_range(add_date))

        search = search.query(query)

        return search

    @classmethod
    def format_date_range(cls, add_dt):
        start_date = add_dt[0]
        end_date = add_dt[1]
        result = {}
        if start_date:
            result['gte'] = start_date
        if end_date:
            result['lte'] = end_date

        result['format'] = "yyyy-MM-dd"
        result['time_zone'] = "+08:00"
        return result

    @classmethod
    async def get_status_total(cls,
                               company_id: str,
                               permission_job_position_ids: list,
                               permission_candidate_record_ids: list,
                               status: list) -> dict:
        """
        获取应聘记录统计数据 - 状态维度
        @param company_id: 企业id
        @param permission_job_position_ids: 用户权限/招聘职位ids
        @param permission_candidate_record_ids: 用户权限/应聘记录ids
        @param status: 筛选条件/状态列表[状态1, 状态2]， 为空则不筛选
        @return: {"状态1": 总数, "状态2": 总数}
        """
        search = cls.basic_search(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            status=status
        )
        search.aggs.bucket("status", "terms", field="c_status")
        client = await es.default_es
        result = await client.search(search.to_dict(), index=cls.INDEX, size=0,
                                     filter_path='aggregations.status.buckets', track_total_hits=True)
        total = {}
        for item in result.get('aggregations', {}).get('status', {}).get('buckets', []):
            total[item.get('key')] = item.get('doc_count')

        return total

    @classmethod
    async def get_job_position_total(cls,
                                     company_id: str,
                                     permission_job_position_ids: list,
                                     permission_candidate_record_ids: list,
                                     job_position_ids: list,
                                     status: list,
                                     add_date: list = []) -> dict:
        """
        获取应聘记录统计数据 - 职位纬度
        @param company_id: 企业id
        @param permission_job_position_ids: 用户权限/招聘职位ids
        @param permission_candidate_record_ids: 用户权限/应聘记录ids
        @param job_position_ids: 筛选条件/职位ids[职位1, 职位2]， 为空则不筛选
        @param status: 筛选条件/状态列表[状态1, 状态2]， 为空则不筛选
        @param add_date: 筛选条件/添加日期[开始日期, 结束日期]， 为空则不筛选
        @return: {"状态1": 总数, "状态2": 总数}
        """
        search = cls.basic_search(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            job_position_ids=job_position_ids,
            status=status,
            add_date=add_date
        )
        search.aggs.bucket("job_position", "terms", field="c_job_position_id")
        client = await es.default_es
        result = await client.search(search.to_dict(), index=cls.INDEX, size=0,
                                     filter_path='aggregations.job_position.buckets', track_total_hits=True)
        total = {}
        for item in result.get('aggregations', {}).get('job_position', {}).get('buckets', []):
            total[item.get('key')] = item.get('doc_count')

        return total

    @classmethod
    async def get_count(cls,
                        company_id: str,
                        permission_job_position_ids: list,
                        permission_candidate_record_ids: list,
                        job_position_ids: list = [],
                        status: list = [],
                        add_date: list = []) -> int:
        """
        应聘记录数量统计
        @param company_id: 企业id
        @param permission_job_position_ids: 用户权限/招聘职位ids
        @param permission_candidate_record_ids: 用户权限/应聘记录ids
        @param job_position_ids: 筛选条件/职位ids[职位1, 职位2]， 为空则不筛选
        @param status: 筛选条件/状态列表[状态1, 状态2]， 为空则不筛选
        @param add_date: 筛选条件/添加日期[开始日期, 结束日期]， 为空则不筛选
        @return: 总数
        """
        search = cls.basic_search(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            job_position_ids=job_position_ids,
            status=status,
            add_date=add_date
        )

        client = await es.default_es
        result = await client.count(search.to_dict(), index=cls.INDEX, filter_path='count')

        return result.get('count', 0)


class CandidateRecordESService:
    INDEX = 'recruitment_candidate_record'

    @classmethod
    def basic_search(cls, company_id: str, search_params: dict):
        """
        基础搜索
        @param company_id: 企业id
        @param search_params: 筛选条件数据
        @return:
        """
        param_utils = SearchParamsUtils(search_params)
        search = Search()

        query = Q(
            "term", company_id=company_id) & Q(
            "term", is_delete=False) & ~Q(
            "term", c_status=8)

        permission_job_position_ids = param_utils.get_value('permission_job_position_ids', [])
        permission_candidate_record_ids = param_utils.get_value('permission_candidate_record_ids', [])
        if permission_candidate_record_ids is not None or permission_job_position_ids is not None:
            query = query & (
                    Q("terms", job_position_id=permission_job_position_ids) |
                    Q("terms", id=permission_candidate_record_ids)
            )

        job_position_ids = param_utils.get_array('job_position_ids', is_format_uuid=True)
        if job_position_ids is not None:
            query = query & Q("terms", job_position_id=job_position_ids)

        dep_job_position_ids = param_utils.get_array('dep_job_position_ids', is_format_uuid=True)
        if dep_job_position_ids is not None:
            query = query & Q("terms", job_position_id=dep_job_position_ids)

        participant_job_position_ids = param_utils.get_array('participant_job_position_ids', is_format_uuid=True)
        if participant_job_position_ids:
            query = query & Q("terms", job_position_id=participant_job_position_ids)

        status = param_utils.get_array('status')
        if status is not None:
            query = query & Q("terms", status=status)

        sex = param_utils.get_array('sex')
        if sex is not None:
            query = query & Q("terms", sex=sex)

        age = param_utils.num_date_query('age')
        if age is not None:
            query = query & Q("range", birthday=age)

        work_experience = param_utils.num_date_query('work_experience')
        if work_experience is not None:
            query = query & Q("range", work_experience=work_experience)

        education = param_utils.get_array('education')
        if education is not None:
            query = query & Q("terms", education=education)

        school = param_utils.get_value('school')
        if school is not None:
            query = query & Q("wildcard", school="*{}*".format(school))

        profession = param_utils.get_value('profession')
        if profession is not None:
            query = query & Q("wildcard", profession="*{}*".format(profession))

        last_company = param_utils.get_value('last_company')
        if last_company is not None:
            query = query & Q("wildcard", latest_company="*{}*".format(last_company))

        last_job_position = param_utils.get_value('last_job_position')
        if last_job_position is not None:
            query = query & Q("wildcard", work_job_list="*{}*".format(last_job_position))

        job_position = param_utils.get_value('job_position')
        if job_position is not None:
            query = query & Q("wildcard", latest_job="*{}*".format(job_position))

        expected_salary = param_utils.get_range('expected_salary')
        if expected_salary is not None:
            try:
                gte = expected_salary[0]
                lte = expected_salary[1]
                if lte:
                    query = query & Q("range", salary_max={"lte": int(lte)})
                if gte:
                    query = query & Q("range", salary_min={"gte": int(gte)})
                query = query & Q("range", salary_max={"gt": 0}) & Q("range", salary_min={"gt": 0})
            except:
                # 转换错误直接不查询
                pass

        keyword = param_utils.get_value('keyword')
        if keyword is not None:
            query = query & (
                    Q("wildcard", name="*{}*".format(keyword)) | Q(
                "wildcard", mobile="*{}*".format(keyword)) | Q(
                "wildcard", email="*{}*".format(keyword))
            )

        name = param_utils.get_value('name')
        if name is not None:
            query = query & Q("wildcard", name="*{}*".format(name))

        mobile = param_utils.get_value('mobile')
        if mobile is not None:
            query = query & Q("wildcard", mobile="*{}*".format(mobile))

        email = param_utils.get_value('email')
        if email is not None:
            query = query & Q("wildcard", email="*{}*".format(email))

        residential_address = param_utils.get_value('residential_address')
        if residential_address is not None:
            query = query & Q("wildcard", residential_address="*{}*".format(residential_address))

        form_status = param_utils.get_array('form_status')
        if form_status is not None:
            query = query & Q("terms", form_status=form_status)

        offer_add_dt = param_utils.get_range_date_query('offer_add_dt')
        if offer_add_dt is not None:
            query = query & Q("range", offer_add_dt=offer_add_dt)
            query = query & Q("terms", offer_status=[
                OfferStatus.draft, OfferStatus.accept, OfferStatus.expire, OfferStatus.refuse
            ])

        offer_status = param_utils.get_array('offer_status')
        if offer_status is not None:
            query = query & Q("terms", offer_status=offer_status)

        offer_hire_dt = param_utils.get_range_date_query('offer_hire_dt')
        if offer_hire_dt is not None:
            query = query & Q("range", offer_hire_dt=offer_hire_dt)

        eliminated_reason_ids = param_utils.get_array('eliminated_reason_ids', is_format_uuid=True)
        if eliminated_reason_ids is not None:
            query = query & Q("terms", eliminated_reason_id=eliminated_reason_ids)

        eliminated_dt = param_utils.get_range_date_query('eliminated_dt')
        if eliminated_dt is not None:
            query = query & Q("range", eliminated_dt=eliminated_dt)

        recruitment_channel_ids = param_utils.get_array('recruitment_channel_ids', is_format_uuid=True)
        if recruitment_channel_ids is not None:
            query = query & Q("terms", recruitment_channel_id=recruitment_channel_ids)

        add_by_ids = param_utils.get_array('add_by_ids', is_format_uuid=True)
        if add_by_ids is not None:
            query = query & Q("terms", add_by_id=add_by_ids)

        add_dt = param_utils.get_range_date_query('add_dt')
        if add_dt is not None:
            query = query & Q("range", add_dt=add_dt)

        recruitment_page_ids = param_utils.get_array('recruitment_page_ids', is_format_uuid=True)
        if recruitment_page_ids is not None:
            query = query & Q("terms", recruitment_page_id=recruitment_page_ids)

        tag_ids = param_utils.get_array('tag_ids', is_format_uuid=True)
        if tag_ids is not None:
            query = query & Q("terms", tag_list=tag_ids)

        interview_count = param_utils.get_array('interview_count')
        if interview_count is not None:
            if '0' in interview_count:
                query = query & Q("range", interview_count={'gt': 0})
            else:
                query = query & Q("terms", interview_count=interview_count)

        search = search.query(query)

        p = param_utils.get_int('p')
        if p:
            limit = param_utils.get_int('limit', 10)
            offset = (p - 1) * limit
            search = search[offset: offset + limit]

        order_by = param_utils.get_value("order_by", '2')
        if order_by == '1':
            search = search.sort('-update_dt')
        elif order_by == '2':
            search = search.sort('-add_dt')

        return search

    @classmethod
    async def get_status_total(cls,
                               company_id: str,
                               search_params: dict) -> dict:
        """
        获取应聘记录统计数据 - 状态维度
        @param company_id: 企业id
        @param search_params: 筛选条件数据
        @return: {"状态1": 总数, "状态2": 总数}
        """
        search = cls.basic_search(
            company_id=company_id,
            search_params=search_params
        )
        search.aggs.bucket("status", "terms", field="status", order=[{"_term": "asc"}])
        client = await es.default_es
        result = await client.search(search.to_dict(), index=cls.INDEX, size=0,
                                     filter_path='aggregations.status.buckets', track_total_hits=True)
        total = {}
        for item in result.get('aggregations', {}).get('status', {}).get('buckets', []):
            total[item.get('key')] = item.get('doc_count')

        return total

    @classmethod
    async def get_count(cls,
                        company_id: str,
                        search_params: dict) -> int:
        """
        获取应聘记录总数
        @param company_id: 企业id
        @param search_params: 筛选条件数据
        @return: 总数
        """
        search = cls.basic_search(
            company_id=company_id,
            search_params=search_params
        )
        client = await es.default_es
        result = await client.search(search.to_dict(), index=cls.INDEX, size=0,
                                     filter_path='hits.total', track_total_hits=True)

        return result.get('hits', {}).get('total', {}).get('value', 0)

    @classmethod
    async def get_list(cls,
                       company_id: str,
                       search_params: dict) -> (int, list):
        """
        获取应聘记录列表
        @param company_id: 企业id
        @param search_params: 筛选条件数据
        @return: 总数
        """
        search = cls.basic_search(
            company_id=company_id,
            search_params=search_params
        )
        client = await es.default_es
        result = await client.search(search.to_dict(), index=cls.INDEX, filter_path='hits', track_total_hits=True)

        count = result.get('hits', {}).get('total', {}).get('value', 0)
        list = [row.get('_source', {}) for row in result.get('hits', {}).get('hits', [])]

        return count, list

    @classmethod
    async def save_candidate_record(cls, instance):
        client = await es.default_es
        instance = ToModel(instance)
        params = {
            "routing": uuid2str(instance.company_id),
            "refresh": 'true'
        }

        action = {
            "id": uuid2str(instance.id),
            'company_id': uuid2str(instance.company_id),
            'add_by_id': uuid2str(instance.add_by_id),
            'add_dt': esutils.format_datetime(instance.add_dt),
            'update_dt': esutils.format_datetime(instance.update_dt),
            'is_delete': bool(instance.is_delete),
            'candidate_id': uuid2str(instance.candidate_id),

            'job_position_id': uuid2str(instance.job_position_id),
            'status': instance.status,
            'form_status': instance.form_status,
            'eliminated_reason_id': uuid2str(instance.eliminated_reason_id),
            'eliminated_dt': esutils.format_datetime(instance.eliminated_dt),
            'recruitment_channel_id': uuid2str(instance.recruitment_channel_id),
            'interview_count': instance.interview_count,
            'referee_name': instance.referee_name,
            'referee_mobile': instance.referee_mobile,
            'entry_sign_id': instance.entry_sign_id,
            'intention_emp_id': instance.intention_emp_id,
            'candidate_form_id': instance.candidate_form_id,
            'employee_id': instance.employee_id
        }
        try:
            await client.update(
                index=cls.INDEX,
                body={'doc': action, 'doc_as_upsert': True},
                params=params, id=uuid2str(instance.id),
                retry_on_conflict=5
            )
        except:
            exc = traceback.format_exc()
            exc = '{}[{}]ORM信号同步Es任务执行出错!!!\n {}'.format(
                config.PROJECT_NAME, config.APP_ENV, exc
            )
            if config.APP_ENV != 'local':
                logging.error(exc)
                # TODO 发给SENTRY
                try:
                    Notifier.exception(exc)
                except Exception:
                    pass
