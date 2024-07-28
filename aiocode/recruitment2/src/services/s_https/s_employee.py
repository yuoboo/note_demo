# coding: utf-8
import asyncio
import copy

import typing
from functools import reduce

import ujson

from constants.redis_keys import COMPANY_DEPT_LIST_KEY, COMPANY_DEPT_TREE_KEY
from drivers.redis import redis_db
from kits.exception import ServiceError
from utils.ehr_request import EhrRequest
from utils.strutils import uuid2str
from utils.logger import http_logger


class EmployeeService(object):

    @classmethod
    async def get_employee_info_by_ids(
            cls, company_id: str, emp_ids: list, head_fields: list, auto_raise=True
    ) -> list:
        params_data = {
            "company_id": uuid2str(company_id),
            "cond": {"id__in": [uuid2str(emp_id) for emp_id in emp_ids]},
            "head_fields": head_fields,
        }
        res = await EhrRequest("employee").intranet("intranet_employee_search/search").post(data=params_data)
        if not res or res["resultcode"] != 200:
            if auto_raise:
                error_msg = "查询员工信息失败" if not res else res["errormsg"]
                raise ServiceError(msg=error_msg)
            return []

        return res["data"]["result"]

    @classmethod
    async def check_employee(cls, company_id: str, emp_name: str, emp_mobile: str) -> (str, str):
        """
        校验员工信息
        :param company_id:
        :param emp_name: 员工姓名
        :param emp_mobile: 员工手机号
        :return: emp_status 1. 在职， 2.待入职
        """
        data = {
            "company_id": company_id,
            "emp_name": emp_name,
            "mobile": emp_mobile
        }
        res = await EhrRequest("v1").intranet("employee/private/check_emp").post(data=data)
        if res and res["resultcode"] == 200:
            if res["data"]:
                emp_status = res["data"].get("emp_status")
                emp_id = res["data"].get("emp_id")
                return emp_status, uuid2str(emp_id)
        return None, None

    @classmethod
    async def check_blacklist(cls, company_id: str, emp_list: list) -> list:
        """
        校验黑名单
        :param company_id:
        :param emp_list: [{"id": "", "id_no": "", "mobile": "", "name": ""}]
        :return:{'add_reason': '这是个人才', 'name': '通芳', 'mobile': '15507780000',
                'flag': 1, 'add_by': '喻冰', 'id_no': '', 'add_dt': '2021-01-28', 'id': ''}
        """
        params = {
            "company_id": company_id,
            "objs": emp_list
        }
        res = await EhrRequest("employee").intranet("black/confirm").post(data=params)
        if res and res["resultcode"] != 200:
            http_logger.error(f"校验黑名单失败, 返回结果: {res}")
            return []

        return res["data"]

    @classmethod
    async def verify_employee_by_mobiles(cls, company_id: str, mobiles: list):
        """
        根据手机号查询存在员工和待入职
        @param company_id:
        @param mobiles:
        @return:
        """
        data = {
            "company_id": uuid2str(company_id),
            "mobile_list": mobiles
        }
        res = await EhrRequest("employee").intranet("emp_relation/bulk_verify_mobile").post(data=data)
        if res and res["resultcode"] == 200:
            return res.get("data") or {}

        return {}


