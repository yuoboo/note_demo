import time

import pytest

from services import PortalPageService
from services.s_https.s_employee import EmployeeService, DepartmentService


@pytest.mark.asyncio
async def test_check_employee():
    company_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    emp_name = "喻岩"
    mobile = "13830720000"
    status, emp_id = await EmployeeService.check_employee(
        company_id=company_id, emp_name=emp_name, emp_mobile=mobile
    )
    print(f"this is check_employee:{status}, {emp_id}")
    # 在职
    assert status == 1
    assert emp_id

    emp_name = "卡萨丁"
    mobile = "13011112222"
    status, emp_id = await EmployeeService.check_employee(
        company_id, emp_name, mobile
    )
    print(f"this is check_employee:{status}, {emp_id}")
    # 待入职
    assert status == 2
    assert emp_id

    emp_name = "不存在"
    mobile = "150111111111"
    status, emp_id = await EmployeeService.check_employee(
        company_id, emp_name, mobile
    )
    print(f"this is check_employee:{status}, {emp_id}")
    # 不存在的员工
    assert status == 0
    assert emp_id is None


@pytest.mark.asyncio
async def test_check_blacklist():
    company_id = "f79b05ee3cc94514a2f62f5cd6aa8b6e"
    emp_list = [
        {"id": "", "id_no": "", "name": "通芳", "mobile": "15507780000"},
        {"id": "", "id_no": "", "name": "公文", "mobile": "13698310000"},
    ]
    res = await EmployeeService.check_blacklist(company_id, emp_list)
    print(res)
    assert 1


class TestDepartmentService:
    def setup(self):
        self.company_id = "87809583568d407ca0597039d81fac5a"

    @pytest.mark.asyncio
    async def test_get_children_ids(self):
        dep_ids = ["589d553a-90e7-43da-8de8-0835f20a8268", "931795cd-0fbe-4f3b-8bf6-1d9697a703aa"]
        t1 = time.perf_counter()
        res = await DepartmentService.get_children_ids(self.company_id, dep_ids)
        print(111, time.perf_counter() - t1, res)
        assert res

