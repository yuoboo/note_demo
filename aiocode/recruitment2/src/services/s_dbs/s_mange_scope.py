# coding: utf-8
from __future__ import absolute_import
import sqlalchemy as sa
import ujson
from sqlalchemy import join, and_, or_

from constants.redis_keys import COMPANY_USER_MANAGE_SCOPE
from drivers.mysql import db
from constants import ParticipantType, CandidateRecordStage, CrStatus
from drivers.redis import redis_db
from kits.exception import ServiceError
from utils.ehr_request import EhrRequest
from utils.sa_db import db_executor
from utils.strutils import uuid2str
from utils.logger import http_logger
from utils.api_auth import validate_permission
from models.m_job_position import tb_job_position, tb_job_position_participant_rel
from models.m_recruitment_team import tb_participant, tb_hr_emp_rel
from models.m_candidate_record import tb_candidate_record_participant_rel


class ManageScopeService(object):

    @classmethod
    async def _get_manage_deps(cls, company_id: str, user_id: str, raise_exception: bool = True) -> list:
        """
        获取管理部门信息
        """
        scope_params = {
            "company_id": uuid2str(company_id),
            "user_id": uuid2str(user_id),
            "perm_code": "recruitment"
        }
        res = await EhrRequest("ucenter").intranet("company_user/scope_id").get(data=scope_params)
        if not res or res["resultcode"] != 200:
            http_logger.error(f'获取管理范围失败，参数：{scope_params}, 返回: {res}')
            if raise_exception:
                raise ServiceError(msg="获取管理范围失败")
            return []

        # 管理范围为空
        if not res.get("data"):
            return []
        scope_id = res["data"].get("scope_id")
        dep_params = {
            "company_id": uuid2str(company_id),
            "scope_ids": [scope_id],
            "is_sub": True
        }
        res = await EhrRequest("employee").intranet("manage_scope/batch_detail_basic").post(data=dep_params)
        if not res or res["resultcode"] != 200:
            return []

        dep_ids = res.get("data", {}).get(uuid2str(scope_id), {}).get("dept", {}).get("ids", [])
        return dep_ids

    @classmethod
    async def _get_participant_relation_ids(
            cls, company_id: str, user_id: str, user_type: int = ParticipantType.HR
    ) -> dict:
        """
        获取用户在招聘参与的职位及应聘记录
        """
        engine = await db.default_db
        p_stmt = sa.select(
            [tb_participant.c.id.label("id")]
        ).where(
            and_(
                tb_participant.c.company_id == uuid2str(company_id),
                tb_participant.c.participant_refer_id == user_id,
                tb_participant.c.participant_type == user_type,
                tb_participant.c.is_delete == 0
            )
        )
        participant = await db_executor.fetch_one_data(engine, p_stmt)
        j_position_items = []
        c_record_items = []
        if participant:
            participant_id = participant["id"]

            position_stmt = sa.select([
                tb_job_position_participant_rel.c.job_position_id.label("job_position_id")
            ]).where(
                and_(
                    tb_job_position_participant_rel.c.participant_id == participant_id,
                    tb_job_position_participant_rel.c.is_delete == 0
                )
            )
            j_position_items = await db_executor.fetch_all_data(engine, position_stmt)
            c_record_items = []
            # 只有员工角色才会有参与的应聘记录这一项
            if user_type == ParticipantType.EMPLOYEE:
                record_stmt = sa.select([
                    tb_candidate_record_participant_rel.c.candidate_record_id.label("candidate_record_id")
                ]).where(
                    and_(
                        tb_candidate_record_participant_rel.c.participant_id == participant_id,
                        tb_candidate_record_participant_rel.c.is_delete == 0
                    )
                )
                c_record_items = await db_executor.fetch_all_data(engine, record_stmt)

        j_position_ids = set([uuid2str(item["job_position_id"]) for item in j_position_items])
        c_record_ids = set([uuid2str(item["candidate_record_id"]) for item in c_record_items])

        return {"position_ids": list(j_position_ids), "record_ids": list(c_record_ids)}

    @classmethod
    async def _get_participant_position_ids(cls, company_id: str, refer_ids: list) -> list:
        """
        获取用户参与的职位ids
        @param company_id:
        @param refer_ids:
        @return:
        """
        company_id = uuid2str(company_id)
        refer_ids = [uuid2str(refer_id) for refer_id in refer_ids]

        tbs = join(
            tb_participant, tb_job_position_participant_rel,
            tb_job_position_participant_rel.c.participant_id == tb_participant.c.id
        )
        exp = sa.select([
            tb_job_position_participant_rel.c.job_position_id.label("job_position_id")
        ]).where(
            and_(
                tb_participant.c.is_delete == 0,
                tb_participant.c.company_id == company_id,
                tb_participant.c.participant_refer_id.in_(refer_ids),
                tb_job_position_participant_rel.c.is_delete == 0
            )
        ).select_from(tbs)
        engine = await db.default_db
        j_position_items = await db_executor.fetch_all_data(engine, exp)
        position_ids = set([uuid2str(item[0]) for item in j_position_items if item and item[0]])
        return list(position_ids)

    @classmethod
    async def hr_manage_scope(cls, company_id: str, user_id: str) -> dict:
        """
        HR管理职位ids
        """
        company_id, user_id = uuid2str(company_id), uuid2str(user_id)
        redis_cli = await redis_db.default_redis
        scope_key = COMPANY_USER_MANAGE_SCOPE[0].format(company_id=company_id, user_id=user_id)
        position_ids = await redis_cli.get(scope_key)
        if position_ids:
            return {"position_ids": ujson.loads(position_ids)}

        # 用户中心设置的管理范围
        scope_dep_ids = await cls._get_manage_deps(company_id, user_id)
        scope_dep_ids = [uuid2str(s) for s in scope_dep_ids]
        # 招聘设置的参与的职位信息
        participant_ids = await cls._get_participant_relation_ids(
            company_id, user_id, user_type=ParticipantType.HR
        )
        position_ids = participant_ids.get("position_ids") or []

        exp = sa.select([
            tb_job_position.c.id.label("id")
        ]).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.is_delete == 0,
                or_(
                    tb_job_position.c.dep_id.in_(scope_dep_ids),
                    tb_job_position.c.dep_id.is_(None),
                    tb_job_position.c.id.in_(position_ids)
                )
            )
        )
        if not await validate_permission(company_id, user_id, "recruitment:secret_position"):
            exp = exp.where(
                tb_job_position.c.secret_position == 0
            )

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        position_ids = [uuid2str(v[0]) for v in items if v]
        # 缓存redis:3min
        await redis_cli.setex(scope_key, COMPANY_USER_MANAGE_SCOPE[1], ujson.dumps(position_ids))

        return {"position_ids": position_ids}

    @classmethod
    async def _get_user_id_by_emp_id(cls, company_id: str, emp_id: str) -> str:
        stmt = sa.select([
            tb_hr_emp_rel.c.hr_id.label("user_id")
        ]).where(
            and_(
                tb_hr_emp_rel.c.company_id == company_id,
                tb_hr_emp_rel.c.emp_id == emp_id,
                tb_hr_emp_rel.c.is_delete == 0
            )
        )

        tbs = join(
            tb_hr_emp_rel, tb_participant,
            tb_hr_emp_rel.c.hr_id == tb_participant.c.participant_refer_id
        )

        stmt = stmt.select_from(tbs).where(
            and_(
                tb_participant.c.company_id == company_id,
                tb_participant.c.participant_type == 1,
                tb_participant.c.is_delete == 0,
                tb_participant.c.participant_refer_status == 0
            )
        )

        engine = await db.default_db
        item = await db_executor.fetch_one_data(engine, stmt)

        return item["user_id"] if item else None

    @classmethod
    async def emp_manage_scope(cls, company_id: str, emp_id: str) -> dict:
        """
        员工管理职位ids
        """
        company_id = uuid2str(company_id)
        emp_id = uuid2str(emp_id)
        user_id = await cls._get_user_id_by_emp_id(company_id, emp_id)

        participant_r_ids = await cls._get_participant_relation_ids(
            company_id, emp_id, user_type=ParticipantType.EMPLOYEE
        )
        position_ids = participant_r_ids.get("position_ids") or []
        record_ids = participant_r_ids.get("record_ids") or []
        if user_id:
            res_data = await cls.hr_manage_scope(company_id, user_id)
            position_ids.extend(res_data.get("position_ids"))

        data = {
            "position_ids": position_ids, "record_ids": record_ids, "user_id": user_id
        }

        return data

    @classmethod
    async def user_manage_dep_ids(cls, company_id: str, refer_id: str, user_type: int) -> list:
        """
        查询用户的管理职位的部门（不包括参与的应聘记录的职位）
        @param company_id:
        @param refer_id:
        @param user_type:
        @return:
        """
        company_id = uuid2str(company_id)
        refer_id = uuid2str(refer_id)

        async def _filter_by_scope_and_positions(filter_exp, hr_id, p_ids):     # p_ids -> 职位id
            scope_dep_ids = await cls._get_manage_deps(company_id, hr_id)
            scope_dep_ids = [uuid2str(s) for s in scope_dep_ids]
            filter_exp = filter_exp.where(
                or_(
                    tb_job_position.c.dep_id.in_(scope_dep_ids),
                    tb_job_position.c.id.in_(p_ids)
                )
            )
            if not await validate_permission(company_id, hr_id, "recruitment:secret_position"):
                filter_exp = filter_exp.where(tb_job_position.c.secret_position == 0)
            return filter_exp

        exp = sa.select([
            tb_job_position.c.dep_id.label("dep_id")
        ]).where(
            and_(
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.is_delete == 0,
            )
        )
        if user_type == ParticipantType.HR:
            position_ids = await cls._get_participant_position_ids(company_id, [refer_id])
            exp = await _filter_by_scope_and_positions(exp, refer_id, position_ids)

        else:
            user_id = await cls._get_user_id_by_emp_id(company_id, refer_id)
            if user_id:
                position_ids = await cls._get_participant_position_ids(company_id, [user_id, refer_id])
                exp = await _filter_by_scope_and_positions(exp, user_id, position_ids)

            else:
                position_ids = await cls._get_participant_position_ids(company_id, [refer_id])
                exp = exp.where(tb_job_position.c.id.in_(position_ids))
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)

        return list(set([uuid2str(dep_id[0]) for dep_id in items if dep_id and dep_id[0]]))

    @classmethod
    async def validate_record_permission(
            cls, company_id: str, user_id: str, user_type: int, position_id: str, candidate_record_id: str
    ) -> bool:
        """
        验证指定应聘记录是否有访问权限
        @param company_id:
        @param user_id:
        @param user_type:
        @param position_id:
        @param candidate_record_id:
        @return:
        """
        position_id = uuid2str(position_id)
        candidate_record_id = uuid2str(candidate_record_id)
        if user_type == ParticipantType.HR:
            res_data = await cls.hr_manage_scope(company_id, user_id)
        else:
            res_data = await cls.emp_manage_scope(company_id, user_id)
        position_ids = res_data.get("position_ids") or []
        record_ids = res_data.get("record_ids") or []
        if any(
                [
                    position_id in position_ids,
                    candidate_record_id in record_ids
                ]
        ):
            return True
        return False


