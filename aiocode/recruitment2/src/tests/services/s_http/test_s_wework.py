import pytest
from configs import config

from framework_engine import create_app
from services.s_https.s_wework import WeWorkService, WeWorkExternalContactService

app = create_app()


class TestWeWorkService:
    def setup(self):
        self.app_id = 2010
        self.company_id = '87809583568d407ca0597039d81fac5a'
        self.user_ids = ["zyp", "ZhengZe"]

    @pytest.mark.asyncio
    async def test_get_token(self):
        company_service = WeWorkService(
            app_id=2010,
            company_id=self.company_id
        )

        company_token = await company_service.get_token()
        assert company_token

    @pytest.mark.asyncio
    async def test_is_app(self):
        service = WeWorkService(
            app_id=2010,
            company_id='test_company'
        )
        is_app = await service.is_app()
        assert is_app is False


class TestWeWorkExternalContactService:
    def setup(self):
        self.app_id = 2010
        self.company_id = '87809583568d407ca0597039d81fac5a'
        self.user_ids = ["chenyuan"]

    @pytest.mark.asyncio
    async def test_get_follow_user_list(self):
        service = WeWorkExternalContactService(
            app_id=2010,
            company_id=self.company_id
        )

        results = await service.get_follow_user_list()
        assert len(results) > 0
