from constants import EliminatedReasonStep
from services.s_dbs.config.s_eliminated_reason import EliminatedReasonService, eliminated_reason_tbu
from utils.strutils import uuid2str
from kits.exception import APIValidationError

import logging
logger = logging.getLogger("sanic.root")


class EliminatedReasonBusiness(object):

    @classmethod
    async def create_reason(cls, company_id: str, user_id: str, reason_step: int, reason: str
                            ) -> str:
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        is_exist = await EliminatedReasonService.valid_reason_text(company_id, reason, reason_step)

        if is_exist:
            raise APIValidationError(msg=f"{EliminatedReasonStep.attrs_[reason_step]}下已存在此淘汰原因")

        record_id = await EliminatedReasonService.create_eliminated_reason(
            company_id=company_id, user_id=user_id, reason_step=reason_step, reason=reason
        )
        return record_id

    @classmethod
    async def update_reason(cls, company_id: str, user_id: str, record_id: str, reason: str):
        """
        更新淘汰原因
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        record_id = uuid2str(record_id)

        # 查询是否存在
        is_exist = await EliminatedReasonService.query_reason_exist(
            company_id=company_id, pk=record_id
        )
        if not is_exist:
            raise APIValidationError(msg="淘汰原因不存在")

        await EliminatedReasonService.update_eliminated_reason(
            company_id=company_id, user_id=user_id, pk=record_id, reason=reason
        )
        return record_id

    @classmethod
    async def delete_reason(cls, company_id: str, user_id: str, record_id: str):
        """
        删除淘汰原因
        :param company_id:
        :param user_id:
        :param record_id: 淘汰记录id
        """
        company_id = uuid2str(company_id)
        record_id = uuid2str(record_id)

        # 查询原因是否存在
        is_exist = await EliminatedReasonService.query_reason_exist(
            company_id=company_id, pk=record_id
        )
        if not is_exist:
            raise APIValidationError(msg="淘汰原因不存在")

        # todo 这里需要从查询应聘记录是否有在用

        # 删除
        await EliminatedReasonService.delete_eliminated_reason(
            company_id=company_id, user_id=user_id, pk=record_id
        )

    @classmethod
    async def get_list_with_pagination(cls, company_id: str, page: int, limit: int,
                                       reason_step: int) -> list:
        """
        返回淘汰原因列表信息 带分页
        """
        logger.info("[recruitment2 test log] this is eliminated reason log")
        return await EliminatedReasonService.get_eliminated_reasons_with_page(
            company_id=company_id, page=page, limit=limit, reason_step=reason_step
        )

    @classmethod
    async def get_reason_select_list(cls, company_id: str, reason_step: int = None) -> list:
        """
        返回企业所有淘汰原因， 不带分页
        """
        company_id = uuid2str(company_id)

        if reason_step:
            if reason_step not in EliminatedReasonStep.attrs_:
                raise APIValidationError(msg="reason_step 不在淘汰原因可选范围内")

        fields = ["id", "reason", "reason_step", "order_no"]
        return await EliminatedReasonService.get_select_data(
            company_id=company_id, fields=fields, reason_step=reason_step
        )

    @classmethod
    async def sort_reasons(cls, company_id: str, user_id: str, record_ids: list):
        """
        淘汰原因排序
        @:param record_ids： 淘汰原因id列表
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        length = len(record_ids)

        if not record_ids:
            raise APIValidationError(msg="record_ids 参数不能为空")
        elif length != len(set(record_ids)):
            raise APIValidationError(msg="record_ids 参数存在重复id")

        record_ids = [uuid2str(r) for r in record_ids]

        # 判断数据完全存在
        rowcount = await EliminatedReasonService.ge_rowcount_by_ids(
            company_id=company_id, record_ids=record_ids
        )
        if rowcount != length:
            raise APIValidationError(msg="数据不完全存在")

        # 保存顺序
        for index, _id in enumerate(record_ids):
            await EliminatedReasonService.update_reason_sort(
                company_id=company_id, user_id=user_id,
                pk=_id, order_no=index + 1
            )

    @classmethod
    async def get_count_by_reason_step(cls, company_id: str) -> list:
        """
        统计各阶段淘汰原因
        """
        company_id = uuid2str(company_id)

        ret = []
        for step, name in EliminatedReasonStep.attrs_.items():
            ret.append({
                "reason_step": step,
                "step_name": name,
                "total_count": await EliminatedReasonService.get_count_by_reason_step(
                    company_id=company_id, reason_step=step
                )
            })
        return ret


class IntranetEliminateReasonBiz:

    @classmethod
    async def get_reason_info(cls, company_id: str, ids: list, fields: list = None):
        """
        查询指定淘汰原因信息， 返回指定字段
        """
        if fields:
            diff = set(fields) - set(eliminated_reason_tbu.tb_keys)
            if diff:
                raise APIValidationError(msg=f"不支持字段：{diff}")

        reasons = await EliminatedReasonService.get_reasons_by_ids(
            company_id, [uuid2str(_id) for _id in ids], fields=fields
        )

        return reasons