class PermissionCodeService(object):

    @classmethod
    def get_operate_stage(cls, record_status):
        """
        获取操作阶段
        """
        primary_stages = (
            CrStatus.TO_BE_PRELIMINARY_SCREEN, CrStatus.PRELIMINARY_SCREEN_PASSED,
            CrStatus.PRELIMINARY_SCREEN_ELIMINATE
        )

        interview_stages = (
            CrStatus.INTERVIEW_ARRANGED, CrStatus.INTERVIEWED,
            CrStatus.INTERVIEW_PASSED, CrStatus.INTERVIEW_ELIMINATE
        )

        employ_stages = (
            CrStatus.PROPOSED_EMPLOYMENT, CrStatus.OFFER_ISSUED,
            CrStatus.TO_BE_EMPLOYED, CrStatus.EMPLOYED,
            CrStatus.EMPLOYMENT_CANCELED
        )

        stage = None
        if record_status in primary_stages:
            stage = CandidateRecordStage.PRIMARY_STAGE
        if record_status in interview_stages:
            stage = CandidateRecordStage.INTERVIEW_STAGE
        if record_status in employ_stages:
            stage = CandidateRecordStage.EMPLOY_STAGE
        return stage

    @classmethod
    async def get_permission_code_by_status(
            cls, target_status: int = CandidateRecordStage.PRIMARY_STAGE,
            default_permission: str = "recruitment:screen_resume"
    ) -> str:
        """
        获取权限编码
        """
        stage2permission_code = {
            CandidateRecordStage.PRIMARY_STAGE: "recruitment:screen_resume",
            CandidateRecordStage.INTERVIEW_STAGE: "recruitment:interview_following",
            CandidateRecordStage.EMPLOY_STAGE: "recruitment:employed_following"
        }

        stage = cls.get_operate_stage(target_status)
        return stage2permission_code.get(stage, default_permission)