class DepartmentService(object):

    @classmethod
    async def get_com_tree(cls, company_id: str) -> list:
        """
        获取公司组织信息(树形)
        """
        redis_cli = await redis_db.default_redis
        redis_key = COMPANY_DEPT_TREE_KEY.format(company_id=uuid2str(company_id))
        data = await redis_cli.get(redis_key)
        if data:
            return ujson.loads(data)
        result = await EhrRequest("orgs").intranet("department/tree").get(
            data={"company_id": company_id}
        )
        data = result.get("data") or [] if result else []
        await redis_cli.set(redis_key, ujson.dumps(data))
        return data

    @classmethod
    async def get_com_list(cls, company_id: str):
        """
        获取公司组织列表信息
        :param company_id:
        """
        redis_cli = await redis_db.default_redis
        redis_key = COMPANY_DEPT_LIST_KEY.format(company_id=uuid2str(company_id))
        data = await redis_cli.get(redis_key)
        if data:
            return ujson.loads(data)
        query_data = {"company_id": uuid2str(company_id)}
        result = await EhrRequest("orgs").intranet("department/list").get(
            data=query_data
        )
        # 去除不需要的信息
        data = []
        res = result.get("data") or [] if result else []
        for item in res:
            data.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "sup_department_id": item["sup_department_id"],
                    "level": item["level"]
                }
            )
        await redis_cli.set(redis_key, ujson.dumps(data))
        return data

    @classmethod
    async def get_parent_ids(cls, company_id: str, dep_ids: list) -> dict:
        """
        通过组织id获取所有父级id, 包括自身
        dep_ids: 组织id列表 ---> 返回{"id1": [父级id], "id2": [父级id]}
        """
        if not dep_ids:
            return {}
        dep_ids = list(set([uuid2str(dep_id) for dep_id in dep_ids]))
        dep_list = await cls.get_com_list(company_id)
        if not dep_list:
            return {}
        dep_id2parent_ids = {}
        dep_id2dep = {item["id"]: item for item in dep_list}
        for did in sorted(dep_id2dep, key=lambda x: dep_id2dep[x]["level"]):
            dep = dep_id2dep[did]
            parent = dep_id2dep.get(dep["sup_department_id"], None)
            if parent:
                parent_dep_id_list = parent.get("parent_dep_id_list") or []
                parent_dep_id_list += [uuid2str(parent["id"])]
            else:
                parent_dep_id_list = []
            dep["parent_dep_id_list"] = parent_dep_id_list

            dep_copy = copy.deepcopy(dep)
            parent_ids = dep_copy["parent_dep_id_list"]
            parent_ids.append(did)
            dep_id2parent_ids[did] = parent_ids

        res = {}
        for dep_id in dep_ids:
            res[dep_id] = dep_id2parent_ids.get(dep_id, [])

        return res

    @classmethod
    async def get_parent_map_by_ids(cls, company_id: str, dep_ids: list):
        if not dep_ids:
            return {}

        dep_ids = [uuid2str(_id) for _id in dep_ids if _id]
        com_deps = await cls.get_com_list(company_id)
        tmp_dict = dict(zip([uuid2str(c["id"]) for c in com_deps], com_deps))
        res = dict()
        for _dep in sorted(com_deps, key=lambda x: x["level"], reverse=False):
            _id = uuid2str(_dep["id"])
            obj = tmp_dict.get(_id)
            parent_id = obj.get("sup_department_id")
            if parent_id:
                parent = tmp_dict.get(uuid2str(parent_id))
                obj["parent_ids"] = parent.get("parent_ids", []) + [_id]
            else:
                obj["parent_ids"] = [_id]

            if _id in dep_ids:
                res[_id] = obj["parent_ids"]
        return res

    @classmethod
    async def get_fullname_map(cls, company_id: str):
        com_deps = await cls.get_com_list(company_id)
        res = dict()
        tmp_dict = dict(zip([uuid2str(c["id"]) for c in com_deps], com_deps))
        for _dep in sorted(com_deps, key=lambda x: x["level"], reverse=False):
            _id = uuid2str(_dep["id"])
            obj = tmp_dict.get(_id)
            parent_id = obj.get("sup_department_id")
            if parent_id:
                parent = tmp_dict.get(uuid2str(parent_id))
                obj["fullname"] = f'{parent["fullname"]}/{obj["name"]}'
            else:
                obj["fullname"] = obj["name"]

            res[_id] = obj["fullname"]
        return res

    @classmethod
    async def get_dep_parent_tree(cls, company_id: str, dep_ids: list) -> list:
        """返回部门父级树"""
        _parent_map = await cls.get_parent_map_by_ids(company_id, dep_ids)
        all_dep_ids = reduce(lambda x, y: x+y, _parent_map.values())
        deps = await cls.get_com_list(company_id)
        return cls.create_dep_tree(list(filter(lambda x: uuid2str(x["id"]) in all_dep_ids, deps)))

    @classmethod
    def create_dep_tree(cls, data: list) -> list:
        """
        组装部门数
        数据中需要包含如下字段
        部门id -> id
        部门name -> name
        部门level -> level
        父级部门id -> sup_department_id
        """
        if not data:
            return []

        _dict = {uuid2str(d['id']): d for d in data}
        res = []
        for i in sorted(data, key=lambda x: x["level"], reverse=False):
            obj = _dict.get(i["id"])
            # 前端组件需要根据 is_permission 来判断显示, 这里统一加上
            obj["is_permission"] = True
            # 加入下级key
            obj.setdefault("list", [])
            # 加入上级
            parent_pk = obj.get("sup_department_id")
            parent = _dict.get(uuid2str(parent_pk))
            if not parent:
                obj["fullname"] = obj["name"]
                res.append(obj)
            else:
                obj["fullname"] = f'{parent["fullname"]}/{obj["name"]}'
                parent.setdefault("list", []).append(obj)

        return res

    @classmethod
    async def get_children_ids(cls, company_id: str, dep_ids: typing.List[str]) -> dict:
        """
        通过id获取所有子类id, 返回数据中包含父类本身
        :return: {"父类id": []}
        """
        if not dep_ids:
            return {}
        dep_ids = list(set([uuid2str(dep_id) for dep_id in dep_ids]))
        dep_list = await cls.get_com_list(company_id)
        if not dep_list:
            return {}
        dep_id2dep = {item["id"]: item for item in dep_list}

        for did in sorted(dep_id2dep, key=lambda x: dep_id2dep[x]["level"], reverse=True):
            dep = dep_id2dep[did]
            # 子部门id
            all_children_ids = dep.get("children_dep_id_list", [])
            dep["children_dep_id_list"] = all_children_ids
            parent = dep_id2dep.get(dep["sup_department_id"], None)
            if parent:
                parent["children_dep_id_list"] = parent.get("children_dep_id_list", []) + [uuid2str(did)]
                if all_children_ids:
                    parent["children_dep_id_list"] = parent.get("children_dep_id_list", []) + all_children_ids

        res = {}
        for dep_id in dep_ids:
            children_ids = dep_id2dep.get(dep_id, {}).get("children_dep_id_list", [])
            children_ids.append(dep_id)
            res[dep_id] = children_ids

        return res

    @classmethod
    async def get_all_dep_ids(cls, company_id: str, dep_ids: list) -> list:
        """
        获取部门列表的所有子部门集合（包括自身）
        """
        ret = []
        if dep_ids:
            dep_ids = [uuid2str(dep_id) for dep_id in dep_ids]
            res = await cls.get_children_ids(company_id, dep_ids)
            for item in res.values():
                ret.extend(item)
        ret = [uuid2str(item) for item in ret]
        return ret

    @classmethod
    async def get_parent_tree(cls, company_id: str, dep_ids: list) -> list:

        parent_dep_data = await cls.get_parent_ids(company_id, dep_ids) or {}
        permission_dep_ids = []
        for _, value_list in parent_dep_data.items():
            permission_dep_ids.extend(value_list)
        permission_dep_ids = list(set([uuid2str(dep_id) for dep_id in permission_dep_ids if dep_id]))
        # 获取当前企业组织部门信息
        all_dep_data = await cls.get_com_tree(company_id)

        # 过滤当前企业组织部门信息
        def check_permission(data_list, parent_name=''):
            for item in data_list:
                department_id = uuid2str(item.get("id"))
                fullname = "{}/{}".format(parent_name, item.get("name")) if parent_name else item.get("name")
                item["is_permission"] = True if department_id in permission_dep_ids else False
                item["fullname"] = fullname
                if item.get("list"):
                    check_permission(item.get("list"), fullname)
                else:
                    continue

        check_permission(all_dep_data)

        def clean_dep_data(data2_list):
            for item2 in data2_list:
                if not item2["is_permission"]:
                    data2_list.remove(item2)
                    continue
                if item2.get("list"):
                    clean_dep_data(item2.get("list"))

        clean_dep_data(all_dep_data)

        return all_dep_data

    @classmethod
    async def get_all_dep_ids(cls, company_id: str, dep_ids: list) -> list:
        """
        获取部门列表的所有子部门集合（包括自身）
        """
        ret = []
        if dep_ids:
            dep_ids = [uuid2str(dep_id) for dep_id in dep_ids]
            res = await cls.get_children_ids(company_id, dep_ids)
            for item in res.values():
                ret.extend(item)
        ret = [uuid2str(item) for item in ret]
        return ret


