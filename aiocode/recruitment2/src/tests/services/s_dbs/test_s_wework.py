import pytest
from services.s_dbs.s_wework import WeWorkService


@pytest.mark.asyncio
async def test_create_or_update_external_contact_data():

    _types = await WeWorkService.create_or_update_external_contact_data(
        company_id="ab164df86d10491f90ccbece63cc865e",
        wework_external_contact_id="460960c0769248fa80d6f38707ff06b1",
        follow_user=[{"employee_id": "cb2e1668e5924b8cbf812dab614b57ae", "user_id": "joe"}]
    )
    assert True
