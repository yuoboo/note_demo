# coding: utf-8
from constants import CommentType, OperateType, ParticipantType
from constants.commons import null_uuid
from drivers.mysql import db
from models.m_candidate_record import tb_candidate_comment_record
from services.s_https.s_ucenter import get_user
from utils.sa_db import db_executor
from utils.strutils import gen_uuid, uuid2str


class CommentRecordService(object):
    """
    评论记录服务类
    """

    @classmethod
    async def _ge_user_info(cls, company_id, user_id, user_type):
        """
        获取用户信息
        :param user_id:
        :param user_type:
        :return:
        """
        if user_type == ParticipantType.HR:
            user = await get_user(user_id)
            name, avatar = user.get("nickname"), ""
        else:
            name, avatar = "", ""
        return name, avatar

    @classmethod
    def _get_operate_desc(cls, operate_type):
        """
        获取操作描述
        :param operate_type:
        :return:
        """

        return ""

    @classmethod
    async def create_comment(
            cls, company_id, candidate_id, comment,
            candidate_record_id=null_uuid,
            add_by_id=null_uuid,
            user_type=ParticipantType.NONE,
            comment_type=CommentType.OTHER_TYPE,
            need_name=False,
            operate_type=OperateType.OPERATE_NONE,
            refer_id=null_uuid,
    ):
        """
        创建评论
        :param company_id:
        :param candidate_id:
        :param comment:
        :param candidate_record_id:
        :param add_by_id:
        :param user_type:
        :param comment_type:
        :param need_name: 是否需要拼接操作人姓名
        :param operate_type: 操作类型
        :param refer_id: 操作类型
        :return:
        """
        name, avatar = '', ''
        if comment_type == CommentType.DISCUSS_TYPE or need_name:
            name, avatar = await cls._ge_user_info(company_id, add_by_id, user_type)
        comment = "{}{}".format(name, comment) if need_name else comment
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                tb_candidate_comment_record.insert().values(
                    id=gen_uuid(),
                    company_id=uuid2str(company_id),
                    candidate_id=uuid2str(candidate_id),
                    comment_type=comment_type,
                    comment=comment,
                    candidate_record_id=uuid2str(candidate_record_id),
                    add_by_id=uuid2str(add_by_id),
                    user_type=user_type,
                    operate_type=operate_type,
                    operate_desc=cls._get_operate_desc(operate_type),
                    add_by_name=name if comment_type == CommentType.DISCUSS_TYPE else "",
                    add_by_avatar=avatar if comment_type == CommentType.DISCUSS_TYPE else "",
                    refer_id=uuid2str(refer_id)
                )
            )

    @classmethod
    async def batch_create_candidate_comment(
            cls, company_id, candidate_ids, comment,
            add_by_id=null_uuid,
            user_type=ParticipantType.NONE,
            comment_type=CommentType.OTHER_TYPE,
            need_name=False,
            operate_type=OperateType.OPERATE_NONE,
            refer_id=null_uuid,
    ):
        """
        批量给候选人添加评论
        :param company_id:
        :param candidate_ids:
        :param comment:
        :param add_by_id:
        :param user_type:
        :param comment_type:
        :param need_name: 是否需要拼接操作人姓名
        :param operate_type: 操作类型
        :param refer_id: 操作类型
        :return:
        """
        name, avatar = '', ''
        if comment_type == CommentType.DISCUSS_TYPE or need_name:
            name, avatar = await cls._ge_user_info(company_id, add_by_id, user_type)
        comment = "{}{}".format(name, comment) if need_name else comment
        values = []
        for candidate_id in candidate_ids:
            values.append(
                {
                    "company_id": uuid2str(company_id),
                    "candidate_id": uuid2str(candidate_id),
                    "comment_type": comment_type,
                    "comment": comment,
                    "candidate_record_id": null_uuid,
                    "add_by_id": uuid2str(add_by_id),
                    "user_type": user_type,
                    "operate_type": operate_type,
                    "operate_desc": cls._get_operate_desc(operate_type),
                    "add_by_name": name if comment_type == CommentType.DISCUSS_TYPE else "",
                    "add_by_avatar": avatar if comment_type == CommentType.DISCUSS_TYPE else "",
                    "refer_id": uuid2str(refer_id)

                }
            )
        await db_executor.batch_create(db.default, tb_candidate_comment_record, values)
