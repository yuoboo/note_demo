import pytest

from framework_engine import create_app
from services import ManageScopeService


app = create_app()


class TestRecruitmentTeamService:
    @pytest.mark.asyncio
    async def test_get_offer_submit_by_candidate_record_ids(self):
        company_id = '13b6bb3c18d94953941d9af21636b072'
        emp_id = '5455581ad7ed49f7bc3ce55ad3c8404d'

        results = await ManageScopeService._get_user_id_by_emp_id(
            company_id, emp_id
        )

        assert results
