import pytest

from business.portals.b_portal_wework import PortalWeWorkBusiness
from configs import config


class TestPortalWeWorkBusiness(object):
    @pytest.mark.asyncio
    async def test_get_hr_list(self):
        company_id = '87809583568d407ca0597039d81fac5a'
        hr_list = await PortalWeWorkBusiness.get_hr_list(company_id)
        assert hr_list

    @pytest.mark.asyncio
    async def test_get_external_contact_qr_code(self):
        company_id = '87809583568d407ca0597039d81fac5a'
        employee_id = 'e0f16445662543529e0de032f1c69e23'
        app_id = config.WEWORK_2HAOHR_APPID
        qr_code = await PortalWeWorkBusiness.get_external_contact_qr_code(
            app_id, company_id, employee_id)
        assert qr_code
