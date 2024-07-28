import pytest
from services.s_dbs.s_job_position import JobPositionTypeService


@pytest.mark.asyncio
async def test_position_types():
    _types = await JobPositionTypeService.get_position_type_tree()
    print(_types)
    assert _types

