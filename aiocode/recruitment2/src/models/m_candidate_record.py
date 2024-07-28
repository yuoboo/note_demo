# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey

from models import meta


# 应聘记录表
tb_candidate_record = sa.Table(
    't_candidate_record', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_candidate_id', sa.String(32), comment='候选人ID', key='candidate_id'),
    sa.Column(
        'c_job_position_id', None,
        ForeignKey('models.m_job_position.tb_job_position.c_id'),
        comment='职位ID', key='job_position_id'
    ),

    sa.Column(
        'c_recruitment_channel_id', None,
        ForeignKey('models.m_config.tb_recruitment_channel.c_id'),
        comment='招聘渠道ID', key='recruitment_channel_id'
    ),
    sa.Column('c_status', sa.Integer, comment='状态', key='status'),
    sa.Column('c_interview_count', sa.Integer, comment='面试轮次', default=0, key='interview_count'),
    sa.Column('c_eliminated_reason_id', sa.String(32), comment='淘汰原因ID', key='eliminated_reason_id'),
    sa.Column('c_eliminated_by_id', sa.String(32), comment='淘汰人ID', key='eliminated_by_id'),
    sa.Column('c_eliminated_dt', sa.DateTime, comment='淘汰时间', key='eliminated_dt'),
    sa.Column('c_is_notice', sa.Boolean, default=False, comment='淘汰是否通知候选人', key='is_notice'),
    sa.Column('c_source', sa.Integer, comment='记录来源', key='source'),
    sa.Column('c_candidate_form_id', sa.String(32), comment='候选人应聘登记表ID', default=None, key='candidate_form_id'),
    sa.Column('c_employment_form_id', sa.String(32), comment='应聘登记表ID', default=None, key='employment_form_id'),
    sa.Column('c_form_status', sa.Integer, comment='应聘登记表状态', default=1, key='form_status'),
    sa.Column('c_referee_id', sa.String(32), comment='内推人ID', default=None, key='referee_id'),
    sa.Column('c_referee_name', sa.String(100), comment='内推人姓名', default='', key='referee_name'),
    sa.Column('c_referee_mobile', sa.String(100), comment='内推人手机号', default='', key='referee_mobile'),
    sa.Column('c_intention_emp_id', sa.String(32), comment='待入职员工ID', server_default='', key='intention_emp_id'),
    sa.Column('c_employee_id', sa.String(32), comment='员工ID', server_default='', key='employee_id'),
    sa.Column('c_entry_sign_id', sa.String(32), comment='入职登记表ID', server_default='', key='entry_sign_id'),
    sa.Column('c_recruitment_page_id', sa.String(32), comment='招聘网页ID', server_default='', key='recruitment_page_id'),
    sa.Column('c_entry_dt', sa.DateTime, comment='入职时间', key='entry_dt'),

    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, default=datetime.now, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, default=False, comment='是否删除', key='is_delete'),

    sa.Index('idx_job_position', 'company_id', 'job_position_id'),
    sa.Index('idx_basic', 'company_id', 'status'),
    sa.Index('idx_candidate', 'candidate_id')
)


# 关联候选人应聘记录参与者
tb_candidate_record_participant_rel = sa.Table(
    't_candidate_record_participant', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment="id", key="id"),
    sa.Column('c_candidate_record_id', sa.String(32), comment="应聘记录id", key="candidate_record_id"),
    sa.Column('c_participant_id', sa.String(32), comment="参与者id", key="participant_id"),
    sa.Column('c_add_dt', sa.DateTime, comment="添加时间", default=datetime.now, key="add_dt"),
    sa.Column('c_is_delete', sa.Boolean, comment="是否删除", default=False, key="is_delete"),
)


# 应聘记录评论记录
tb_candidate_comment_record = sa.Table(
    't_candidate_comment_record', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_candidate_id', sa.String(32), comment='候选人ID', key='candidate_id'),
    sa.Column('c_candidate_record_id', sa.String(32), comment="应聘记录ID", key='candidate_record_id'),
    sa.Column('c_comment_type', sa.Integer, comment='评论类型', key='comment_type'),
    sa.Column('c_comment', sa.String(3000), comment='评论内容', default="", key='comment'),
    sa.Column('c_operate_type', sa.Integer, comment='操作类型', key='operate_type'),
    sa.Column('c_operate_desc', sa.String(200), comment='操作描述', default="", key='operate_desc'),
    sa.Column('c_user_type', sa.Integer, comment='用户类型(0：未知 1：HR 2:员工)', key='user_type'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人Id', key='add_by_id'),
    sa.Column('c_add_by_name', sa.String(50), comment='添加人姓名', key='add_by_name'),
    sa.Column('c_add_by_avatar', sa.String(200), comment='添加人头像', key='add_by_avatar'),
    sa.Column('c_refer_id', sa.String(32), comment='相关Id', default='', key='refer_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt')
)


# 应聘记录状态变更记录表
t_status_log = sa.Table(
    't_status_log', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_candidate_id', sa.String(32), comment='候选人ID', key='candidate_id'),
    sa.Column('c_candidate_record_id', sa.String(32), comment="应聘记录ID", key='candidate_record_id'),
    sa.Column('c_job_position_id', sa.String(32), comment="应聘记录ID", key='job_position_id'),
    sa.Column('c_status_before', sa.Integer, comment='评论类型', key='status_before'),
    sa.Column('c_status_after', sa.Integer, comment='评论类型', key='status_after'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人Id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt')
)


# 应聘记录转发记录
tb_candidate_record_forwards = sa.Table(
    't_candidate_record_forwards', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_task_id', sa.String(32), comment='批量任务ID', key='task_id'),
    sa.Column('c_candidate_record_id', sa.String(32), comment="应聘记录ID", key='candidate_record_id'),
    sa.Column('c_emp_ids', sa.Text, comment="转发面试官IDs", key='emp_ids'),
    sa.Column('c_log_desc', sa.String(200), comment="日志详情", key='log_desc'),
    sa.Column('c_comment', sa.String(3000), comment="评论内容", key='comment'),
    sa.Column('c_add_position_participant', sa.Boolean, comment="是否将面试官添加到职位的面试官", key='add_position_participant'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
    sa.Column('c_is_latest', sa.Boolean, comment='是否最新转发', key='is_latest'),
)
