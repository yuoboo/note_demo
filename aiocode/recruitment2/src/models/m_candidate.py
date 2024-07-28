import sqlalchemy as sa

from models import meta

# 临时只读模型， 之后要切至redis和http

tb_candidate_remark = sa.Table(
    't_candidate_remark', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),

    sa.Column('c_candidate_id', sa.String(32), comment='候选人ID', key='candidate_id'),
    sa.Column('c_text', sa.String(256), comment='内容', key='text'),
)


tb_candidate_tag = sa.Table(
    't_candidate_tag', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),

    sa.Column('c_name', sa.String(64), comment='标签名称', key='name'),
    sa.Column('c_order', sa.Integer, comment='排序值', key='order'),
)

tb_candidate = sa.Table(
    't_candidate', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),

    sa.Column('c_name', sa.String(32), comment="候选人姓名", key="name"),
    sa.Column('c_mobile', sa.String(256), comment="手机号", key="mobile"),
    sa.Column('c_email', sa.String(256), comment="邮箱", key="email"),
    sa.Column('c_sex', sa.Integer, comment="性别", default=0, key="sex"),
    sa.Column('c_avatar', sa.String(1024), comment='候选人头像', key='avatar'),
    sa.Column('c_talent_is_join', sa.Boolean, comment='是否加入人才库', key='talent_is_join'),
    sa.Column('c_talent_join_dt', sa.DateTime, comment='入库时间', key='talent_join_dt'),
    sa.Column('c_talent_join_by_id', sa.String(32), comment='加入人才库操作人id', key='talent_join_by_id'),
    sa.Column('c_wework_external_contact', sa.SmallInteger, comment='企业微信外部联系人类型', key='wework_external_contact'),
)

tb_stand_resume = sa.Table(
    't_stand_resume', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人id', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),

    sa.Column('c_candidate_id', sa.String(32), comment='候选人ID', key='candidate_id'),
    sa.Column('c_candidate_record_id', sa.String(32), comment='应聘记录id', key='candidate_record_id'),
    sa.Column('c_data', sa.Text, comment='data', key='data'),
)
