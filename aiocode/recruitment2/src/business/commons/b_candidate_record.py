import asyncio
import datetime
import aiotask_context

from constants import CandidateRecordSource, CandidateRecordStatus
from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordCreateService, CandidateRecordService
from services.s_dbs.s_status_log import CandidateStatusLog
from services.s_es.s_candidate_record_es import CandidateRecordESService
from utils.logger import app_logger
from utils.strutils import uuid2str, gen_uuid
from business.commons.b_bi import bi_biz

__all__ = ["CandidateRecordCommon"]


class CandidateRecordCommon:
    @staticmethod
    async def _after_create_candidate_record(company_id: str, candidate_record_ids: list):
        # todo 发送事件到事件分发平台, 清除缓存 ...

        # 同步ES
        try:
            candidate_records = await CandidateRecordService.get_candidate_records_by_ids(
                company_id=company_id, candidate_record_ids=candidate_record_ids)
            if len(candidate_records) == 1:
                await CandidateRecordESService.save_candidate_record(candidate_records[0])
        except Exception as e:
            app_logger.error(f"同步ES失败:{e}")

        # 上传数据到BI
        await bi_biz.send_candidate_record_to_bi(company_id, candidate_record_ids)

    async def create_candidate_record(
            self, company_id: str, user_id: str,
            candidate_id: str,
            job_position_id: str,
            status: int = CandidateRecordStatus.PRIMARY_STEP1,
            candidate_record_id: str = None,
            recruitment_channel_id: str = None,
            source=CandidateRecordSource.HR,
            referee_id: str = None,
            referee_name: str = None,
            referee_mobile: str = None,
            recruitment_page_id: str = ""
    ):
        """
        创建候选人应聘记录
        :param company_id:
        :param user_id:
        :param candidate_id:
        :param candidate_record_id:
        :param job_position_id:
        :param recruitment_channel_id:
        :param status:
        :param source: 创建来源
        :param referee_id: 内推人id
        :param referee_name: 内推人姓名
        :param referee_mobile: 内推人手机
        :param recruitment_page_id:
        """
        interview_count = 0
        if status in [
            CandidateRecordStatus.INTERVIEW_STEP1, CandidateRecordStatus.INTERVIEW_STEP2,
            CandidateRecordStatus.INTERVIEW_STEP3, CandidateRecordStatus.INTERVIEW_STEP4
        ]:
            interview_count = 1
        eliminated_dt = None
        eliminated_by_id = None
        if status in [
            CandidateRecordStatus.PRIMARY_STEP3,
            CandidateRecordStatus.INTERVIEW_STEP4,
            CandidateRecordStatus.EMPLOY_STEP5
        ]:
            eliminated_dt = datetime.datetime.now()
            eliminated_by_id = uuid2str(user_id)

        candidate_record_id = candidate_record_id or gen_uuid()
        create_values = {
            "id": candidate_record_id,
            "status": status,
            "recruitment_channel_id": recruitment_channel_id,
            "source": source,
            "interview_count": interview_count,
            "referee_id": referee_id,
            "referee_name": referee_name,
            "referee_mobile": referee_mobile,
            "eliminated_by_id": eliminated_by_id,
            "eliminated_dt": eliminated_dt,
            "recruitment_page_id": uuid2str(recruitment_page_id) or ''
        }

        await asyncio.gather(
            # 创建应聘记录
            CandidateRecordCreateService.create_obj(
                company_id, user_id, candidate_id, job_position_id, **create_values
            ),
            # 记录统计用的日志
            CandidateStatusLog.create_status_log(
                company_id, user_id, candidate_id, candidate_record_id, job_position_id, 0, status
            )
        )

        _app = aiotask_context.get("app")
        _app.add_task(
            self._after_create_candidate_record(company_id, [candidate_record_id])
        )
