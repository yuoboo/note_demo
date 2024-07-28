# -*- coding: utf-8 -*-

__all__ = ["biz"]

from business.b_job_position import JobPositionBusiness
from business.commons import DataReportBiz
from business.configs.b_common import CommonBusiness
from business.commons.b_manage_scope import ManageScopeBusiness
from business.configs.b_recruitment_team import RecruitmentTeamBusiness
from business.b_recruit_team import RecruitmentTeamBiz
from business.commons.b_notify_callback import NotifyCallBackBusiness
from business.configs.b_email_template import EmailTemplateBusiness
from business.portals.b_portal_page import PortalPageBusiness, IntranetPortalPageBusiness
from business.portals.b_portal_wework import PortalWeWorkBusiness
from business.portals.b_portal_delivery import RecruitPortalPostManageBiz
from business.b_company_introduction import CompanyIntroductionBusiness
from business.portals.b_referral_config import ReferralConfigBusiness
from business.talent_activate.b_activate_condition import TalentActivateConditionBusiness
from business.talent_activate.b_activate_record import ActivateRecordBusiness
from business.candidate_record.b_candidate_record import CandidateRecordBusiness


class Intranet(object):
    portal_page = IntranetPortalPageBusiness()


class Business(object):
    """业务层"""
    intranet = Intranet()

    config_common = CommonBusiness()
    portal_page = PortalPageBusiness()
    portal_wework = PortalWeWorkBusiness()
    portal_delivery = RecruitPortalPostManageBiz()
    com_intro = CompanyIntroductionBusiness()

    job_position = JobPositionBusiness()    # 招聘职位
    referral_config = ReferralConfigBusiness()
    activate_condition = TalentActivateConditionBusiness()
    activate_record = ActivateRecordBusiness()
    manage_scope = ManageScopeBusiness()
    recruitment_team = RecruitmentTeamBusiness()
    candidate_record = CandidateRecordBusiness()

    recruit_team = RecruitmentTeamBiz()
    email_template = EmailTemplateBusiness()
    notify_callback = NotifyCallBackBusiness()


biz = Business()
