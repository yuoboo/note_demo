# -*- coding: utf-8 -*-
import sqlalchemy as sa
from datetime import datetime

from constants import ShowColor
from constants.commons import null_uuid
from models import meta

# 招聘渠道表
from utils.strutils import gen_uuid


tb_recruitment_channel = sa.Table(
    't_recruitment_channel', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_name', sa.String(32), comment='渠道名称', key='name'),
    sa.Column('c_remark', sa.String(256), comment='备注', key='remark'),
    sa.Column('c_is_system', sa.Boolean, comment='是否系统', default=False, key='is_system'),
    sa.Column('c_is_forbidden', sa.Boolean, comment='是否禁用', default=False, key='is_forbidden'),
    sa.Column('c_related_url', sa.String(512), comment='跳转链接', default='', key='related_url'),
    sa.Column('c_all_system', sa.Boolean, comment='系统保留', default=False, key='all_system'),
    sa.Column('c_order_no', sa.Integer, comment='排序值', default=999, key='order_no'),
    sa.Column('c_show_color', sa.String(16), default=ShowColor.black, key='show_color', comment='显示颜色'),

    sa.Column('c_add_by_id', sa.String(32), comment='添加人', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', default=null_uuid, key='update_by_id'),
    sa.Column(
        'c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'
    ),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),
)

# 企业介绍表
tb_company_intro = sa.Table(
    "t_company_introduction", meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', key='id'),
    sa.Column('c_company_id', sa.String, comment='企业id', key='company_id'),
    sa.Column('c_company_name', sa.String(100), default='', comment='企业名称', key='company_name'),
    sa.Column('c_company_scale_id', sa.Integer, default=0, comment='企业规模ID', key='company_scale_id'),
    sa.Column('c_industry_id', sa.Integer, default=0, comment='行业ID', key='industry_id'),
    sa.Column('c_second_industry_id', sa.Integer, default=0, comment='二级行业ID', key='second_industry_id'),
    sa.Column('c_contacts', sa.String(32), default='', comment='联系人', key='contacts'),
    sa.Column('c_contact_number', sa.String(100), default='', comment='联系人电话', key='contact_number'),
    sa.Column('c_contact_email', sa.String(100), default='', comment='联系人邮箱', key='contact_email'),
    sa.Column('c_company_address', sa.String(200), default='', comment='企业地址', key='company_address'),
    sa.Column('c_address_longitude', sa.Float, comment='地址经度', key='address_longitude'),
    sa.Column('c_address_latitude', sa.Float, comment='地址纬度', key='address_latitude'),
    sa.Column('c_company_desc', sa.Text, comment='企业描述', key='company_desc'),
    sa.Column('c_welfare_tag', sa.String(2000), comment='企业福利标签', default='', key='welfare_tag'),
    sa.Column('c_logo_url', sa.String(200), comment='企业logo', default='', key='logo_url'),
    sa.Column('c_image_url', sa.String(2000), comment='企业照片', default='', key='image_url'),
    sa.Column('c_qrcode_type', sa.SmallInteger, nullable=False, comment='二维码类型(1.微信、2.企业微信)', default=1, key='qrcode_type'),
    sa.Column('c_wechat_qrcode', sa.String(256), comment='联系人微信码', default='', key='qrcode_url'),
    sa.Column('c_qrcode_user_id', sa.String(32), comment='二维码用户id', key='qrcode_user_id'),
    sa.Column('c_is_default', sa.Boolean, comment='是否默认',  default=False, key='is_default'),
    sa.Column('c_order_no', sa.Integer, comment='排序值', default=1, key='order_no'),

    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', key='is_delete'),

    # 索引
    sa.Index('ix_company_id', 'company_id')
)

# 选择而表头
tb_select_field = sa.Table(
    "t_select_field_record", meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment="id", key="id"),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key="company_id"),
    sa.Column('c_form_type', sa.SmallInteger, comment='', key='scene_type'),
    sa.Column('c_add_by_type', sa.SmallInteger, comment='用户类型', key='user_type'),
    sa.Column('c_add_by_id', sa.String(32), comment="添加人", key='add_by_id'),
    sa.Column('c_fields', sa.Text, comment="所选字段", key='fields'),
    sa.Column('c_is_deleted', sa.Boolean, comment="是否删除", default=False, key="is_deleted"),
    sa.Column('c_add_dt', sa.DateTime, comment="添加时间", default=sa.func.now(), key='add_dt'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', onupdate=sa.func.now(), key='update_dt'),

    # 存在的索引
    sa.Index('ix_company_add_by_type_delete', 'company_id', 'add_by_id', 'scene_type', 'is_deleted')
)

