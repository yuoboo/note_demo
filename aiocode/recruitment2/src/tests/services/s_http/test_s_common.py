import pytest

from framework_engine import create_app
from services.s_https.s_common import get_bg_check_status


app = create_app()


@pytest.mark.asyncio
async def test_get_bg_check_status():
    results = await get_bg_check_status('', [])
    assert results
