import asyncio
import datetime

import aiotask_context

from business.b_wework import WeWorkBusiness
from business.commons import com_biz
from celery_worker import celery_app
from constants import CandidateRecordStatus, CandidateRecordSource, RecruitPageType, DeliveryType, ParticipantType
from constants.commons import null_uuid
from kits.exception import APIValidationError
from services import svc
from services.s_dbs.candidate_records.s_comment_record import CommentRecordService
from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordService
from services.s_dbs.s_job_position import JobPositionSelectService
from services.s_dbs.portals.s_portal_delivery import DeliveryRecordService
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService
from services.s_dbs.s_candidate import CandidateService as CandidateRead
from services.s_dbs.s_wework import WeWorkService
from services.s_dbs.s_wx_recruitment import RecruitmentPageRecord
from services.s_dbs.talent_activate.s_activate_record import ActivateRecordService
from services.s_https import s_ucenter
from services.s_https.s_bigdata import BigDataService, BigDataDateFormat
from services.s_https.s_candidate import CandidateService
from services.s_https.s_employee import EmployeeService, DepartmentService
from services.s_https.s_wework import WeWorkExternalContactService
from utils.excel_util import ListExport
from error_code import Code as ErrorCode
from utils.strutils import uuid2str
from utils.time_cal import get_date_min_datetime, get_date_max_datetime


def page_blank_ret(p, limit):
    return {
        "p": p,
        "limit": limit,
        "offset": 1,
        "totalpage": 0,
        "total_count": 0,
        "objects": []
    }


class ReferralRecordExport(ListExport):
    """
    投递记录导出
    """
    header = ["投递时间", "候选人姓名", "候选人手机号码", "投递职位", "用人部门", "候选人状态", "推荐人姓名",
              "推荐人手机号", "推荐理由", "内推奖励", "内推奖励是否发放", "招聘门户"]
    fields = ["add_dt", "candidate_name", "candidate_mobile", "referral_position_name", "dep_name", "candidate_status",
              "referee_name", "referee_mobile", "reason", "referral_bonus", "is_payed", "recruitment_page_name"]

    @staticmethod
    def format_status_str(status: int, interview_count: int = None):
        if status in CandidateRecordStatus.attrs_:
            _status_str = CandidateRecordStatus.attrs_[status]
            if status in (
                    CandidateRecordStatus.INTERVIEW_STEP1, CandidateRecordStatus.INTERVIEW_STEP2,
                    CandidateRecordStatus.INTERVIEW_STEP3, CandidateRecordStatus.INTERVIEW_STEP4):
                _status_str += f'（第{interview_count}轮）' if interview_count else 1
            return _status_str
        return ""

    def clean_row_data(self, row):
        row["add_dt"] = str(row.get("add_dt", ""))
        _candidate = row.get("candidate", {})
        _record = row.get("candidate_record", {})
        _position = row.get("job_position", {})
        _portal_position = row.get("portal_position", {})
        _page = row.get("recruitment_page", {})
        row["candidate_name"] = _candidate.get("name")
        row["candidate_mobile"] = _candidate.get("mobile")
        row["referral_position_name"] = _portal_position.get("name")
        row["dep_name"] = _position.get("dep_name")
        row["candidate_status"] = self.format_status_str(_record.get("status", 0), _record.get("interview_count", 0))
        row["referee_name"] = _record.get("referee_name")
        row["referee_name"] = _record.get("referee_name")
        row["referee_mobile"] = _record.get("referee_mobile")
        row["is_payed"] = "是" if row.get("is_payed") else "否"
        row["recruitment_page_name"] = _page.get("name")
        return row


class EmpReferralRecordExport(ReferralRecordExport):
    """
    内推记录导出(员工端)
    """
    header = ["投递时间", "候选人姓名", "候选人手机号码", "推荐理由", "内推职位", "内推奖励", "招聘门户"]
    fields = ["add_dt", "candidate_name", "candidate_mobile", "reason", "referral_position_name", "referral_bonus",
              "recruitment_page_name"]


