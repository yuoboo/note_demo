import pytest

from framework_engine import create_app
from services.s_https.s_ucenter import get_users


app = create_app()


@pytest.mark.asyncio
async def test_get_users():
    results = await get_users(['362f7de6128e460589ef729e7cdda774', '212ec42eccbe4132b9994528b31820fb'])
    assert results
