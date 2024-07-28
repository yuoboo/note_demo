import pytest

from business.b_wework import WeWorkBusiness


class TestWeWorkBusiness(object):
    @pytest.mark.asyncio
    async def test_get_by_external_id_first(self):
        datas = [
            {
                'company_id': 'ab164df86d10491f90ccbece63cc865e',
                'external_id': 'wmEKyIDQAAnuhO2rppkTsfnEbmBEw-QQ',
                'want': 'e86ff1c59d064587be9aa75be810c213'
            }
        ]
        for data in datas:
            got = await WeWorkBusiness.get_by_external_id_first(data.get('company_id'), data.get('external_id'))
            assert got.get('candidate_id') == data.get('want')

    @pytest.mark.asyncio
    async def test_add_external_contact(self):
        external_user_id = 'wmEKyIDQAAnuhO2rppkTsfnEbmBEw-QQ'
        corp_id = 'ww9ee984b6fe86bf1a'
