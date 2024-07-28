import pytest

from services.s_https.s_candidate import CandidateService


@pytest.mark.asyncio
async def test_candidate_search():
    company_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    keyword = "ex"
    res = await CandidateService.search_candidate(
        company_id=company_id, keyword=keyword
    )
    print(111, res)
    assert res

@pytest.mark.asyncio
async def test_candidate_create():
    company_id = ""
    candidate_name = ""
    candidate_mobile = ""
    attachments = []
    resume_key = ""
    candidate_id = ""
    candidate_result = await CandidateService.create_candidate_by_form_data_and_attach(
        company_id=company_id,
        candidate_data={"candidate_name": candidate_name, "mobile": candidate_mobile},
        candidate_attachments=attachments, file_key=resume_key, candidate_id=candidate_id
    )
    assert candidate_result
