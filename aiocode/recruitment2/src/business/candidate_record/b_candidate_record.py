from constants import CandidateRecordStatus
from services import svc


class CandidateRecordBusiness:
    @classmethod
    async def check_has_allow_join_talent(cls, company_id: str, candidate_ids: list):
        """
        通过候选人id，判断当前候选人是否可以加入人才库
        :param company_id: 企业id
        :param candidate_ids: 候选人id列表
        :return:
        """
        records = await svc.candidate_record.get_candidate_record_by_referee(
            company_id, status=[
                CandidateRecordStatus.PRIMARY_STEP1,
                CandidateRecordStatus.PRIMARY_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP3,
                CandidateRecordStatus.EMPLOY_STEP1,
                CandidateRecordStatus.EMPLOY_STEP2,
                CandidateRecordStatus.EMPLOY_STEP3,
                CandidateRecordStatus.EMPLOY_STEP4,
            ], candidate_ids=candidate_ids
        )
        results = {}
        for record in records:
            candidate_id = record.get('candidate_id')
            if candidate_id not in results:
                results[candidate_id] = {}
                results[candidate_id]['candidate_record_id'] = record.get('id')
                results[candidate_id]['text'] = '/'

            if record.get('status') == CandidateRecordStatus.EMPLOY_STEP4:
                if '已入职' not in results[candidate_id]['text']:
                    results[candidate_id]['text'] = results[candidate_id]['text'] + '已入职'
            else:
                if '已在应聘中' not in results[candidate_id]['text']:
                    results[candidate_id]['text'] = '已在应聘中' + results[candidate_id]['text']

        for key, value in results.items():
            v = results[key]['text']
            if v == '/':
                results[key]['text'] = ''
            elif v.startswith('/'):
                results[key]['text'] = v[1:]
            elif v.endswith('/'):
                results[key]['text'] = v[:-1]

        return results
