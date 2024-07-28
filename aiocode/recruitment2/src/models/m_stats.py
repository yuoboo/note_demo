# -*- coding: utf-8 -*-
import sqlalchemy as sa

from models import meta

# 职位进度统计表
tb_recruitment_progress = sa.Table(
    't_recruitment_progress', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id'),
    sa.Column('c_job_position_id', sa.String(32), comment='职位id'),
    sa.Column('c_to_be_screened', sa.Integer, comment='待初筛'),
    sa.Column('c_screen_passed', sa.Integer, comment='初筛通过'),
    sa.Column('c_interview_data', sa.String(1024), comment='面试信息'),  # {"scheduled": 1, "interviewed": 1, "passed": 1}}
    sa.Column('c_offered', sa.Integer, comment='已发offer'),
    sa.Column('c_pending_entry', sa.Integer, comment='待入职'),
    sa.Column('c_have_joined', sa.Integer, comment='已入职'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间'),
)

# 招聘渠道统计表
tb_channel_statistics = sa.Table(
    't_channel_stats', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, comment='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id'),
    sa.Column('c_channel_id', sa.String(32), comment='渠道id'),
    sa.Column('c_candidates', sa.Integer, comment='候选人数'),
    sa.Column('c_interviews', sa.Integer, comment='安排面试数'),
    sa.Column('c_offers', sa.Integer, comment='已发offer'),
    sa.Column('c_elimination', sa.Integer, comment='淘汰人数'),
    sa.Column('c_enrollment', sa.Integer, comment='入职人数'),
)
