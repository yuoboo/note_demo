from business.commons.data_report.b_data_report import DataReportBase
from business.commons.data_report import b_job_position
from business.commons.data_report import b_candidate_record
from business.commons.data_report import b_common


class DataReportBiz:
    base = DataReportBase()
    add_job_position = b_job_position.AddJobPositionReportBiz()
    update_job_position = b_job_position.UpdateJobPositionReportBiz()

    add_candidate_record = b_candidate_record.AddCandidateRecordReportBiz()

    common = b_common.CommonBusiness()


if __name__ == "__main__":
    import asyncio

    async def run():
        await DataReportBiz.update_job_position.send_data(
            company_id="f79b05ee3cc94514a2f62f5cd6aa8b6e",
            ev_ids=["0f582ea7f9274fe49b0bccd335eb2712"]
        )
    asyncio.run(run())

