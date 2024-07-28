from __future__ import absolute_import

import sqlalchemy as sa
from sqlalchemy import ForeignKey

from utils.strutils import gen_uuid
from constants import InterviewWay, InvitationStatus
from constants.commons import null_uuid
from models import meta


# 面试表
tb_interview = sa.Table(
    "t_interview", meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment="id", key='id'),
    sa.Column('c_company_id', sa.String(32), comment="企业id", default=null_uuid, key='company_id'),
    sa.Column(
        'c_candidate_record_id', None, ForeignKey('models.m_candidate_record.tb_candidate_record.c_id'), key='candidate_record_id'
    ),
    # sa.Column('c_candidate_record_id', sa.String(32), comment="应聘记录id", default=null_uuid, key='candidate_record_id'),
    sa.Column('c_interview_dt', sa.DateTime, comment="面试时间", key='interview_dt'),
    sa.Column('c_is_notification', sa.Boolean, comment="是否通知"),
    sa.Column('c_interview_information_id', sa.String(32), comment='', key='interview_information_id'),
    sa.Column('c_notify_candidate_email', sa.Boolean, comment='是否邮件通知', default=False, key='notify_candidate_email'),
    sa.Column('c_notify_candidate_sms', sa.Boolean, comment='是否短信通知', default=False, key='notify_candidate_sms'),
    sa.Column('c_notify_participant_email', sa.Boolean, comment='是否邮件通知面试官', default=False, key='notify_participant_email'),
    sa.Column('c_notify_participant_wechat', sa.Boolean, comment='是否微信通知面试官', default=False, key='notify_participant_wechat'),
    sa.Column('c_email_title', sa.String(100), comment='', default='', key='email_title'),
    sa.Column('c_email_content', sa.Text, comment='邮件内容', default='', key='email_content'),
    sa.Column('c_email_attach', sa.Text, comment='邮件附件', default='', key='email_attach'),
    sa.Column('c_email_template_id', sa.String(32), comment='邮件模板id', default=null_uuid, key='email_template_id'),
    sa.Column('c_count', sa.SmallInteger, comment="面试轮次", default=0, key='count'),
    sa.Column('c_is_sign', sa.Boolean, comment="是否签到", default=False, key='is_sign'),
    sa.Column('c_sign_dt', sa.DateTime, comment='签到时间', default=None, key='sign_dt'),
    sa.Column('c_sign_notify_participant', comment='签到是否通知面试官', default=False, key='sign_notify_participant'),
    sa.Column('c_interview_way', sa.SmallInteger, comment='面试方式', default=InterviewWay.face2face_interview, key='interview_way'),
    sa.Column('c_is_send_employment_form', sa.Boolean, comment='是否发送应聘登记表', default=False, key='is_send_employment_form'),
    sa.Column('c_is_group_interview', sa.Boolean, comment='是否群面', default=False, key='is_group_interview'),
    sa.Column('c_group_interview_id', sa.String(32), comment='群面标识符', default=null_uuid, key='group_interview_id'),
    sa.Column('c_invitation_status', sa.SmallInteger, comment='面试邀约状态', default=InvitationStatus.UNKNOWN, key='invitation_status'),
    sa.Column('c_read_invitation', sa.Boolean, comment='是否已阅读面试邀约', default=False, key='read_invitation'),
    sa.Column('c_is_latest', sa.Boolean, comment='是否为应聘记录的最新面试', default=True, key='is_latest'),
    sa.Column('c_add_by_id', sa.String(32), comment="添加人", default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=sa.func.now(), key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', onupdate=sa.func.now(), key='update_by_id'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    # 已存在索引
    sa.Index('idx_basic', 'is_delete', 'company_id'),
    sa.Index('index_candidate_record_id', 'candidate_record_id'),
    sa.Index('idx_crecord_dt', 'candidate_record_id', 'interview_dt')
)


# 面试官关联表
tb_interview_participant_rel = sa.Table(
    "t_interview_participant_rel", meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment="id", key='id'),
    sa.Column('c_company_id', sa.String(32), comment="企业id", default=null_uuid, key='company_id'),
    sa.Column(
        'c_interview_id', None, ForeignKey('models.m_interview.tb_interview.c_id'), key='interview_id'
    ),
    sa.Column(
        'c_candidate_record_id', None, ForeignKey('models.m_candidate_record.tb_candidate_record.c_id'),
        key='candidate_record_id'
    ),
    sa.Column('c_participant_id', sa.String(32), comment="面试官ID", key='participant_id'),
    sa.Column('c_participant_type', sa.Integer, comment="面试官类型（1：主2：其他）", key='participant_type'),
    sa.Column('c_add_by_id', sa.String(32), comment="添加人", default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=sa.func.now(), key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', onupdate=sa.func.now(), key='update_by_id'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
    sa.Column('c_is_comment', sa.Boolean, comment='是否评价', default=False, key='is_comment')
)
