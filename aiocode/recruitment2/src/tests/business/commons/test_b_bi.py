import pytest
from business.commons.b_bi import bi_biz


@pytest.mark.asyncio
async def test_send_position_to_bi():
    company_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    job_position_ids = ["0733de96e9e94b1e8bdde0029a1a3637"]
    await bi_biz.send_job_position_to_bi(company_id, job_position_ids)


@pytest.mark.asyncio
async def test_send_candidate_record_to_bi():
    company_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    candidate_record_ids = ["ffa900dc67ee4d66b14c4fffebc9debf", "d501de87815242388669850e00688e8d"]
    await bi_biz.send_candidate_record_to_bi(company_id, candidate_record_ids)
