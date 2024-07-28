import pytest

from framework_engine import create_app
from services.s_dbs.s_offer_record import OfferSubmitRecord


app = create_app()


class TestOfferSubmitRecord:
    @pytest.mark.asyncio
    async def test_get_offer_submit_by_candidate_record_ids(self):
        company_id = 'ab164df86d10491f90ccbece63cc865e'
        candidate_record_ids = [
            '090acf286d3c4536802f7fd6d6d1ff61',
            '531eb89be5444d349ca899826da92ed3',
            '79638978847846d18d3d508751d98e0e'
        ]

        results = await OfferSubmitRecord.get_offer_submit_by_candidate_record_ids(
            company_id,
            candidate_record_ids
        )

        assert True
