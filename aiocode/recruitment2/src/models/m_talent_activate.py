# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey

from constants import TalentActivateStatus, ActivateNotifyWay
from models import meta

tb_talent_activate_record = sa.Table(
    't_talent_activate_record', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_task_id', sa.String(32), comment='任务ID', key='task_id'),
    sa.Column('c_candidate_id', sa.String(32), comment='候选人ID', key='candidate_id'),
    sa.Column('c_portal_page_id', sa.String(32), comment='门户网页ID', key='portal_page_id'),
    sa.Column('c_page_position_id', sa.String(32), comment='门户职位ID', key='page_position_id'),
    sa.Column('c_sms_template_id', sa.String(32), comment='短信模板ID', key='sms_template_id'),
    sa.Column(
        'c_candidate_record_id', None,
        ForeignKey('models.m_candidate_record.tb_candidate_record.c_id'),
        comment='应聘记录ID', key='candidate_record_id'
    ),
    sa.Column(
        'c_activate_status', sa.Integer, comment='激活状态',
        default=TalentActivateStatus.Null, key='activate_status'
    ),
    sa.Column('c_sms_content', sa.String(256), comment='短信内容', key='sms_content'),
    sa.Column('c_notify_way', sa.Integer, comment='通知方式', default=ActivateNotifyWay.Sms, key='notify_way'),
    sa.Column('c_is_read', sa.Boolean, default=False, comment='是否访问', key='is_read'),
    sa.Column('c_latest_read_dt', sa.DateTime, comment='最新访问时间', key='latest_read_dt'),
    sa.Column('c_send_email_id', sa.String(32), comment='发送邮件ID', key='send_email_id'),
    sa.Column('c_email_template_id', sa.String(32), comment='邮件模板ID', key='email_template_id'),
    sa.Column('c_sms_response', sa.String(512), comment='短信发送结果', key='sms_response'),

    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, default=datetime.now, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column(
        'c_update_dt', sa.DateTime, default=datetime.now,
        onupdate=datetime.now, comment='更新时间', key='update_dt'
    ),
    sa.Column('c_is_delete', sa.Boolean, default=False, comment='是否删除', key='is_delete'),

    sa.Index('idx_com_page_sta', 'company_id', "portal_page_id", "activate_status")
)
