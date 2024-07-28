from datetime import datetime

import sqlalchemy as sa

from constants.commons import null_uuid
from models import meta
from utils.strutils import gen_uuid


tb_wework_external_contact = sa.Table(
    't_wework_external_contact', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_external_type', sa.Integer, nullable=False, comment='外部联系人类型(1.微信、2.企业微信)',
              default=0, key='external_type'),
    sa.Column('c_external_id', sa.String(50), comment='外部联系人id', default='', key='external_id'),
    sa.Column('c_unionid', sa.String(50), comment='微信开放平台的唯一身份标识', default='', key='unionid'),
    sa.Column('c_name', sa.String(32), comment='姓名', key='name'),
    sa.Column('c_candidate_id', sa.String(32), comment='候选人id', default=null_uuid, key='candidate_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
)


tb_wework_external_contact_data = sa.Table(
    't_wework_external_contact_data', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_wework_external_contact_id', sa.String(32), comment='候选人id', default=null_uuid, key='wework_external_contact_id'),
    sa.Column('c_follow_user', sa.JSON, comment='关联用户信息', default="", key='follow_user'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
)


tb_wework_external_contact_way = sa.Table(
    't_wework_external_contact_way', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_app_id', sa.Integer, comment='app id', key='app_id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_employee_id', sa.String(32), comment='员工id', key='employee_id'),
    sa.Column('c_wework_user_id', sa.String(32), comment='企业微信用户id', key='wework_user_id'),
    sa.Column('c_config_id', sa.String(32), comment='联系方式的配置id', key='config_id'),
    sa.Column('c_qr_code', sa.String(200), comment='联系我二维码链接', key='qr_code'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
)
