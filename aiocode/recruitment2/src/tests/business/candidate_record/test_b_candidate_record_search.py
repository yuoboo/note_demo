import pytest

from business.candidate_record.b_candidate_record_search import CandidateRecordSearchBusiness


class TestCandidateRecordSearchBusiness(object):
    @pytest.mark.asyncio
    async def test_search(self):
        params = {'p': '1', 'order_by': '1', 'limit': '20', 'display': 2, 'scene_type': '34'}
        company_id = 'ab164df86d10491f90ccbece63cc865e'
        user_id = '5dfc3e1b81644eb5a7ce4a34005c7026'
        user_type = 1
        for i in range(100):
            await CandidateRecordSearchBusiness.search(company_id, user_id, params, user_type)
