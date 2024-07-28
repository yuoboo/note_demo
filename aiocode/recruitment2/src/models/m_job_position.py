# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey

from models import meta


# 招聘职位表
tb_job_position = sa.Table(
    't_job_position', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    # sa.Column('c_name', sa.String(100), nullable=False, key='name', comment="职位名称"),
    sa.Column('c_work_type', sa.Integer, comment='工作性质', key='work_type'),
    sa.Column('c_position', sa.String(128), comment='职位名', key='name'),
    sa.Column('c_status', sa.Integer, comment='状态', key='status'),
    sa.Column('c_dep_id', sa.String(32), comment='部门ID', key='dep_id'),
    sa.Column('c_dep_name', sa.String(1024), comment='部门名称', key='dep_name'),
    sa.Column('c_position_total', sa.Integer, comment='招聘人数', key='position_total'),
    sa.Column('c_salary_min', sa.Integer, comment='薪资范围(小)', key='salary_min'),
    sa.Column('c_salary_max', sa.Integer, comment='薪资范围(大)', key='salary_max'),
    sa.Column('c_salary_unit', sa.Integer, comment="薪资单位", key="salary_unit"),
    sa.Column('c_job_position_type_id', sa.String(32), comment='职位类型ID', key='job_position_type_id'),
    sa.Column('c_province_id', sa.Integer, comment='省份', key='province_id'),
    sa.Column('c_province_name', sa.String(20), comment='省份', key='province_name'),
    sa.Column('c_city_id', sa.Integer, comment='城市', key='city_id'),
    sa.Column('c_city_name', sa.String(20), comment='城市', key='city_name'),
    sa.Column('c_town_id', sa.Integer, comment='区县', key='town_id'),
    sa.Column('c_town_name', sa.String(20), comment='区县', key='town_name'),
    sa.Column('c_reason', sa.String(500), comment='招聘原因', key='reason'),
    sa.Column('c_age_min', sa.Integer, comment='最小年龄', key='age_min'),
    sa.Column('c_age_max', sa.Integer, comment='最大年龄', key='age_max'),
    sa.Column('c_language_level', sa.String(1000), comment="语言要求", key="language_level"),
    sa.Column("c_start_dt", sa.DateTime, comment="启动时间", key="start_dt"),
    sa.Column("c_stop_dt", sa.DateTime, comment="停止时间", key="stop_dt"),
    sa.Column('c_stop_by_id', sa.String(32), comment="停止人id", key="stop_by_id"),
    sa.Column('c_stop_by_name', sa.String(50), comment="停止人姓名", key="stop_by_name"),
    sa.Column('c_stop_reason', sa.String(100), comment="停止招聘原因", key="stop_by_reason"),
    sa.Column('c_position_description', sa.Text, comment="职位描述", key="position_description"),
    sa.Column('c_latest_entry_date', sa.DateTime, comment="最迟到岗时间", key="latest_entry_date"),
    sa.Column('c_employment_form_id', sa.String(32), comment="应聘登记表id", key="employment_form_id"),
    sa.Column('c_qrcode_url', sa.String(200), comment="职位小程序码", key="qrcode_url"),
    sa.Column('c_education', sa.Integer, comment='学历', key='education'),
    sa.Column('c_work_experience', sa.Integer, comment='工作经验要求', key='work_experience'),
    sa.Column('c_work_place_id', sa.String(32), comment='工作地点ID', key='work_place_id'),
    sa.Column('c_work_place_name', sa.String(256), comment='工作地点名称', key='work_place_name'),
    sa.Column('c_emergency_level', sa.Integer, comment='紧急程度', key='emergency_level'),
    sa.Column('c_job_title_id', sa.String(32), comment='岗位ID', key='job_title_id'),
    sa.Column('c_job_title_name', sa.String(100), comment='岗位名称', key='job_title_name'),
    sa.Column('c_deadline', sa.Date, comment="截止日期", key="deadline"),
    # sa.Column('c_support_recommendation', sa.Boolean, comment='是否支持内推', key='support_recommendation'),
    sa.Column('c_secret_position', sa.Boolean, comment="保密职位", key="secret_position"),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_by_name', sa.String(50), comment="添加人姓名", key="add_by_name"),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
    sa.Column('c_referral_bonus', sa.String(200), nullable=False, default='', comment='内推奖金', key='referral_bonus'),

    # 索引
    sa.Index('idx_basic', 'is_delete', 'company_id', 'status')
)

# 招聘职位类型表
tb_job_position_type = sa.Table(
    't_job_position_type', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id', key='id'),
    sa.Column('c_name', sa.String(64), nullable=False, comment='名称', key='name'),
    sa.Column('c_level', sa.Integer, nullable=False, comment='层级', key='level'),
    sa.Column('c_order', sa.Integer, nullable=False, comment='层级内排序', key='order'),
    sa.Column('c_parent_id', sa.String(32), comment='父级id', key='parent_id'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
)

# 职位和面试官关联表
tb_job_position_participant_rel = sa.Table(
    't_job_position_participant', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id', key="id"),
    # sa.Column('c_company_id', sa.String(32), comment='企业id', key="company_id"), #TODO 此表暂时没有此字段 需要补充
    sa.Column('c_job_position_id', sa.String(32), comment='职位id', key="job_position_id"),
    sa.Column(
        'c_participant_id', None, ForeignKey('models.m_recruitment_team.tb_participant.c_id'), key='participant_id'
    ),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key="add_dt"),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
)

# 免费版招聘职位数量限制表
tb_job_position_count_limit = sa.Table(
    't_job_position_count_limit', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id'),
    sa.Column('c_oid', sa.String(32), comment='原uuid'),
    sa.Column('c_company_id', sa.String(32), comment='企业id'),
    sa.Column('c_limit', sa.Integer, comment='限制数量'),
    sa.Column('c_is_default', sa.Boolean, comment='是否默认'),
    sa.Column('c_is_enable', sa.Boolean, comment='是否可用'),
    sa.Column('c_add_dt', sa.DateTime, default=datetime.now, comment='添加时间'),
    sa.Column('c_update_dt', sa.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间'),
)

# 职位导入记录表
tb_job_position_import = sa.Table(
    't_job_position_import', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id'),
    sa.Column('c_oid', sa.String(32), comment='原uuid'),
    sa.Column('c_company_id', sa.String(32), comment='企业id'),
    sa.Column('c_file_url', sa.String(1024), comment='文件地址'),
    sa.Column('c_status', sa.SmallInteger, comment='状态'),
    sa.Column('c_exception_info', sa.Text, comment='异常信息'),
    sa.Column('c_error_file_url', sa.String(1024), comment='错误文件下载地址'),
    sa.Column('c_all_count', sa.Integer, comment='总条数'),
    sa.Column('c_success_count', sa.Integer, comment='成功条数'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id'),
    sa.Column('c_add_dt', sa.DateTime, default=datetime.now, comment='添加时间'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人'),
    sa.Column('c_update_dt', sa.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间'),
)
