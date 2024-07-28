# coding: utf-8
import sanic

from apps.employee_apis.candidate_record import candidate_record_search_apis
from apps.employee_apis.configs import api as config_apis, recruitment_channel_apis, custom_search_apis, common_apis
from apps.employee_apis.portals import portal_position_apis
from apps.employee_apis.portals import portal_delivery_apis, portal_page_apis, portal_wework_apis
from apps.employee_apis.job_positions import job_position_apis as position_apis


def add_employee_routes(app: sanic.Sanic):
    employee_bp = sanic.Blueprint('employee', url_prefix="/api/employee")

    # 招聘配置相关
    employee_bp.add_route(config_apis.EmpSelectHeaderView.as_view(), "/select_header/")
    employee_bp.add_route(config_apis.EmpEliminatedReasonView.as_view(), "/eliminated_reason/select_list/")
    # 招聘渠道
    employee_bp.add_route(recruitment_channel_apis.EmployeeRecruitmentChannelView.as_view(), "/recruitment_channel/")

    # 招聘门户
    employee_bp.add_route(portal_delivery_apis.EmpReferralRecordView.as_view(), '/referral_record/')
    employee_bp.add_route(portal_delivery_apis.EmpReferralRecordListView.as_view(), '/portals/referral_record/')
    employee_bp.add_route(portal_delivery_apis.EmpReferralRecordExportView.as_view(), '/portals/referral_record/export/')
    employee_bp.add_route(portal_delivery_apis.EmpMyReferralRecordView.as_view(), '/portals/my_records/')
    employee_bp.add_route(portal_delivery_apis.EmpMyReferralStatView.as_view(), '/portals/my_records/stats/')
    employee_bp.add_route(portal_delivery_apis.WeWorkReferralView.as_view(), '/portals/wework/referral/')
    employee_bp.add_route(portal_delivery_apis.EmpWeWorkCandidateCreateView.as_view(), '/portals/wework/add_candidate/')
    employee_bp.add_route(
        portal_delivery_apis.EmpWeWork2HAOHRExternalContactQrCodeView.as_view(), '/portals/wework/2haohr/get_contact_qrcode/'
    )
    employee_bp.add_route(portal_page_apis.EmpPortalPageBasicView.as_view(), '/portals/basic_list/')
    employee_bp.add_route(portal_page_apis.EmpPortalCompanyIntroView.as_view(), '/portals/company_intro/detail/')
    employee_bp.add_route(portal_page_apis.EmpReferralConfigView.as_view(), '/referral_config/')

    # 招聘门户 - 获取外部联系人员工信息
    employee_bp.add_route(
        portal_wework_apis.PortalWeWorkExternalContactView.as_view(), "/referral_portal/wework/get_external_contact/"
    )

    # 内推职位相关
    employee_bp.add_route(portal_position_apis.EmpReferRecordPositionListView.as_view(), '/portals/position_select/')
    employee_bp.add_route(portal_position_apis.EmpPortalPositionListFilterView.as_view(), '/portals/position_filter/')
    employee_bp.add_route(
        portal_position_apis.EmpPortalPositionListView.as_view(), '/portals/referral_position/list/'
    )
    employee_bp.add_route(
        portal_position_apis.EmpPortalPositionSelectListView.as_view(), '/portals/referral_position/select_list/'
    )
    employee_bp.add_route(
        portal_position_apis.EmpPortalPositionDetailView.as_view(), '/portals/referral_position/detail/'
    )
    # 内推人相关
    employee_bp.add_route(
        portal_page_apis.ReferralEmployeeDetailView.as_view(), '/portals/referral_employee/detail/'
    )
    employee_bp.add_route(
        portal_page_apis.ReferralEmployeeUpdateView.as_view(), '/portals/referral_employee/update/'
    )
    employee_bp.add_route(custom_search_apis.CustomSearchView.as_view(), "/custom_search/")

    employee_bp.add_route(
        candidate_record_search_apis.SearchQueryConfigView.as_view(), "/candidate_record/query_config/"
    )
    employee_bp.add_route(candidate_record_search_apis.SearchQueryView.as_view(), "/candidate_record/")

    employee_bp.add_route(common_apis.HasHrView.as_view(), "/common/has_hr/")
    employee_bp.add_route(common_apis.EmpShareShortUrlView.as_view(), "/common/share_short_url/")
    employee_bp.add_route(common_apis.EmpShareMiniQrCode.as_view(), "/common/share_mini_qrcode/")
    employee_bp.add_route(common_apis.HrPermissionView.as_view(), "/common/hr_permission/")
    employee_bp.add_route(common_apis.SmsPlatformGetBalanceView.as_view(), '/common/sms_platform/get_balance/')

    # 招聘职位
    employee_bp.add_route(position_apis.JobPositionTypeView.as_view(), "/job_position/type_tree/")
    employee_bp.add_route(position_apis.EmpHrJobPositionMenuView.as_view(), "/job_position/emp_hr_select_menu/")

    app.blueprint(employee_bp)
