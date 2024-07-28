import pytest

from framework_engine import create_app
from services.s_https.s_person_ucenter import PersonUCenterService

app = create_app()


class TestPersonUCenterService:
    def setup(self):
        self.app_id = 2010
        self.company_id = '14074096fd4d4bb782b829dea931f8df'
        self.user_ids = ["zyp", "ZhengZe"]
        self.employee_ids = [
            '0311f4e329064f5bb59d592443ec36aa',
            '6383d26e4d564f4e8a45b0278881b6cd'
        ]

    @pytest.mark.asyncio
    async def test_wework_get_corp_accesstoken(self):
        company_token = await PersonUCenterService.wework_get_corp_accesstoken(
            app_id=self.app_id,
            company_id=self.company_id
        )
        assert company_token

    @pytest.mark.asyncio
    async def test_wework_get_corp_users(self):
        corp_users = await PersonUCenterService.wework_get_corp_users(
            app_id=self.app_id,
            user_ids=self.user_ids
        )

        company_users = await PersonUCenterService.wework_get_corp_users(
            app_id=self.app_id,
            company_id=self.company_id,
            user_ids=self.user_ids
        )

        corp_employees = await PersonUCenterService.wework_get_corp_users(
            app_id=self.app_id,
            employee_ids=self.employee_ids
        )

        company_employees = await PersonUCenterService.wework_get_corp_users(
            app_id=self.app_id,
            company_id=self.company_id,
            employee_ids=self.employee_ids
        )

        assert len(corp_users) > 0 and len(company_users) > 0
        assert len(corp_employees) > 0 and len(company_employees) == 0

    @pytest.mark.asyncio
    async def test_wework_get_corp_accesstoken(self):
        company = await PersonUCenterService.wework_get_suite_corp(
            app_id=self.app_id,
            company_id=self.company_id
        )
        assert company

    @pytest.mark.asyncio
    async def test_wework_get_core_suite_info(self):
        info = await PersonUCenterService.wework_get_core_suite_info(
            suite_id='ww2c442e3cb6461e47',
            corp_id='ww9a48c0f1585ead25'
        )
        assert info
