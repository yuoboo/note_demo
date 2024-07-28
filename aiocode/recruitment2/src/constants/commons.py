# coding:utf-8
import datetime

from constants import CandidateRecordStatus as CdrStatus

null_uuid = '0' * 32

null_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)


RECORD_STATUS_ROUTES = {
        CdrStatus.PRIMARY_STEP1: [CdrStatus.PRIMARY_STEP1],
        CdrStatus.PRIMARY_STEP2: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2],
        CdrStatus.PRIMARY_STEP3: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP3],
        CdrStatus.INTERVIEW_STEP1: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1],
        CdrStatus.INTERVIEW_STEP2: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2],
        CdrStatus.INTERVIEW_STEP3: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2, CdrStatus.INTERVIEW_STEP3],
        CdrStatus.INTERVIEW_STEP4: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP4],
        CdrStatus.EMPLOY_STEP1: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2, CdrStatus.INTERVIEW_STEP3, CdrStatus.EMPLOY_STEP1],
        CdrStatus.EMPLOY_STEP2: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2, CdrStatus.INTERVIEW_STEP3, CdrStatus.EMPLOY_STEP1, CdrStatus.EMPLOY_STEP2],
        CdrStatus.EMPLOY_STEP3: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2, CdrStatus.INTERVIEW_STEP3, CdrStatus.EMPLOY_STEP1, CdrStatus.EMPLOY_STEP2, CdrStatus.EMPLOY_STEP3],
        CdrStatus.EMPLOY_STEP4: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2, CdrStatus.INTERVIEW_STEP3, CdrStatus.EMPLOY_STEP1, CdrStatus.EMPLOY_STEP2, CdrStatus.EMPLOY_STEP3, CdrStatus.EMPLOY_STEP4],
        CdrStatus.EMPLOY_STEP5: [CdrStatus.PRIMARY_STEP1, CdrStatus.PRIMARY_STEP2, CdrStatus.INTERVIEW_STEP1, CdrStatus.INTERVIEW_STEP2, CdrStatus.INTERVIEW_STEP3, CdrStatus.EMPLOY_STEP1, CdrStatus.EMPLOY_STEP5],
    }
