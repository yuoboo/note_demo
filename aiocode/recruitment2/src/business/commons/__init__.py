from .b_candidate_record import CandidateRecordCommon
from business.commons.data_report import DataReportBiz
from .b_sms_platform import SmsPlatformBusiness


__all__ = ["com_biz"]


class CommonBiz(object):
    cr = CandidateRecordCommon()
    sms_platform = SmsPlatformBusiness()
    data_report = DataReportBiz()


com_biz = CommonBiz()

