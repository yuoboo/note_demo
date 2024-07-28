import pytest
import datetime
from services.s_es.s_interview_es import OldInterviewESService


@pytest.mark.asyncio
async def test_get_count():
    company_id = 'ab164df86d10491f90ccbece63cc865e'
    permission_job_position_ids = []
    permission_candidate_record_ids = []
    result = await OldInterviewESService.get_count(
        company_id=company_id,
        permission_job_position_ids=permission_job_position_ids,
        permission_candidate_record_ids=permission_candidate_record_ids,
        interview_dt=['2020-11-26 15:01:00', None]
    )
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_get_job_position_total():
    company_id = 'ab164df86d10491f90ccbece63cc865e'
    permission_job_position_ids = []
    permission_candidate_record_ids = []
    job_position_ids = ['90277287721c4775b011636959520d79', '9dc8cfbb308b44ecaadc139084eb9072']
    result = await OldInterviewESService.get_job_position_total(
        company_id=company_id,
        permission_job_position_ids=permission_job_position_ids,
        permission_candidate_record_ids=permission_candidate_record_ids,
        job_position_ids=job_position_ids,
        interview_dt=['2020-11-20 00:00:00', None]
    )
    assert len(result.keys()) >= 0

