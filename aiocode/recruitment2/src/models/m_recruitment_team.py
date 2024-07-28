import sqlalchemy as sa
from models import meta

# 招聘团队表
tb_participant = sa.Table(
    't_participant', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key="id"),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key="company_id"),
    sa.Column('c_participant_type', sa.SmallInteger, comment='参与者类型', key="participant_type"),
    sa.Column('c_participant_refer_id', sa.String(32), comment='参与者关联id', key="participant_refer_id"),
    sa.Column('c_participant_refer_status', sa.SmallInteger, comment='是否被停用', key="participant_refer_status"),  # 原participant_refer_status
    sa.Column('c_company_user_id', sa.String(32), comment='企业用户id', key='company_user_id'),
    sa.Column('c_name', sa.String(35), comment='姓名', key="name"),
    sa.Column('c_avatar', sa.String(225), comment='头像', key="avatar"),
    sa.Column('c_mobile', sa.String(20), comment='手机号', key="mobile"),
    sa.Column('c_email', sa.String(100), comment='邮箱地址', key="email"),
    sa.Column('c_department_id', sa.String(32), comment='部门id', key='department_id'),
    sa.Column('c_department_name', sa.String(500), comment='部门名称', key='department_name'),
    sa.Column('c_job_id', sa.String(32), comment='岗位id', key='job_id'),
    sa.Column('c_job_name', sa.String(100), comment='岗位名称', key='job_name'),

    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),
)

# hr和员工关联表
tb_hr_emp_rel = sa.Table(
    't_hr_emp_rel', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key="id"),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_hr_id', sa.String(32), comment='hr的id', key='hr_id'),
    sa.Column('c_emp_id', sa.String(32), comment='员工id', key='emp_id'),

    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),
)
