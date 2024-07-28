import pytest
import time
from utils.table_util import TableUtil
from models.m_wework import tb_wework_external_contact
from services.s_dbs.s_wework import WeWorkService


@pytest.mark.asyncio
async def test_table_util():
    wework_tbu = TableUtil(tb_wework_external_contact)
    print(wework_tbu.table_defaults())
    print(wework_tbu.get_default("add_dt"))
    time.sleep(2)
    print(wework_tbu.get_default("add_dt"))
    assert not wework_tbu.get_default("is_delete")


@pytest.mark.asyncio
async def test_json():
    company_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    unionid = "oJ3FUt_WNhjuLlQ5aFxo_eaSeTpc"
    res = await WeWorkService.get_external_by_unionid(company_id, unionid)
    print('\n', res)
    follow_user = res.get("follow_user")
    print(type(follow_user), follow_user)
    assert 1


@pytest.mark.asyncio
async def test_get_or_create():
    company_id = 'f79b05ee3cc94514a2f62f5cd6aa8b6e'
    unionid = "1223333221"
    is_created, res = await WeWorkService.get_or_create(company_id, unionid, name="测试122")
    print('\n', res)
    follow_user = res.get("follow_user")
    print(type(follow_user), follow_user)
    assert 2
