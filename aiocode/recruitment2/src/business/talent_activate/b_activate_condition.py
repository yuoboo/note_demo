from collections import defaultdict

from kits.exception import APIValidationError
from services import svc

from utils.strutils import uuid2str


class TalentActivateConditionBusiness(object):
    """
    人才激活条件检验
    """
    @classmethod
    async def verify_candidate(cls, company_id: str, candidate_id: str):
        """
        单个校验候选人是否可以激活
        @param company_id:
        @param candidate_id:
        @return:
        """
        res = {"result": True, "code": 0, "msg": ""}
        candidate_id = uuid2str(candidate_id)
        candidate_list = await svc.candidate.get_candidates_by_ids(
            company_id, [candidate_id], ["id", "name", "mobile"]
        )
        candidate = candidate_list[0] if candidate_list else None
        if not candidate:
            raise APIValidationError(msg='候选人不存在')
        mobile = candidate.get("mobile")
        if not mobile:
            res.update(
                {"result": False, "code": 1, "msg": "人才没有手机号，无法发起激活！"}
            )
            return res

        records = await svc.candidate_record.get_recruiting_records_by_candidate_ids(
            company_id, [candidate_id], ["id"]
        )
        if records:
            res.update(
                {"result": False, "code": 2, "msg": "人才已成为候选人，无法发起激活！"}
            )
            return res
        emp_res = await svc.http_employee.verify_employee_by_mobiles(
            company_id, [mobile]
        )
        if emp_res.get("intention_emp_list"):
            res.update(
                {"result": False, "code": 3, "msg": "人才待入职，无法发起激活！"}
            )
            return res
        if emp_res.get("emp_list"):
            res.update(
                {"result": False, "code": 4, "msg": "人才已在职，无法发起激活！"}
            )
            return res

        return res

    @staticmethod
    async def _verify_candidate_mobile(company_id: str, candidate_ids: list):
        """
        校验是否空手机号
        @param company_id:
        @param candidate_ids:
        @return:
        """
        none_mobile_candidates = []
        candidate_list = await svc.candidate.get_candidates_by_ids(
            company_id, candidate_ids, ["id", "name", "mobile"]
        )
        # 校验手机号为空的
        id2other_candidate = {}
        for candidate in candidate_list:
            mobile = candidate.get("mobile")
            if mobile:
                id2other_candidate[candidate.get("id")] = candidate
            else:
                none_mobile_candidates.append(candidate)

        return none_mobile_candidates, id2other_candidate

    @staticmethod
    async def _verify_recruiting_records(company_id: str, id2candidate: dict):
        """
        校验是否有招聘中记录
        @param company_id:
        @param id2candidate:
        @return:
        """
        exist_recruiting_candidates = []
        records = await svc.candidate_record.get_recruiting_records_by_candidate_ids(
            company_id, list(id2candidate.keys()), ["id", "candidate_id"]
        )
        for record in records:
            candidate_id = record.get("candidate_id")
            candidate = id2candidate.pop(candidate_id, None)
            if candidate:
                exist_recruiting_candidates.append(candidate)

        return exist_recruiting_candidates, id2candidate

    @staticmethod
    async def _verify_employed_emp(company_id: str, id2candidate: dict):
        """
        校验是否在职员工（在职和待入职）
        @param company_id:
        @param id2candidate:
        @return:
        """
        intention_candidates = []
        employed_candidates = []
        mobile2candidates = defaultdict(list)
        if id2candidate:
            for _, candidate in id2candidate.items():
                mobile2candidates.setdefault(candidate.get("mobile"), []).append(candidate)
        if mobile2candidates:
            emp_res = await svc.http_employee.verify_employee_by_mobiles(
                company_id, list(mobile2candidates.keys())
            )
            emp_list = emp_res.get("emp_list") or []
            emp_mobiles = []
            for emp in emp_list:
                employed_candidates.extend(mobile2candidates.get(emp.get("mobile"), []))
                emp_mobiles.append(emp.get("mobile"))
            intention_emp_list = emp_res.get("intention_emp_list") or []
            for intention in intention_emp_list:
                if intention.get("mobile") not in emp_mobiles:
                    intention_candidates.extend(mobile2candidates.get(intention.get("mobile"), []))

        return employed_candidates, intention_candidates

    @classmethod
    async def batch_verify_candidates(cls, company_id: str, candidate_ids: list):
        """
        批量校验候选人是否满足激活
        @param company_id:
        @param candidate_ids:
        @return:
        """
        candidate_ids = [uuid2str(_id) for _id in candidate_ids]
        # 校验手机号为空
        none_mobile_candidates, id2other_candidate = await cls._verify_candidate_mobile(
            company_id, candidate_ids
        )
        # 校验有招聘中记录的
        exist_recruiting_candidates = []
        if id2other_candidate:
            exist_recruiting_candidates, id2other_candidate = await cls._verify_recruiting_records(
                company_id, id2other_candidate
            )
        # 校验是否在职或者人事待入职
        employed_candidates = []
        intention_candidates = []
        if id2other_candidate:
            employed_candidates, intention_candidates = await cls._verify_employed_emp(company_id, id2other_candidate)

        res = {
            "none_mobile_count": len(none_mobile_candidates),
            "none_mobile_candidates": none_mobile_candidates,
            "recruiting_count": len(exist_recruiting_candidates),
            "recruiting_candidates": exist_recruiting_candidates,
            "employed_count": len(employed_candidates),
            "employed_candidates": employed_candidates,
            "intention_count": len(intention_candidates),
            "intention_candidates": intention_candidates
        }

        return res
