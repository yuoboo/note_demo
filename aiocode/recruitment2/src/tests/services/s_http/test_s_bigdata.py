import pytest

from framework_engine import create_app
from services.s_https.s_bigdata import BigDataService, BigDataDateFormat

app = create_app()


class TestBigDataService:
    @pytest.mark.asyncio
    async def test_portals_pv_current_month(self):
        company_share_id = 'bda13867c7ee46ff8e5b6027252c3a8a'
        count = await BigDataService.get_portals_pv_current_month(company_share_id)

        assert count >= 0

    @pytest.mark.asyncio
    async def test_get_portals_employee(self):
        company_share_id = 'bf38e69fad3a45719e34774d61ce5c60'
        employee_id = '9dc962a7a14f4027adc3d79f74ddeab7'
        count = await BigDataService.get_portals_employee_pv_current_month(
            company_share_id=company_share_id,
            employee_id=employee_id
        )

        assert count >= 0

        count = await BigDataService.get_portals_employee_pv_yesterday(
            company_share_id=company_share_id,
            employee_id=employee_id
        )

        assert count >= 0

    @pytest.mark.asyncio
    async def test_get_portals_page_pv(self):
        company_share_id = '31fc75b000a64e07b6943e4146b2c258'
        count = await BigDataService.get_portals_page_pv_current_month(
            company_share_id=company_share_id
        )

        assert len(count) >= 0
