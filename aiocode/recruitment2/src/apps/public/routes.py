# coding: utf-8
import sanic

from apps.public import interview_api, portal_page_api, talent_activate_apis
from apps.public.configs import common_apis


def add_public_routes(app: sanic.Sanic):
    public_bp = sanic.Blueprint('public', url_prefix="/api/public")
    # 招聘配置相关
    public_bp.add_route(interview_api.WechatUserMobileVerificationApi.as_view(), "/wx/mobile_verification/")
    public_bp.add_route(interview_api.WeChatSignConfigApi.as_view(), "/wx/interview_sign_config/")

    # 招聘门户 投递
    public_bp.add_route(portal_page_api.CandidatePortalPageView.as_view(), "/wx_recruitment/")
    public_bp.add_route(portal_page_api.PortalPositionQrCodeView.as_view(), "/portals/position_qrcode/")
    public_bp.add_route(portal_page_api.ReferralEmployeeDetailView.as_view(), "/portals/referral_employee/detail/")
    public_bp.add_route(portal_page_api.RecruitmentPageDetailView.as_view(), "/portals/company_intro/detail/")

    # 微信招聘
    public_bp.add_route(portal_page_api.PortalPositionFilterView.as_view(), "/portals/position_filter/")
    # 人才激活
    public_bp.add_route(talent_activate_apis.ActivateLinkReadView.as_view(), "/activate_link_view/")

    # 通用
    public_bp.add_route(common_apis.ShareShortUrlView.as_view(), "/common/share_short_url/")
    public_bp.add_route(common_apis.ShareMiniQrCode.as_view(), "/common/share_mini_qrcode/")
    app.blueprint(public_bp)
