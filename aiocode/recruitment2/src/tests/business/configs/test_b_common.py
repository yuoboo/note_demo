import pytest

from business.configs.b_common import CommonBusiness


class TestCommonBusiness(object):
    @pytest.mark.asyncio
    async def test_has_hr(self):
        datas = [
            {
                'company_id': 'ab164df86d10491f90ccbece63cc865e',
                'emp_id': 'd36af3408fc14ff78d066481add8be90',
                'want': True
            },
            {
                'company_id': 'ab164df86d10491f90ccbece63cc865e',
                'emp_id': 'd36af3408fc14ff78d066481add8be91',
                'want': False
            }
        ]
        for data in datas:
            got = await CommonBusiness.has_hr(data.get('company_id'), data.get('emp_id'))
            assert got == data.get('want')
