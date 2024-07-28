from business.commons.data_report import DataReportBase
from constants import CandidateRecordStatus, ParticipantType
from constants.commons import RECORD_STATUS_ROUTES
from services import svc
from utils.strutils import uuid2str
from utils.timeutils import to_string


def _check_work_mark(origin_status, target_status, status):
    """
    是否筛选简历判断
    @param origin_status:
    @param target_status:
    @param status:
    @return:
    """
    work_mark = 0
    if all(
            [
                origin_status in [CandidateRecordStatus.FORM_CREATE, CandidateRecordStatus.PRIMARY_STEP1],
                status == target_status,
                target_status in [CandidateRecordStatus.PRIMARY_STEP2, CandidateRecordStatus.PRIMARY_STEP3]
            ]
    ):
        work_mark = 1

    return work_mark


class AddCandidateRecordReportBiz(DataReportBase):
    """
    添加应聘记录
    ev_data:
    [{
      "job_position_id": "", // 招聘需求ID
      "user_type": 0, // 操作人身份  (1:HR用户 2：员工)"
      "add_by_id":"",  // 操作人ID
      "candidate_record_id":"",  // 应聘记录ID
      "candidate_id":"",  //  应聘者id
      "add_dt": 20020202,  //  操作时间
      "referee_id":"", // 推荐人ID
      "status": 0, //30:待初筛 31：初筛通过 32：初选淘汰 40：已安排面试 41：已面试 42：面试通过 43：面试淘汰 50：拟录用 51：已发offer 52：待入职 53：已入职 54：撤销录用
      "channel_id":"", // 招聘渠道ID
      "portal_page_id":"",  //   招聘门户ID
      "candidate_id":"" //   应聘者ID
    }]
    """

    fields_map = {
        "id": "candidate_record_id",
        "job_position_id": "job_position_id",
        "user_type": "user_type",
        "candidate_id": "candidate_id",
        "referee_id": "referee_id",
        "status": "status",
        "recruitment_channel_id": "channel_id",
        "recruitment_page_id": "portal_page_id",
        "add_by_id": "add_by_id",
        "add_dt": "add_dt",
        "status_records": "status_records",
        "work_mark": "work_mark"
    }

    filter_fields = True
    ev_code = 'RE00200'

    async def get_ev_data(self, company_id, ids, **kwargs):
        fields = [
            "job_position_id", "add_by_id", "id", "candidate_id", "add_dt", "status",
            "recruitment_channel_id", "referee_id", "recruitment_page_id"
        ]
        data = []
        user_type = kwargs.get("user_type") or ParticipantType.NONE
        queryset = await svc.candidate_record.get_candidate_records_by_ids(company_id, ids, fields=fields)
        for item in queryset:
            item.update(
                {
                    "user_type": user_type,
                }
            )
            data.append(item)

        return data

    async def prepare_data(self, company_id, ev_data, **kwargs):
        """

        @param company_id:
        @type ev_data: list
        @param kwargs:
        @return:
        """
        if not ev_data:
            raise Exception("参数缺失")
        data = []
        for item in ev_data:
            status_routes = RECORD_STATUS_ROUTES.get(item.get("status"))
            item["status_records"] = [{"status": status} for status in status_routes]
            item["work_mark"] = _check_work_mark(CandidateRecordStatus.PRIMARY_STEP1, item.get("status"), item["status"])
            data.append(item)

        return data

    async def handle_row(self, company_id, row):

        dt_fmt = "%Y-%m-%d %H:%M:%S"
        row["id"] = uuid2str(row.get("id"))
        row["job_position_id"] = uuid2str(row.get("job_position_id"))
        row["candidate_id"] = uuid2str(row.get("candidate_id"))
        row["add_by_id"] = uuid2str(row.get("add_by_id"))
        row["recruitment_channel_id"] = uuid2str(row.get("recruitment_channel_id")) or ""
        row["referee_id"] = uuid2str(row.get("referee_id")) or ""
        row["recruitment_page_id"] = uuid2str(row.get("recruitment_page_id")) or ""
        row["add_dt"] = to_string(row["add_dt"], dt_fmt) if row.get("add_dt") else ""
        row["status_records"] = row.get("status_records", [])
        row["work_mark"] = row.get("work_mark")

        return row
