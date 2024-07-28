import datetime

from drivers.es import es
from elasticsearch_dsl import Search, Q, A

from services.s_es.s_candidate_record_es import OldCandidateRecordESService


class OldInterviewESService:
    INDEX = 'recruitment_search'

    @classmethod
    def basic_search(cls,
                     company_id: str,
                     permission_job_position_ids: list,
                     permission_candidate_record_ids: list,
                     status: list = None,
                     job_position_ids: list = None,
                     interview_dt: list = None):
        """
        基础搜索
        @param company_id: 企业id
        @param permission_job_position_ids: 用户权限/招聘职位ids
        @param permission_candidate_record_ids: 用户权限/应聘记录ids
        @param status: 筛选条件/状态列表[状态1, 状态2]， 为空则不筛选
        @param job_position_ids: 筛选条件/职位ids[职位1, 职位2]， 为空则不筛选
        @param interview_dt: 筛选条件/面试时间[开始时间, 结束时间]， 为空则不筛选
        @return:
        """
        search = Search()

        query = Q(
            "term", candidate_parent="interview") & Q(
            "term", c_company_id=company_id) & Q(
            "term", c_is_delete=False)

        candidate_record_query = Q("term", c_is_delete=False)
        if permission_job_position_ids or permission_candidate_record_ids:
            candidate_record_query = candidate_record_query & (
                    Q("terms", c_job_position_id=permission_job_position_ids) |
                    Q("terms", c_id=permission_candidate_record_ids)
            )

        if job_position_ids:
            candidate_record_query = candidate_record_query & Q("terms", c_job_position_id=job_position_ids)

        if status:
            candidate_record_query = candidate_record_query & Q("terms", c_status=status)

        if interview_dt and len(interview_dt) == 2:
            query = query & Q("range", c_interview_dt=cls.format_datetime_range(interview_dt))

        query = query & Q("has_parent", parent_type="candidate_record", inner_hits={}, query=candidate_record_query)
        search = search.query(query)

        return search

    @classmethod
    def format_date_range(cls, date):
        start_date = date[0]
        end_date = date[1]
        result = {}
        if start_date:
            result['gte'] = start_date
        if end_date:
            result['lte'] = end_date

        result['format'] = "yyyy-MM-dd"
        result['time_zone'] = "+08:00"
        return result

    @classmethod
    def format_datetime_range(cls, dt):
        start_date = dt[0]
        end_date = dt[1]
        result = {}
        if start_date:
            result['gte'] = start_date
        if end_date:
            result['lte'] = end_date

        result['format'] = "yyyy-MM-dd HH:mm:ss"
        result['time_zone'] = "+08:00"
        return result

    @classmethod
    async def get_job_position_total(cls,
                                     company_id: str,
                                     permission_job_position_ids: list,
                                     permission_candidate_record_ids: list,
                                     job_position_ids: list = [],
                                     status: list = [],
                                     interview_dt: list = []) -> dict:
        """
        获取面试日程统计数据 - 职位纬度
        @param company_id: 企业id
        @param permission_job_position_ids: 用户权限/招聘职位ids
        @param permission_candidate_record_ids: 用户权限/应聘记录ids
        @param job_position_ids: 筛选条件/职位ids[职位1, 职位2]， 为空则不筛选
        @param status: 筛选条件/状态列表[状态1, 状态2]， 为空则不筛选
        @param interview_dt: 筛选条件/面试时间[开始时间, 结束时间]， 为空则不筛选
        @return: {"状态1": 总数, "状态2": 总数}
        """
        search = OldCandidateRecordESService.basic_search(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            job_position_ids=job_position_ids,
            status=status
        )
        aggs = A("terms", field="c_job_position_id")
        aggs_query = Q(
            "range", c_interview_dt=cls.format_datetime_range(interview_dt)) & Q(
            "term", c_is_delete=False
        )
        aggs2 = A("children", type="interview")
        aggs2.bucket("count", 'filter', filter=aggs_query)
        aggs.bucket("parent", aggs2)
        search.aggs.bucket("job_position", aggs)
        client = await es.default_es
        result = await client.search(search.to_dict(), index=cls.INDEX, size=0,
                                     filter_path='aggregations.job_position.buckets', track_total_hits=True)
        total = {}
        for item in result.get('aggregations', {}).get('job_position', {}).get('buckets', []):
            total[item.get('key')] = item.get('parent', {}).get('count', {}).get('doc_count')

        return total

    @classmethod
    async def get_count(cls,
                        company_id: str,
                        permission_job_position_ids: list,
                        permission_candidate_record_ids: list,
                        interview_dt: list = []) -> int:
        """
        面试日程数量统计
        @param company_id:
        @param permission_job_position_ids:
        @param permission_candidate_record_ids:
        @param interview_dt: 筛选条件/面试时间[开始时间, 结束时间]， 为空则不筛选
        @return: 总数
        """
        search = cls.basic_search(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            interview_dt=interview_dt
        )

        client = await es.default_es
        result = await client.count(search.to_dict(), index=cls.INDEX, filter_path='count')

        return result.get('count', 0)
