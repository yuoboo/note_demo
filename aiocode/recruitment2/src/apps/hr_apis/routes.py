# coding: utf-8
import sanic

from apps.hr_apis.candidate_record import candidate_record_search_apis, candidate_record_apis
from apps.hr_apis.job_position import job_position_apis
from apps.hr_apis.configs import select_header_apis, recruitment_channel_apis, email_template_apis, \
    eliminated_reason_apis, interview_contact_info_apis, company_introduction_apis, company_request_apis, \
    custom_search_apis, common_apis
from apps.hr_apis.talent_activate import activate_condition_apis, activate_record_apis

from apps.hr_apis.workbench import last_position_apis, recruitment_flow_apis
from apps.hr_apis import Ping, IpView, Redis02Test, Redis01Test
from apps.hr_apis.statistical_analysis import recruit_progress_apis, recruit_transfer_apis, eliminated_stats_apis, \
    workload_stats_apis
from apps.hr_apis.portals import post_manage_apis, referral_config_apis, portal_wework_apis


def add_api_routes(app: sanic.Sanic):
    api_bp = sanic.Blueprint('api', url_prefix='/api')

    # ping
    api_bp.add_route(Ping.as_view(), "/ping/")
    api_bp.add_route(IpView.as_view(), "/ip/")
    api_bp.add_route(Redis01Test.as_view(), "/dept_redis/")
    api_bp.add_route(Redis02Test.as_view(), "/dept_http/")

    # 招聘工作台
    api_bp.add_route(recruitment_flow_apis.RecruitmentTrendsView.as_view(), "/workbench/position_total/"),
    api_bp.add_route(recruitment_flow_apis.RecruitmentFlowView.as_view(), "/workbench/flow/"),
    api_bp.add_route(last_position_apis.LastJobPositionView.as_view(), "/workbench/last_position/"),
    api_bp.add_route(last_position_apis.PositionTodayAdd.as_view(), "/workbench/position_add/"),

    # 招聘配置相关
    api_bp.add_route(select_header_apis.SelectHeaderView.as_view(), "/hr_select_header/")
    api_bp.add_route(interview_contact_info_apis.InterviewContactInfo.as_view(), "/interview_contact_info/")
    api_bp.add_route(interview_contact_info_apis.InterviewContactInfo.as_view(), "/interview_contact_info/<pk>/")
    api_bp.add_route(
        interview_contact_info_apis.InterviewContactInfoSortApi.as_view(), "/interview_contact_information_sort/"
    )

    api_bp.add_route(eliminated_reason_apis.EliminatedReasonApi.as_view(), "/eliminated_reason/")
    api_bp.add_route(eliminated_reason_apis.EliminatedReasonSortApi.as_view(), "/eliminated_reason_sort/")
    api_bp.add_route(eliminated_reason_apis.EliminatedReasonSelectListApi.as_view(), "/eliminated_reason/select_list/")
    api_bp.add_route(eliminated_reason_apis.EliminatedReasonStepConfigApi.as_view(), "/eliminated_reason/step_config/")

    api_bp.add_route(custom_search_apis.CustomSearchView.as_view(), "/custom_search/")

    # 招聘渠道
    api_bp.add_route(recruitment_channel_apis.RecruitmentChannelView.as_view(), "/recruitment_channel/")
    api_bp.add_route(recruitment_channel_apis.RecruitmentChannelStatusView.as_view(), "/recruitment_channel_status/")

    api_bp.add_route(email_template_apis.EmailTemplateView.as_view(), "/config/email_template/")
    api_bp.add_route(email_template_apis.OfferEmailTemplateView.as_view(), "/offers/email_template/")

    # 企业介绍
    api_bp.add_route(
        company_introduction_apis.CompanyIntroductionListView.as_view(), "/company_introduction/list/"
    )
    api_bp.add_route(
        company_introduction_apis.CompanyIntroductionCreateView.as_view(), "/company_introduction/create/"
    )
    api_bp.add_route(
        company_introduction_apis.CompanyIntroductionUpdateView.as_view(), "/company_introduction/update/"
    )
    api_bp.add_route(
        company_introduction_apis.UpdateIntroductionQrCodeView.as_view(), "/company_introduction/update_qrcode/"
    )
    api_bp.add_route(
        company_introduction_apis.CompanyIntroductionDeleteView.as_view(), "/company_introduction/delete/"
    )
    api_bp.add_route(
        company_introduction_apis.CompanyIntroductionSortView.as_view(), "/company_introduction/re_sort/"
    )

    # 招聘门户 - 内推网页
    api_bp.add_route(referral_config_apis.ReferralConfigView.as_view(), "/referral_config/")
    # 招聘门户 - 投递管理
    api_bp.add_route(post_manage_apis.ReferralRecordListView.as_view(), "/referral_records/list/")
    api_bp.add_route(post_manage_apis.PortalRecordStatisticsView.as_view(), "/referral_stats/")
    api_bp.add_route(post_manage_apis.ReferralRecordExportView.as_view(), "/referral_records/export/")
    api_bp.add_route(post_manage_apis.ReferralRecordSetPayView.as_view(), "/portals/set_payed/")
    api_bp.add_route(post_manage_apis.DeliveryRecordSetBonusView.as_view(), "/portals/set_bonus/")
    api_bp.add_route(post_manage_apis.PortalPostPositionListView.as_view(), "/portals/position_select/")
    api_bp.add_route(post_manage_apis.PortalRecordPromotionStatView.as_view(), "/portals/promotion_stat/")

    # 招聘门户 - 企业微信获取有"客户联系功能"权限的HR列表
    api_bp.add_route(portal_wework_apis.PortalWeWorkGetHrListView.as_view(), "/referral_portal/wework/get_hr_list/")
    # 招聘门户 - 获取外部联系人员工信息
    api_bp.add_route(
        portal_wework_apis.PortalWeWorkExternalContactView.as_view(), "/referral_portal/wework/get_external_contact/"
    )

    # 招聘开通
    api_bp.add_route(company_request_apis.CompanyRequestView.as_view(), "/company_request/")

    # 招聘职位
    api_bp.add_route(job_position_apis.JobPositionCityListView.as_view(), "/job_position/city_list/")
    api_bp.add_route(job_position_apis.JobPositionDepartmentTreeView.as_view(), "/job_position/dep_tree/")
    api_bp.add_route(job_position_apis.JobPositionTypeTreeView.as_view(), "/job_position/type_tree/")
    api_bp.add_route(
        job_position_apis.ReferralJobPositionView.as_view(), "/job_position/referral_portal/"
    )
    api_bp.add_route(job_position_apis.JobPositionSetReferralBonusView.as_view(), "/job_position/set_referral_bonus/")

    # 人才库激活
    api_bp.add_route(activate_condition_apis.VerifyCandidatesView.as_view(), "/talent_activate/verify_candidates/")
    api_bp.add_route(activate_condition_apis.VerifyCandidateView.as_view(), "/talent_activate/verify_candidate/")
    api_bp.add_route(activate_record_apis.ActivateRecordView.as_view(), "/talent_activate_record/")
    api_bp.add_route(activate_record_apis.TryActivateView.as_view(), "/talent_activate_try/")
    api_bp.add_route(activate_record_apis.ActivateRecordListView.as_view(), "/talent_activate/record_list/")
    api_bp.add_route(activate_record_apis.ActivateRecordPortalListView.as_view(), "/talent_activate_record/portal_list/")
    api_bp.add_route(activate_record_apis.CandidateActivateCountView.as_view(), "/talent_activate/activate_count/")

    # 统计分析
    api_bp.add_route(recruit_progress_apis.RecruitProgressView.as_view(), "/stats/recruit_progress/")
    api_bp.add_route(recruit_progress_apis.RecruitProgressSheetView.as_view(), "/stats/recruit_progress/sheet/")
    api_bp.add_route(recruit_transfer_apis.CandidateTransferView.as_view(), "/stats/candidate_transfer/")
    api_bp.add_route(recruit_transfer_apis.CandidateTransferSheetView.as_view(), "/stats/candidate_transfer/sheet/")
    api_bp.add_route(recruit_transfer_apis.ChannelTransferStatsView.as_view(), "/stats/channel_transfer/")
    api_bp.add_route(eliminated_stats_apis.EliminatedReasonStatsView.as_view(), "/stats/eliminated_reason/")
    api_bp.add_route(eliminated_stats_apis.EliminatedReasonStatsSheetView.as_view(), "/stats/eliminated_reason/sheet/")
    api_bp.add_route(workload_stats_apis.PositionWorkLoadView.as_view(), "/stats/position_workload/")
    api_bp.add_route(workload_stats_apis.DepartmentWorkLoadView.as_view(), "/stats/department_workload/")
    api_bp.add_route(workload_stats_apis.RecruitHRWorkLoadView.as_view(), "/stats/hr_workload/")
    api_bp.add_route(workload_stats_apis.RecruitEmpWorkLoadView.as_view(), "/stats/emp_workload/")

    # 统计分析导出
    api_bp.add_route(recruit_progress_apis.RecruitProgressExportView.as_view(), "/stats/recruitment_progress/export/")
    api_bp.add_route(recruit_transfer_apis.CandidateTransferExportView.as_view(), "/stats/candidate_transfer/export/")
    api_bp.add_route(recruit_transfer_apis.ChannelTransferExportView.as_view(), "/stats/channel_transfer/export/")
    api_bp.add_route(eliminated_stats_apis.EliminatedReasonStatsExportView.as_view(), "/stats/eliminated_reason/export/")
    api_bp.add_route(workload_stats_apis.PositionWorkLoadExportView.as_view(), "/stats/position_workload/export/")
    api_bp.add_route(workload_stats_apis.RecruitmentTeamWorkLoadExportView.as_view(), "/stats/team_workload/export/")

    # 应聘流程相关
    api_bp.add_route(candidate_record_search_apis.SearchQueryConfigView.as_view(), "/candidate_record/query_config/")
    api_bp.add_route(candidate_record_search_apis.SearchQueryView.as_view(), "/candidate_record/")
    api_bp.add_route(candidate_record_apis.CheckHasAllowJoinTalentView.as_view(),
                     "/candidate_record/check_has_allow_join_talent/")

    # 通用接口
    api_bp.add_route(common_apis.ShareShortUrlView.as_view(), "/common/share_short_url/")
    api_bp.add_route(common_apis.ShareMiniQrCode.as_view(), "/common/share_mini_qrcode/")
    api_bp.add_route(common_apis.SensitiveView.as_view(), "/common/sensitive/")
    api_bp.add_route(common_apis.MyQrCodeView.as_view(), "/common/get_my_qrcode/")

    app.blueprint(api_bp)