class RecruitPortalPostManageBiz:
    """
    招聘门户投递管理
    """
    @staticmethod
    def add_future_task(task):
        """
        :param task: future, couroutine or awaitable
        :return:
        """
        if task:
            _app = aiotask_context.get("app")
            _app.add_task(task)

    @classmethod
    async def we_work_add_candidate_by_hr(
            cls, company_id: str, user_id: str, form_data: dict,
            attachments: list = None, source: int = CandidateRecordSource.HR
    ):
        """
        企业微信侧边栏HR 添加候选人
        """
        job_position_id = uuid2str(form_data.get("job_position_id"))
        resume_key = uuid2str(form_data.get("resume_key"))
        candidate_name = form_data.get("candidate_name")
        mobile = form_data.get("mobile")
        external_id = form_data.get("external_id")
        status = form_data.get("status", CandidateRecordStatus.PRIMARY_STEP1)
        recruit_channel_id = uuid2str(form_data.get("recruit_channel_id")) or None

        if status not in CandidateRecordStatus.attrs_:
            raise APIValidationError(msg="候选人状态参数错误")

        # 根据外部联系人id获取候选人unionid, 外部联系人id与app_id相关
        app_id = await WeWorkBusiness.get_company_app_id(company_id)
        wx_service = WeWorkExternalContactService(app_id=app_id, company_id=company_id)
        external_contact = await wx_service.get_external_contact(external_id)
        if not external_contact:
            raise APIValidationError(ErrorCode.we_work_external_user_error)

        external_unionid = external_contact.get("unionid") or ""

        # 校验职位是否在招聘中
        _position = await JobPositionSelectService.get_positions_by_ids(
            company_id, ids=[job_position_id], fields=["id"], query_params={"status": 1}
        )
        if not _position:
            raise APIValidationError(ErrorCode.job_position_not_exist)

        await cls._check_position_and_record(     # 校验是否存在相同应聘记录(在职员工及黑名单求职者中心有校验)
            company_id, candidate_name, mobile, job_position_id, msg_text=candidate_name
        )

        # 创建候选人和标准简历信息
        candidate_result = await CandidateService.create_candidate_by_form_data_and_attach(
            company_id=company_id,
            candidate_data={"candidate_name": candidate_name, "mobile": mobile},
            candidate_attachments=attachments, file_key=resume_key
        )
        candidate_id = candidate_result.get("candidate_id")
        candidate_record_id = candidate_result.get("candidate_record_id")
        # 创建应聘记录
        # await CandidateRecordCreateService.create_candidate_record(
        #     company_id, user_id, candidate_id, candidate_record_id,
        #     job_position_id, recruit_channel_id, status, source=source
        # )
        await com_biz.cr.create_candidate_record(
            company_id, user_id, candidate_id, job_position_id,
            status=status,
            candidate_record_id=candidate_record_id,
            recruitment_channel_id=recruit_channel_id,
            source=source
        )
        # 数据上报
        com_biz.data_report.add_candidate_record.send_task(
            company_id=company_id, user_id=user_id,
            ev_ids=[uuid2str(candidate_record_id)], user_type=ParticipantType.HR
        )

        comment = await cls._format_comment(
            source, company_id, user_id
        )

        cls.add_future_task(
            CommentRecordService.create_comment(
                company_id, candidate_id, comment, candidate_record_id, user_type=ParticipantType.HR
            )
        )

        candidate_id = candidate_result.get("candidate_id")
        external_type = external_contact.get('type', 0)

        cls.add_future_task(
            cls.create_or_update_external_contact(
                company_id, external_unionid, candidate_name, candidate_id,
                external_type=external_type, external_id=external_id
            )
        )

        return candidate_result

    @classmethod
    async def we_work_referral_record(
            cls, company_id: str, user_id: str, form_data: dict,
            attachments: list = None, open_id: str = "", union_id: str = "",
            source: int = CandidateRecordSource.EMP_RECOMMENDATION):
        """
        企业微信侧边栏内推记录
        """
        referral_position_id = uuid2str(form_data.get("position_record_id"))
        referee_id = uuid2str(user_id)
        resume_key = uuid2str(form_data.get("resume_key"))
        candidate_name = form_data.get("candidate_name")
        external_id = form_data.get("external_id")
        reason = form_data.get("reason", "")
        portal_id = uuid2str(form_data.get("portal_id"))

        app_id = await WeWorkBusiness.get_company_app_id(company_id)
        wx_service = WeWorkExternalContactService(app_id=app_id, company_id=company_id)
        external_contact = await wx_service.get_external_contact(external_id)

        if not external_contact:
            raise APIValidationError(ErrorCode.we_work_external_user_error)

        external_unionid = external_contact.get("unionid") or ""

        candidate_data = {
            "candidate_name": candidate_name,
            "mobile": form_data.get("mobile"),
        }
        cr_info = await cls.handle_delivery_record_by_resume(
            company_id=company_id, candidate_data=candidate_data,
            position_record_id=referral_position_id, resume_key=resume_key,
            attachments=attachments, user_id=user_id,
            referee_id=referee_id, reason=reason, recruitment_page_id=portal_id,
            delivery_type=DeliveryType.employee,
            open_id=open_id, union_id=union_id, source=source
        )

        candidate_id = cr_info.get("candidate_id")
        external_type = external_contact.get('type', 0)

        cls.add_future_task(
            cls.create_or_update_external_contact(
                company_id, external_unionid, candidate_name, candidate_id,
                external_type=external_type, external_id=external_id
            )
        )

    @classmethod
    async def candidate_delivery_record(
            cls, company_id: str, form_data: dict, position_record_id: str, resume_key: str,
            recruitment_channel_id: str = None, attachments: list = None,
            referee_id: str = None, reason: str = "",
            open_id: str = "", union_id: str = "", msg_text: str = "您", user_id: str = null_uuid,
            delivery_type=DeliveryType.candidate,
            source: int = CandidateRecordSource.SELF_RECOMMENDATION,
            activate_id: str = None
    ):
        """
        求职者主动投递简历
        需要判断是否存在外部联系人
        """
        position_position_id = uuid2str(position_record_id) or None
        referee_id = uuid2str(referee_id) or None
        resume_key = uuid2str(resume_key)
        recruitment_channel_id = uuid2str(recruitment_channel_id) if recruitment_channel_id else None
        user_id = uuid2str(user_id) or referee_id

        cr_info = await cls.handle_delivery_record_by_resume(
            company_id=company_id, candidate_data=form_data,
            position_record_id=position_position_id, resume_key=resume_key, attachments=attachments,
            referee_id=referee_id, reason=reason,
            recruitment_channel_id=recruitment_channel_id,
            delivery_type=delivery_type, open_id=open_id, union_id=union_id, msg_text=msg_text,
            user_id=user_id, source=source, activate_id=activate_id, user_type=ParticipantType.NONE
        )

        # 更新外部联系人信息
        candidate_id = cr_info.get("candidate_id")
        candidate_name = form_data.get("candidate_name")
        cls.add_future_task(
            cls.create_or_update_external_contact(company_id, union_id, candidate_name, candidate_id)
        )
        return cr_info

    @classmethod
    async def create_referral_record(
            cls, company_id: str, user_id: str, form_data: dict,
            attachments: list = None, open_id: str = None, union_id: str = None,
            source: int = CandidateRecordSource.EMP_RECOMMENDATION):
        """
        推荐简历(员工内推)
        """
        position_record_id = uuid2str(form_data.get("position_record_id"))
        referee_id = uuid2str(form_data.get("referee_id"))
        referee_id = referee_id if referee_id else user_id
        resume_key = uuid2str(form_data.get("resume_key"))
        reason = form_data.get("reason", "")
        portal_id = uuid2str(form_data.get("portal_id"))
        candidate_data = {
            "candidate_name": form_data.get("candidate_name"),
            "mobile": form_data.get("mobile")
        }
        await cls.handle_delivery_record_by_resume(
            company_id=company_id, candidate_data=candidate_data,
            position_record_id=position_record_id, resume_key=resume_key,
            attachments=attachments, user_id=user_id, referee_id=referee_id, reason=reason,
            delivery_type=DeliveryType.employee,
            open_id=open_id, union_id=union_id, source=source, recruitment_page_id=portal_id
        )

    @staticmethod
    async def _get_delivery_channel(company_id: str, referee_id: str, recruit_channel_id: str, page_id: str,
                                    activate_id: str):
        """
        获取渠道信息和内推人信息
        @param company_id:
        @param referee_id:
        @param recruit_channel_id: 招聘渠道ID
        @param page_id: 招聘网页ID
        @return:
        """
        emp_info = {}

        # 查询内推渠道id
        if referee_id:
            channel_id, emp_info_list = await asyncio.gather(
                RecruitmentChannelService.find_channel_by_name(company_id, "内推"),
                EmployeeService.get_employee_info_by_ids(
                    company_id, [referee_id], ["emp_name", "mobile"]
                )
            )
            emp_info = emp_info_list[0] if emp_info_list else {}
        elif activate_id:
            channel_id = await RecruitmentChannelService.find_channel_by_name(company_id, "人才激活")
        else:
            if not recruit_channel_id:
                channel_info = await RecruitmentPageRecord.get_one_page(
                    company_id, pk=page_id, fields=["recruitment_channel_id"]
                )
                recruit_channel_id = channel_info.get("recruitment_channel_id")

            channel_id = recruit_channel_id

        return channel_id, emp_info

    @staticmethod
    def _get_delivery_scene(referee_id, activate_id):
        delivery_scene = RecruitPageType.wx_recruit
        if referee_id:
            delivery_scene = RecruitPageType.referral
        if activate_id:
            delivery_scene = RecruitPageType.talent_activate
        return delivery_scene

    @staticmethod
    async def _get_activate_candidate(company_id: str, mobile: str, activate_id: str):
        """
        获取激活候选人
        @param company_id:
        @param mobile:
        @param activate_id:
        @return:
        """
        candidate_id = None
        # 如果是激活链接投递，需要根据现有候选人创建应聘记录，判断条件：激活记录和手机号，因为激活链接也存在被转发
        if activate_id:
            record = await ActivateRecordService.get_activate_record_by(
                company_id, activate_id, ["candidate_id"]
            )
            if record:
                candidates = await CandidateRead.get_candidates_by_ids(
                    company_id, [record.get("candidate_id")], ["mobile"]
                )
                candidate = candidates[0] if candidates else {}
                if mobile == candidate.get("mobile"):
                    candidate_id = record.get("candidate_id")
        return candidate_id

    @classmethod
    async def handle_delivery_record_by_resume(
            cls, company_id: str, candidate_data: dict, position_record_id: str,  resume_key: str,
            attachments: list = None, referee_id: str = None, reason: str = None,
            open_id: str = None, union_id: str = None, msg_text: str = None, is_blacklist: bool = False,
            recruitment_channel_id: str = None, recruitment_page_id: str = None,
            user_id: str = null_uuid, user_type: int = ParticipantType.EMPLOYEE,
            delivery_type: int = DeliveryType.employee,
            candidate_record_status: int = CandidateRecordStatus.PRIMARY_STEP1,
            source: int = CandidateRecordSource.EMP_RECOMMENDATION,
            activate_id: str = None
    ) -> dict:
        user_id = user_id or null_uuid
        candidate_name = candidate_data.get("candidate_name")
        mobile = candidate_data.get("mobile")

        # 校验招聘门户关联职位
        portal_position = await svc.portal_position.get_portal_position_by_id(
            company_id=company_id, pk=position_record_id,
            fields=["id", "job_position_id", "referral_bonus", "recruitment_page_id"]
        )
        if not portal_position:
            msg = "内推职位不存在" if referee_id else "应聘职位不存在"
            raise APIValidationError(msg=msg)
        else:
            job_position_id = portal_position["job_position_id"]
        activate_candidate_id = await cls._get_activate_candidate(company_id, mobile, activate_id)

        # 如果是激活不需要进行此校验：即激活允许同一职位存在多个应聘记录（在职员工及黑名单求职者中心有校验）
        if not activate_candidate_id:
            await cls._check_position_and_record(
                company_id, candidate_name, mobile, job_position_id, msg_text=msg_text
            )

        recruitment_page_id = recruitment_page_id or portal_position["recruitment_page_id"]
        channel_id, emp_info = await cls._get_delivery_channel(
            company_id, referee_id, recruitment_channel_id, recruitment_page_id, activate_id
        )
        channel_id = channel_id or None

        # 创建候选人和标准简历信息(如果是对存在候选人进行激活，则需要更新候选人的简历)
        candidate_result = await CandidateService.create_candidate_by_form_data_and_attach(
            company_id=company_id,
            candidate_data=candidate_data,
            candidate_attachments=attachments, file_key=resume_key, candidate_id=activate_candidate_id,
            update_talent_resume=True if activate_candidate_id else False
        )
        candidate_id = candidate_result.get("candidate_id")
        candidate_record_id = candidate_result.get("candidate_record_id")
        # 创建应聘记录
        cr_task = com_biz.cr.create_candidate_record(
            company_id, user_id, candidate_id, job_position_id,
            status=candidate_record_status,
            candidate_record_id=candidate_record_id,
            recruitment_channel_id=channel_id,
            source=source,
            referee_id=referee_id,
            referee_name=emp_info.get("emp_name", ""),
            referee_mobile=emp_info.get("mobile", ""),
            recruitment_page_id=recruitment_page_id or ""
        )

        # 创建投递记录
        delivery_scene = cls._get_delivery_scene(referee_id, activate_id)
        dr_task = DeliveryRecordService.create_delivery_record(
            company_id=company_id, candidate_record_id=candidate_record_id,
            position_record_id=position_record_id, recruitment_page_id=recruitment_page_id,
            delivery_scene=delivery_scene, delivery_type=delivery_type, reason=reason,
            referee_id=referee_id or null_uuid, referral_bonus=portal_position['referral_bonus'],
            open_id=open_id, union_id=union_id, add_by_id=user_id or null_uuid
        )
        await asyncio.gather(cr_task, dr_task)

        # 数据上报
        add_by_id = uuid2str(user_id) if user_id != null_uuid else ""
        com_biz.data_report.add_candidate_record.send_task(
            company_id=uuid2str(company_id), user_id=add_by_id,
            ev_ids=[uuid2str(candidate_record_id)], user_type=user_type

        )

        comment = await cls._format_comment(
            source, company_id, user_id,
            referee_name=emp_info.get('emp_name') or "", referee_mobile=emp_info.get('mobile') or "", reason=reason,
            page_id=portal_position["recruitment_page_id"]
        )
        # 更新激活记录的状态
        if activate_candidate_id and activate_id:
            await ActivateRecordService.update_activate_status(
                company_id, activate_id, "", candidate_record_id=candidate_record_id
            )
        cls.add_future_task(
            CommentRecordService.create_comment(
                company_id, candidate_id, comment, candidate_record_id, user_type=user_type
            )
        )

        return candidate_result

    @classmethod
    async def create_or_update_external_contact(
            cls, company_id: str, unionid: str, candidate_name: str, candidate_id: str,
            external_type: int = 0, external_id: str = None
    ):
        """
        创建或者更新外部联系人
        """
        kwargs = {
            'external_type': external_type
        }
        if external_id:
            kwargs.update({
                'external_id': external_id
            })
        is_created, _obj = await WeWorkService.get_or_create(
            company_id, unionid, name=candidate_name, candidate_id=candidate_id,
            fields=["external_type", "external_id", "candidate_id"],
            **kwargs
        )
        # 如果是新创建的外部联系人信息则这里还没有关联外部联系人 没有类型更新到候选人
        if not is_created:
            await WeWorkService.update_external_contact(
                company_id, unionid, candidate_id=candidate_id, external_id=external_id, name=candidate_name
            )
            # 外部联系人id存在则需要更新外部联系人类型到候选人
            if external_id:
                # 如果旧的候选人id存在， 则将旧的候选人外部联系人显示状态改为0
                old_candidate_id = _obj.get('candidate_id', None)
                if old_candidate_id:
                    await CandidateService.update_wework_external_contact(
                        company_id=company_id,
                        candidate_id=old_candidate_id,
                        wework_external_contact=0,
                    )
                await CandidateService.update_wework_external_contact(
                    company_id=company_id,
                    candidate_id=candidate_id,
                    wework_external_contact=_obj.get("external_type"),
                )
        # 主动更新一次外部联系人的follow_user
        celery_app.send_task("apps.tasks.portals.wework.update_wework_external_contact", args=(external_id, company_id))

    @classmethod
    async def is_exist_employee(
            cls, company_id: str, name: str, mobile: str, msg_text="", is_blacklist: bool = False
    ):
        # 校验是否存在在职员工或者待入职员工
        msg_text = msg_text or name
        status, emp_id = await EmployeeService.check_employee(
            company_id=company_id, emp_name=name, emp_mobile=mobile
        )
        if emp_id:
            if status == 1:
                raise APIValidationError(msg=f'{msg_text}已在员工花名册')
            if status == 2:
                raise APIValidationError(msg=f'{msg_text}已是待入职员工')

            if is_blacklist:  # 校验黑名单
                check_ = await EmployeeService.check_blacklist(
                    company_id, emp_list=[{"name": name, "mobile": mobile}]
                )
                if check_ and check_[0].get("flag"):
                    raise APIValidationError(msg=f"{msg_text}已被加入黑名单, 原因:{check_[0].get('add_reason')}")

    @classmethod
    async def _check_position_and_record(
            cls, company_id, name, mobile, job_position_id: str, msg_text=""):

        """校验网页关联职位和应聘记录"""
        candidate_info = await CandidateService.get_candidate_by_name_and_mobile(
            company_id=company_id, name=name, mobile=mobile, auto_create=False
        )
        candidate_id = candidate_info["id"] if candidate_info else None

        if candidate_id:
            # 查询相同应聘职位的应聘记录是否存在
            candidate_record_id = await CandidateRecordService.check_candidate_record(
                company_id, job_position_id, candidate_id
            )
            if candidate_record_id:
                msg_text = msg_text or name
                raise APIValidationError(msg=f"{msg_text}已应聘相同职位")

    @classmethod
    async def _filter_manager_scope(cls, company_id: str, user_id: str, position_ids: list = None) -> list:
        """过滤管理范围"""
        _scope = await svc.manage_scope.hr_manage_scope(company_id, user_id)
        scope_position_ids = [uuid2str(_id) for _id in _scope.get("position_ids", [])]
        if position_ids:
            scope_position_ids = list(set(scope_position_ids) & set([uuid2str(_id) for _id in position_ids]))

        return scope_position_ids

    @classmethod
    async def get_referral_records(cls, company_id: str, user_id: str, form_data: dict,
                                   page: int = 1, limit: int = 20) -> dict:
        """
        获取内推记录列表 排序内推时间倒序, 分页
        显示全部投递记录，需要进行管理范围过滤，不需要进行“内推管理”权限判断
        """
        # 管理范围过滤
        position_ids = await cls._filter_manager_scope(company_id, user_id, form_data.get("position_ids", []))

        # 根据用人部门, 内推职位查询内推职位信息
        flag, cr_ids = await cls._handle_filter_by_form_data(
            company_id,
            dep_ids=form_data.get("dep_ids"),
            position_ids=position_ids,
            keyword=form_data.get("keyword"),
            referee=form_data.get("referee"),
            status=form_data.get("status"),
        )
        if not flag:
            return page_blank_ret(page, limit)

        is_payed = form_data.get("is_payed")
        start_dt = form_data.get("start_dt")
        if start_dt:
            start_dt = get_date_min_datetime(start_dt)

        end_dt = form_data.get("end_dt")
        if end_dt:
            end_dt = get_date_max_datetime(end_dt)

        is_has_bonus = form_data.get("is_has_bonus")
        portal_ids = [uuid2str(_id) for _id in form_data.get("portal_ids", [])]

        # 根据应聘记录ids, 申请职位ids, 内推时间, 是否发放奖金查询内推记录
        referral_dict = await cls.get_delivery_records_with_page(
            company_id=company_id, page=page, candidate_record_ids=cr_ids,
            is_payed=is_payed, start_dt=start_dt, end_dt=end_dt, limit=limit,
            recruitment_page_ids=portal_ids, is_has_bonus=is_has_bonus,
            fields=["id", "add_dt", "candidate_record_id", "position_record_id", "referral_bonus", "is_payed",
                    "recruitment_page_id", "reason"]
        )

        return referral_dict

    @classmethod
    async def get_emp_referral_records_with_page(
            cls, company_id: str, emp_id: str, form_data: dict,
            page: int = 1, limit: int = 20) -> dict:
        """
        获取协作平台我的内推记录
        """

        flag, cr_ids = await cls._handle_filter_by_form_data(
            company_id, dep_ids=form_data.get("dep_ids"),
            position_ids=form_data.get("position_ids"),
            keyword=form_data.get("keyword"),
            status=form_data.get("status"),
            referee=form_data.get("referee")
        )
        if not flag:
            return page_blank_ret(page, limit)

        start_dt = form_data.get("start_dt")
        if start_dt:
            start_dt = get_date_min_datetime(start_dt)

        end_dt = form_data.get("end_dt")
        if end_dt:
            end_dt = get_date_max_datetime(end_dt)

        portal_ids = [uuid2str(_id) for _id in form_data.get("portal_ids", [])]
        is_has_bonus = form_data.get("is_has_bonus")

        # 根据emp_id, 应聘记录和时间查询内推记录
        referral_record = await cls.get_delivery_records_with_page(
            company_id=company_id, page=page, limit=limit,
            candidate_record_ids=cr_ids, referee_id=emp_id,
            start_dt=start_dt, end_dt=end_dt, recruitment_page_ids=portal_ids,
            is_has_bonus=is_has_bonus,
            fields=["id", "add_dt", "candidate_record_id", "position_record_id", "add_by_id",
                    "referral_bonus", "recruitment_page_id", "reason"]
        )

        return referral_record

    @classmethod
    async def get_my_referral_records_with_page(
            cls, company_id: str, referee_id: str = None,
            page: int = 1, limit: int = 20) -> dict:
        """
        小程序我的内推记录
        """
        return await cls.get_delivery_records_with_page(
            company_id, referee_id=referee_id, page=page, limit=limit
        )

    @classmethod
    async def get_delivery_records_with_page(
            cls, company_id: str, referee_id: str = None, candidate_record_ids: list = None,
            is_payed: bool = None, start_dt: str = None, end_dt: str = None,
            recruitment_page_ids: list = None, is_has_bonus: bool = None,
            page: int = 1, limit: int = 20, fields: list = None) -> dict:
        """
        查询投递记录
        :param company_id:
        :param referee_id: 内推人
        :param candidate_record_ids: 应聘记录ids
        :param is_payed: 是否发放内推奖励
        :param start_dt: 内推时间
        :param end_dt:  内推时间
        :param recruitment_page_ids: 招聘门户id
        :param is_has_bonus: 是否有内推奖励
        :param page: 当前页码
        :param limit:
        :param fields: 返回字段
        """
        fields = fields or ["id", "add_dt", "candidate_record_id", "delivery_scene", "delivery_type", "referral_bonus",
                            "recruitment_page_id", "position_record_id", "reason"]
        referral_records = await DeliveryRecordService.get_delivery_records_with_page(
            company_id=company_id, page=page,  candidate_record_ids=candidate_record_ids,
            is_payed=is_payed, start_dt=start_dt, end_dt=end_dt, recruitment_page_ids=recruitment_page_ids,
            referee_id=referee_id, limit=limit, is_has_bonus=is_has_bonus, fields=fields
        )

        cr_ids = [_o["candidate_record_id"] for _o in referral_records["objects"]]
        position_map, candidate_map, cr_map = await cls.get_candidate_record_map(company_id, cr_ids)

        if not recruitment_page_ids:
            recruitment_page_ids = list(set([_r["recruitment_page_id"] for _r in referral_records["objects"]]))

        position_record_ids = list(set([_r["position_record_id"] for _r in referral_records["objects"]]))
        recruitment_page_map, position_records = await asyncio.gather(
            cls.get_recruitment_page_map(company_id, recruitment_page_ids),
            svc.portal_position.get_portal_positions_by_ids(
                company_id, record_ids=position_record_ids, fields=["id", "name"]
            )
        )
        position_records_map = dict(zip([_p["id"] for _p in position_records], position_records))
        for refer in referral_records["objects"]:
            _record = cr_map.get(refer["candidate_record_id"], {})
            refer["candidate"] = candidate_map.get(_record.get("candidate_id"), {})
            refer["job_position"] = position_map.get(_record.get("job_position_id"), {})
            refer["candidate_record"] = _record
            if refer.get("recruitment_page_id"):
                refer["recruitment_page"] = recruitment_page_map.get(refer["recruitment_page_id"], {})
            else:
                refer["recruitment_page"] = {}
            refer["portal_position"] = position_records_map.get(refer["position_record_id"], {})
        return referral_records

    @classmethod
    async def get_referral_records_without_page(
            cls, company_id: str, form_data: dict, emp_id: str = None,
            user_id: str = None, fields: list = None
    ) -> list:
        """
        获取内推记录数据
        """
        # 管理范围过滤
        position_ids = form_data.get("position_ids", [])
        if user_id:
            position_ids = await cls._filter_manager_scope(company_id, user_id, position_ids)

        flag, cr_ids = await cls._handle_filter_by_form_data(
            company_id, dep_ids=form_data.get("dep_ids"), keyword=form_data.get("keyword"),
            position_ids=position_ids, status=form_data.get("status"),
            referee=form_data.get("referee")
        )

        if not flag:
            return []

        start_dt = form_data.get("start_dt")
        if start_dt:
            start_dt = get_date_min_datetime(start_dt)

        end_dt = form_data.get("end_dt")
        if end_dt:
            end_dt = get_date_max_datetime(end_dt)

        portal_ids = [uuid2str(_id) for _id in form_data.get("portal_ids", [])]
        is_has_bonus = form_data.get("is_has_bonus")

        # 根据emp_id, 应聘记录和时间查询内推记录
        referral_records = await DeliveryRecordService.get_referral_records(
            company_id=company_id, candidate_record_ids=cr_ids, referee_id=emp_id,
            start_dt=start_dt, end_dt=end_dt, recruitment_page_ids=portal_ids,
            is_has_bonus=is_has_bonus, fields=fields
        )

        cr_ids = [_o["candidate_record_id"] for _o in referral_records]

        position_map, candidate_map, cr_map = await cls.get_candidate_record_map(company_id, cr_ids)

        if not portal_ids:
            portal_ids = list(set([r["recruitment_page_id"] for r in referral_records if r["recruitment_page_id"]]))

        position_record_ids = list(set([r["position_record_id"] for r in referral_records]))
        recruitment_page_map, position_records = await asyncio.gather(
            cls.get_recruitment_page_map(company_id, portal_ids),
            svc.portal_position.get_portal_positions_by_ids(
                company_id, record_ids=position_record_ids, fields=["id", "name"]
            )
        )
        position_records_map = dict(zip([_p["id"] for _p in position_records], position_records))

        for refer in referral_records:
            _record = cr_map.get(refer["candidate_record_id"], {})
            refer["job_position"] = position_map.get(_record.get("job_position_id"), {})
            refer["candidate_record"] = _record
            _candidate_id = _record.get("candidate_id")
            refer["candidate"] = candidate_map.get(_candidate_id, {})
            refer["recruitment_page"] = recruitment_page_map.get(refer.get("recruitment_page_id"), {})
            refer["portal_position"] = position_records_map.get(refer["position_record_id"], {})
        return referral_records

    @classmethod
    async def get_candidate_record_map(cls, company_id: str, candidate_record_ids: list):
        """通过应聘记录返回 应聘记录map, 招聘职位map, 候选人信息map"""
        candidate_records = await CandidateRecordService.get_candidate_records_by_ids(
            company_id, candidate_record_ids,
            fields=["id", "status", "interview_count", "candidate_id", "job_position_id",
                    "referee_name", "referee_mobile", "referee_id"]
        )
        candidate_ids = [cr["candidate_id"] for cr in candidate_records]
        position_ids = [cr["job_position_id"] for cr in candidate_records]
        candidate_task = CandidateRead.get_candidates_by_ids(
                company_id, candidate_ids, fields=["id", "name", "mobile", "avatar", 'sex']
        )
        position_task = JobPositionSelectService.get_referral_position_by_filter(
            company_id=company_id, ids=position_ids,
            fields=["id", "name", "dep_id", "dep_name"]
        )
        candidates, positions = await asyncio.gather(candidate_task, position_task)
        position_map = dict(zip([p["id"] for p in positions], positions))
        candidate_map = dict(zip([c["id"] for c in candidates], candidates))
        cr_map = dict(zip([cr["id"] for cr in candidate_records], candidate_records))
        return position_map, candidate_map, cr_map

    @classmethod
    async def get_recruitment_page_map(cls, company_id: str, page_ids: list, fields: list = None):
        _page_fields = fields or ["id", "name"]
        recruitment_page_ = await RecruitmentPageRecord.get_many_pages(
            company_id, page_ids, fields=_page_fields
        )
        recruitment_page_map = {_p["id"]: _p for _p in recruitment_page_}
        return recruitment_page_map

    @classmethod
    async def _handle_filter_by_form_data(
            cls, company_id: str, dep_ids: list = None, position_ids: list = None,
            keyword: str = None, status: list = None, referee: str = None) -> (bool, list):
        """
        处理过滤条件
        招聘职位从内推职位变更为非内推后 旧的内推记录仍然需要显示 所以职位查询条件将内推为true的条件去掉了
        返回这些条件查询应聘记录的交集
        """
        if dep_ids:
            dep_ids = await DepartmentService.get_all_dep_ids(company_id, dep_ids)

        position_ids = position_ids or []
        if position_ids:
            position_ids = [uuid2str(_id) for _id in position_ids]

        ret = []
        # 根据用人部门或者职位ids
        if dep_ids:
            job_positions = await JobPositionSelectService.get_referral_position_by_filter(
                company_id=company_id, dep_ids=dep_ids,
                fields=["id"]
            )
            _ids = [p["id"] for p in job_positions]
            if position_ids:
                _ids = set(_ids) & set(position_ids)
            if not _ids:
                return False, ret
            position_ids = list(_ids)

        candidate_ids = None
        if keyword:  # 搜索候选人
            candidates = await CandidateService.search_candidate(company_id, keyword)
            candidate_ids = [c["id"] for c in candidates]
            if not candidate_ids:
                return False, ret

        # candidate_ids, 候选人状态, 内推人姓名/手机号查询应聘记录信息
        cr_status = status or []
        if cr_status or candidate_ids or referee or position_ids:
            candidate_records = await CandidateRecordService.get_candidate_record_by_referee(
                company_id=company_id, status=cr_status, candidate_ids=candidate_ids, referee=referee,
                job_position_ids=position_ids,
                fields=["id"]
            )
            cr_ids = [c["id"] for c in candidate_records]
            if not cr_ids:
                return False, ret
            ret = cr_ids
        return True, ret

    @ classmethod
    async def _format_comment(
            cls, source: int, company_id: str = None, user_id: str = None,
            referee_name: str = "", referee_mobile: str = "", page_id: str = None,
            reason: str = "") -> str:
        """
        组合 操作 comment 文案
        :param source:
        :param company_id:
        :param user_id:
        :param referee_name: 内推人
        :param referee_mobile: 内推人手机
        :param page_id: 招聘网页id
        :param reason: 内推原因
        :return:
        """

        # 创建操作记录
        if source == CandidateRecordSource.EMP_RECOMMENDATION:
            if referee_mobile:
                comment = f"{referee_name}（{referee_mobile}）推荐了候选人，推荐理由：{reason}"
            else:
                comment = f"{referee_name} 推荐了候选人，推荐理由：{reason}"

        elif source == CandidateRecordSource.WX_RECRUITMENT:
            _page = await RecruitmentPageRecord.get_one_page(
                company_id, page_id, fields=["name"]
            ) or {}
            comment = f"候选人投递了简历, 来源招聘网页: {_page.get('name')}"

        elif source == CandidateRecordSource.SELF_RECOMMENDATION:
            if referee_mobile:
                comment = f"候选人投递了简历，内推人：{referee_name}({referee_mobile})"
            else:
                comment = f"候选人投递了简历，内推人：{referee_name})"

        elif source == CandidateRecordSource.HR:
            user = await s_ucenter.get_user(user_id) or {}
            comment = f"{user.get('nickname')} 添加了候选人"
        else:
            raise APIValidationError(msg="生成comment失败，source类型错误")

        return comment

    @classmethod
    def _format_dep_name_last(cls, data: dict) -> dict:
        """
        将部门名称只留最后一级
        """
        dep_name = data.get("dep_name")
        if dep_name:
            data["dep_name"] = str(dep_name).rsplit('/', 1)[-1]
        return data

    @classmethod
    async def get_delivery_record_stat(cls, company_id: str) -> dict:
        """投递记录统计"""
        ret = {
            "view_count": 0,  # 本月招聘门户访问量
            "yesterday_view_count": 0,  # 昨天访问量
            "delivery_count": 0,  # 本月投递简历数
            "yesterday_delivery_count": 0,  # 昨天投递简历数
        }
        month_start, month_end = cls._get_month_start_and_end()
        yes_start, yes_end = cls._get_yesterday_start_and_end()

        # 招聘门户访问量 BigDataService
        _share_id = await cls._get_company_share_id(company_id)

        # 投递记录
        view_count, y_view_count, month_delivery, yes_delivery = await asyncio.gather(
            BigDataService.get_portals_pv_current_month(_share_id),
            BigDataService.get_portals_pv_yesterday(_share_id),
            DeliveryRecordService.delivery_record_stat(company_id, start_dt=month_start, end_dt=month_end),
            DeliveryRecordService.delivery_record_stat(company_id, start_dt=yes_start, end_dt=yes_end)
        )
        ret["view_count"] = view_count
        ret["yesterday_view_count"] = y_view_count
        ret["delivery_count"] = sum(month_delivery.values())
        ret["yesterday_delivery_count"] = sum(yes_delivery.values())
        return ret

    @classmethod
    async def get_delivery_record_stat_emp(cls, company_id: str, emp_id: str = None) -> dict:
        """员工端 投递记录统计"""
        ret = {
            "view_count": 0,    # 本月招聘门户访问量
            "yesterday_view_count": 0,  # 昨天访问量
            "delivery_count": 0,    # 本月投递简历数
            "yesterday_delivery_count": 0,  # 昨天投递简历数
            "delivery_total": 0,   # 所有投递记录
        }
        _share_id = await cls._get_company_share_id(company_id)

        # 统计投递记录数量: 本月记录， 昨天记录
        month_start, month_end = cls._get_month_start_and_end()
        yes_start, yes_end = cls._get_yesterday_start_and_end()

        view_count, y_view_count, delivery_map, delivery_yesterday_map, all_records = await asyncio.gather(
            BigDataService.get_portals_employee_pv_current_month(
                company_share_id=_share_id, employee_id=emp_id
            ),
            BigDataService.get_portals_employee_pv_yesterday(
                company_share_id=_share_id, employee_id=emp_id
            ),
            DeliveryRecordService.delivery_record_stat(
                company_id, emp_id, start_dt=month_start, end_dt=month_end
            ),
            DeliveryRecordService.delivery_record_stat(
                company_id, emp_id, start_dt=yes_start, end_dt=yes_end
            ),
            DeliveryRecordService.count_delivery_records_by_emp(company_id, emp_id=emp_id)
        )
        # 招聘门户访问量统计
        ret["view_count"] = view_count
        ret["yesterday_view_count"] = y_view_count
        # 投递简历统计
        ret["delivery_count"] = sum(delivery_map.values())
        ret["yesterday_delivery_count"] = sum(delivery_yesterday_map.values())
        ret["delivery_total"] = all_records
        return ret

    @classmethod
    async def _get_company_share_id(cls, company_id: str) -> str:
        company = await s_ucenter.get_company_for_id(company_id)
        return uuid2str(company.get("share_id")) or None

    @classmethod
    def _get_month_start_and_end(cls) -> tuple:
        _now = datetime.datetime.now()
        return get_date_min_datetime(_now.date().replace(day=1)), str(_now)

    @classmethod
    def _get_yesterday_start_and_end(cls) -> tuple:
        _yesterday = datetime.datetime.today() + datetime.timedelta(-1)
        return get_date_min_datetime(_yesterday), get_date_max_datetime(_yesterday)

    @classmethod
    async def get_delivery_record_stat_info(cls, company_id: str) -> dict:
        """返回推广效果统计数据"""
        month_start, month_end = cls._get_month_start_and_end()
        yes_start, yes_end = cls._get_yesterday_start_and_end()

        # 获取投递统计
        month_delivery, yes_delivery, recruit_pages = await asyncio.gather(
            DeliveryRecordService.delivery_record_stat(company_id, start_dt=month_start, end_dt=month_end),
            DeliveryRecordService.delivery_record_stat(company_id, start_dt=yes_start, end_dt=yes_end),
            RecruitmentPageRecord.get_company_pages(company_id, fields=["id"])
        )
        page_ids = [page["id"] for page in recruit_pages]

        # 获取PV统计 BigDataService
        _share_id = await cls._get_company_share_id(company_id)
        view_count_list, y_view_count_list = await asyncio.gather(
            BigDataService.get_portals_page_pv_current_month(
                company_share_id=_share_id
            ),
            BigDataService.get_portals_page_pv_yesterday(
                company_share_id=_share_id
            )
        )
        view_count_map = {uuid2str(v.get("key")): v for v in view_count_list}
        y_view_count_map = {uuid2str(v.get("key")): v for v in y_view_count_list}

        ret = dict()
        for _id in page_ids:
            ret[_id] = {
                "view_count": view_count_map.get(_id, {}).get("pv", 0),    # 本月招聘门户访问量
                "yesterday_view_count": y_view_count_map.get(_id, {}).get("pv", 0),  # 昨天访问量
                "delivery_count": month_delivery.get(_id, 0),    # 本月投递简历数
                "yesterday_delivery_count": yes_delivery.get(_id, 0),  # 昨天投递简历数
            }
        return ret

    @classmethod
    async def export_referral_record(cls, company_id: str, form_data: dict) -> str:
        """
        导出内推记录excel
        """
        data = await cls.get_referral_records_without_page(
            company_id, form_data,
            fields=["id", "add_dt", "candidate_record_id", "referral_bonus", "is_payed", "recruitment_page_id",
                    "reason", "position_record_id"]
        )
        export = ReferralRecordExport(export_data=data, sheet_name="投递记录")
        _dt = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")
        return await export.get_url(file_name=f"投递记录_{_dt}.xlsx", dead_time=7 * 24 * 3600)

    @classmethod
    async def export_referral_record_for_emp(cls, company_id: str, emp_id: str, form_data: dict) -> str:
        """
        导出内推记录excel
        """
        data = await cls.get_referral_records_without_page(
            company_id, form_data, emp_id=emp_id,
            fields=["id", "add_dt", "candidate_record_id", "referral_bonus", "recruitment_page_id", "reason",
                    "position_record_id"]
        )
        export = EmpReferralRecordExport(export_data=data, sheet_name="内推记录")
        _dt = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")
        return await export.get_url(file_name=f"内推记录_{_dt}.xlsx")

    @classmethod
    async def set_referral_record_payed(cls, company_id: str, user_id: str, record_ids: list, is_payed: bool):
        """设置是否发放奖金"""
        await DeliveryRecordService.update_record_payed(
            company_id, user_id, ids=record_ids, is_payed=is_payed
        )

    @classmethod
    async def set_referral_bonus(cls, company_id: str, user_id: str, ids: list, referral_bonus: str):
        """设置内推奖励"""
        await DeliveryRecordService.update_record_referral_bonus(
            company_id, user_id, ids=ids, referral_bonus=referral_bonus
        )

    @classmethod
    async def delete_delivery_record(cls, company_id: str, user_id: str, candidate_record_ids: list):
        """
        根据应聘记录删除投递记录
        @param company_id:
        @param user_id:
        @param candidate_record_ids:
        @return:
        """
        await DeliveryRecordService.delete_records_by_candidate_records(
            company_id, user_id, candidate_record_ids
        )