class JobGroupService(object):

    @classmethod
    async def get_job_group_by_job_title(cls, company_id: str, job_title_ids: list):
        result = await EhrRequest("employee").intranet("org/get_job_group").post(
            data={"company_id": company_id, "job_title_ids": job_title_ids}
        )
        return result["data"] if result else {}


if __name__ == "__main__":
    async def helper():
        res = await JobGroupService.get_job_group_by_job_title("55842dd7d2f74f63bc1829d1a5bd5193", ["55842dd7d2f74f63bc1829d1a5bd5193"])
        print(res)
        # res = await EmployeeService.get_employee_info_by_ids(
        #     "55842dd7d2f74f63bc1829d1a5bd5193", ["000013ba3bb5415289fe9fcb603a2d3d"], ["emp_name", "mobile"]
        # )
        # res = await DepartmentService.get_children_ids(
        #     'ec9ab455f91c46c9abaf47d508182972', ['82be8463-93fc-4f55-9232-96beb8233022']
        # )
        # print(res)
        #
        # res = await DepartmentService.get_com_tree('ec9ab455f91c46c9abaf47d508182972')
        # print(res)

        # res = await DepartmentService.get_parent_tree(
        #     'ec9ab455f91c46c9abaf47d508182972', ['82be8463-93fc-4f55-9232-96beb8233022']
        # )
        # print(res)
        import time
        time_1 = time.perf_counter()
        res = await DepartmentService.get_com_list(
            '0a946cfced9d4c10853a3600dbc9d508'
        )
        time_2 = time.perf_counter()
        print(res)
        print("xxxx111", time_2-time_1)

        # 父部门
        # res = await DepartmentService.get_parent_ids(
        #     "0a946cfced9d4c10853a3600dbc9d508", ["9e614c2efa6c4d0787d5e4ccf0310c58", "95d97337f56246e4b59eb8060ddb56ea"]
        # )
        # print(res)
        # time_3 = time.perf_counter()
        # print("zzz", time_3-time_2)
        # res = await DepartmentService.get_dept_parent_ids(
        #     "0a946cfced9d4c10853a3600dbc9d508", ["9e614c2efa6c4d0787d5e4ccf0310c58", "95d97337f56246e4b59eb8060ddb56ea"]
        # )
        # print(res)
        # time_4 = time.perf_counter()
        # print("zzz", time_4 - time_3)

        # 子部门
        # res = await DepartmentService.get_children_ids(
        #     "0a946cfced9d4c10853a3600dbc9d508", ["9e614c2efa6c4d0787d5e4ccf0310c58", "95d97337f56246e4b59eb8060ddb56ea"]
        # )
        # print(res)
        # time_3 = time.perf_counter()
        # print("zzz", time_3 - time_2)
        # res = await DepartmentService.get_dept_children_ids(
        #     "0a946cfced9d4c10853a3600dbc9d508", ["9e614c2efa6c4d0787d5e4ccf0310c58", "95d97337f56246e4b59eb8060ddb56ea"]
        # )
        # print(res)
        # time_4 = time.perf_counter()
        # print("zzz", time_4 - time_3)

        # time_3 = time.perf_counter()
        # res = await DepartmentService.get_com_tree(
        #     '0a946cfced9d4c10853a3600dbc9d508'
        # )
        # time_4 = time.perf_counter()
        # print(res)
        # print("yyyy111", time_4-time_3)

    asyncio.get_event_loop().run_until_complete(helper())
