# coding: utf-8
import sanic

from apps.int_apis import EventCallBackView, wework_apis, delivery_record_apis, notify_callback_apis
from apps.int_apis.configs import common_apis
from apps.int_apis import job_position_apis
from apps.int_apis import manage_scope_apis
from apps.int_apis import recruitment_team_apis
from apps.int_apis import recruit_team_apis, candidate_record_apis
from apps.int_apis import portal_page_apis
from apps.int_apis import data_report_apis


def add_intranet_routes(app: sanic.Sanic):
    intranet_bp = sanic.Blueprint('intranet', url_prefix="/intranet")
    intranet_bp.add_route(EventCallBackView.as_view(), "/event_callback/")
    intranet_bp.add_route(wework_apis.ExternalContactView.as_view(), "/wework/external_contact/")
    intranet_bp.add_route(notify_callback_apis.EmailNotifyCallBackView.as_view(), "/email_notify_callback/")

    intranet_bp.add_route(common_apis.EmpIdConvertHrIdView.as_view(), "/configs/common/emp_id_convert_hr_id/")
    intranet_bp.add_route(common_apis.EliminatedReasonView.as_view(), "/configs/eliminate_reason")
    intranet_bp.add_route(common_apis.RecruitmentChannelView.as_view(), "/configs/recruit_channel")

    intranet_bp.add_route(delivery_record_apis.DeleteDeliveryRecordView.as_view(), "/delete_delivery_record/")

    intranet_bp.add_route(job_position_apis.SelectJobPositionView.as_view(), "/job_position/info")
    intranet_bp.add_route(manage_scope_apis.HrManageScopeView.as_view(), "/hr_manage_scope/")
    intranet_bp.add_route(recruitment_team_apis.RecruitmentTeamView.as_view(), "/recruitment_team/")

    intranet_bp.add_route(recruit_team_apis.ParticipantView.as_view(), "/recruit_team/participants")
    intranet_bp.add_route(candidate_record_apis.CheckHasAllowJoinTalentView.as_view(),
                          "/candidate_record/check_has_allow_join_talent/")

    intranet_bp.add_route(portal_page_apis.PortalPageView.as_view(), "/portals/")

    intranet_bp.add_route(data_report_apis.FieldConvertView.as_view(), "/data_report/field_covert/")

    app.blueprint(intranet_bp)
