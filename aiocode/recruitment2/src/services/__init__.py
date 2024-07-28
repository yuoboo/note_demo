# coding: utf-8
from __future__ import absolute_import

from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordService
from services.s_dbs.candidate_records.s_comment_record import CommentRecordService
from services.s_dbs.config.s_recruitment_team import RecruitmentTeamService
from services.s_dbs.config.s_email_template import EmailTemplateService
from services.s_dbs.portals.s_portal_page import PortalPageService
from services.s_dbs.portals.s_portal_page import PortalPositionsService
from services.s_dbs.portals.s_portal_page import PortalPageService
from services.s_dbs.portals.s_portal_page import ReferralEmployeeService
from services.s_dbs.s_candidate import CandidateService
from services.s_dbs.s_company_introduction import CompanyIntroService
from services.s_dbs.s_job_position import JobPositionSelectService
from services.s_dbs.s_job_position import JobPositionTypeService
from services.s_dbs.s_mange_scope import ManageScopeService, PermissionCodeService
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService
from services.s_dbs.talent_activate.s_activate_record import ActivateRecordService

from services.s_https import s_common, s_employee, s_email_notice
from services.s_https import s_ucenter
from services.s_https import s_sms_notice
from services.s_https.s_candidate import CandidateService as HttpCandidateService
from services.s_https.s_data_report import DataReportService
from services.s_https.s_employee import EmployeeService


class Service(object):
    """服务层"""
    http_common = s_common
    http_ucenter = s_ucenter
    http_employee = EmployeeService()
    http_sms = s_sms_notice
    http_email = s_email_notice
    http_candidate = HttpCandidateService()

    portal_page = PortalPageService()
    referral_page = PortalPageService()
    portal_position = PortalPositionsService()
    referral_emp = ReferralEmployeeService()
    job_position_search = JobPositionSelectService()
    job_position_type = JobPositionTypeService()
    manage_scope = ManageScopeService()
    permission = PermissionCodeService()
    activate_record = ActivateRecordService()
    com_intro = CompanyIntroService()
    candidate_comment = CommentRecordService()
    candidate = CandidateService()
    recruit_channel = RecruitmentChannelService()
    candidate_record = CandidateRecordService()
    recruit_team = RecruitmentTeamService()
    email_template = EmailTemplateService()

    data_report = DataReportService()
    recruitment_team = RecruitmentTeamService()


svc = Service()

__all__ = ["svc", ]