# 招聘开通表
tb_company_request = sa.Table(
    't_company_request', meta,
    sa.Column('c_id', sa.String(32), comment='原uuid', key='id'),
    sa.Column('c_company_id', sa.String, comment='企业id', key='company_id'),
    sa.Column('c_add_by_id', sa.String, comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_interview_count', sa.Integer, comment='默认面试轮次', key='interview_count'),
)


# 淘汰原因
tb_eliminated_reason = sa.Table(
    't_eliminated_reason', meta,
    sa.Column('c_id', sa.String(32), primary_key=True,  default=gen_uuid, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_reason', sa.String(200), comment='淘汰原因', key='reason'),
    sa.Column('c_is_system', sa.Boolean, comment='是否系统', default=False, key='is_system'),
    sa.Column('c_reason_step', sa.SmallInteger, comment="所属阶段", key='reason_step'),
    sa.Column('c_order_no', sa.Integer, comment="排序值", default=1, nullable=False, key='order_no'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    sa.Index('idx_basic', 'is_delete', 'company_id')
)

# 面试信息表
tb_interview_information = sa.Table(
    't_interview_information', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key="id"),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key="company_id"),
    sa.Column('c_linkman', sa.String(35), comment='联系人', key='linkman'),
    sa.Column('c_linkman_mobile', sa.String(20), comment='联系电话', key="linkman_mobile"),
    sa.Column('c_address', sa.String(200), comment='地址', key='address'),
    sa.Column('c_province_id', sa.Integer, comment='省份id', key='province_id'),
    sa.Column('c_province_name', sa.String(20), comment='省份名', key='province_name'),
    sa.Column('c_city_id', sa.Integer, comment='城市id', key='city_id'),
    sa.Column('c_city_name', sa.String(20), comment='城市名', key='city_name'),
    sa.Column('c_town_id', sa.Integer, comment='区县id', key='town_id'),
    sa.Column('c_town_name', sa.String(20), comment='区县名', key='town_name'),
    sa.Column('c_order_no', sa.Integer, comment='排序值', key='order_no'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=sa.func.now(), key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', onupdate=sa.func.now(), key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    # index
    sa.Index('idx_basic', 'is_delete', 'company_id')
)

# email模板表
tb_email_template = sa.Table(
    't_email_template', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_name', sa.String(100), comment='模板名称', key='name'),
    sa.Column('c_email_title', sa.String(100), comment='邮件标题', key='email_title'),
    sa.Column('c_email_content', sa.Text, comment='邮件内容', key='email_content'),
    sa.Column('c_usage', sa.SmallInteger, comment='用途', key='usage'),
    sa.Column('c_is_default', sa.Boolean, comment='是否是默认', key='is_default'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), comment='更新人', key='update_by_id'),
    sa.Column(
        'c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'
    ),
    sa.Column('c_is_deleted', sa.Boolean, comment='是否删除', default=False, key='is_deleted'),

    sa.Index('t_email_template_company_id', 'company_id')
)

# 邮件模板附件
tb_email_template_attach = sa.Table(
    't_email_template_attach', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_email_template_id', sa.String(32), comment='邮件模板ID', key='email_template_id'),
    sa.Column('c_file_name', sa.String(128), comment='文件名称', key='file_name'),
    sa.Column('c_file_size', sa.Integer, comment='文件大小', key='file_size'),
    sa.Column('c_file_type', sa.String(32), comment='文件类型', key='file_type'),
    sa.Column('c_file_key', sa.String(512), comment='文件key', key='file_key'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_deleted', sa.Boolean, comment='是否删除', default=False, key='is_deleted'),

)

# 自定义筛选条件配置
tb_custom_search = sa.Table(
    't_config_custom_search', meta,
    sa.Column('c_id', sa.Integer, primary_key=True, default=gen_uuid, comment='id', key='id'),
    sa.Column('c_company_id', sa.String, comment='企业id', key='company_id'),
    sa.Column('c_scene_type', sa.SmallInteger, comment='场景类型：1、招聘中；2、已淘汰；', key='scene_type'),
    sa.Column('c_user_type', sa.String(100), comment='用户类型：1、HR；2、员工；', key='user_type'),
    sa.Column('c_add_by_id', sa.String(32), comment='添加人', key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=sa.func.now(), key='add_dt'),
    sa.Column('c_update_dt', sa.DateTime, comment='更新时间', onupdate=sa.func.now(), key='update_dt'),
    sa.Column('c_config', sa.Text, comment='自定义筛选条件配置json格式', key='config')
)
