# coding=utf-8
import uuid
from datetime import datetime

import sqlalchemy as sa

# 内推职位表
from sqlalchemy import ForeignKey

from constants import RecruitmentPageStatus, PosterType, PageStyle, WorkType, SalaryUnit, RecruitPageType, \
    DeliveryType
from constants.commons import null_uuid
from models import meta

# 企业介绍信息
from utils.strutils import gen_uuid

# 招聘门户网页记录表
tb_recruitment_portal_record = sa.Table(
    't_recruitment_page_record', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_company_id', sa.String(32), nullable=False, comment='企业id', key='company_id'),
    sa.Column('c_company_introduction_id', sa.String(32), comment='企业信息', default=None, key='company_introduction_id'),
    sa.Column('c_record_no', sa.Integer, nullable=False, comment='记录编码', autoincrement=True, key='record_no'),
    sa.Column('c_name', sa.String(100), nullable=False, comment='名称', key='name'),
    sa.Column('c_desc', sa.String(256), comment='描述内容', default='', key='desc'),
    sa.Column('c_recruitment_channel_id', sa.String(32), comment='招聘渠道', default=None, key='recruitment_channel_id'),
    sa.Column('c_status', sa.SmallInteger, comment='状态值', default=RecruitmentPageStatus.on_line, key='status'),
    sa.Column('c_online_dt', sa.DateTime, comment='上线时间', default=datetime.now, key='online_dt'),
    sa.Column('c_online_by', sa.String(32), comment='上线人id', default=None, key='online_by'),
    sa.Column('c_offline_dt', sa.DateTime, comment='下线时间', key='offline_dt'),
    sa.Column('c_offline_by', sa.String(32), comment='下线人id', default=None, key='offline_by'),
    sa.Column('c_poster_title', sa.String(100), comment='海报标题', default='', key='poster_title'),
    sa.Column('c_poster_subtitle', sa.String(100), comment='海报副标题', default='', key='poster_subtitle'),
    sa.Column('c_poster_type', sa.SmallInteger, comment='海报类型', default=PosterType.default, key='poster_type'),
    sa.Column('c_poster_url', sa.String(200), comment='海报地址', key='poster_url'),
    sa.Column('c_is_default', sa.Boolean, comment='是否默认', default=False, key='is_default'),
    sa.Column('c_is_valid', sa.Boolean, comment='是否有效', default=False, key='is_valid'),
    sa.Column('c_valid_dt', sa.DateTime, comment='设为有效时间', key='valid_dt'),
    sa.Column('c_style', sa.SmallInteger, comment='海报风格', default=PageStyle.Style1, key='style'),
    sa.Column('c_allow_delivery', sa.Boolean, comment='是否允许求职者投递简历', default=True, key='allow_delivery'),  # v2.9 add

    sa.Column('c_add_by_id', sa.String(32), nullable=False, comment='添加人id', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), nullable=False, comment='修改人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    # 索引
    sa.Index('ix_page_record_no', 'record_no'),
    sa.Index('ix_company_id', 'company_id'),
)

# 企业福利标签
tb_company_welfare_tag = sa.Table(
    't_company_welfare_tag', meta,

    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_name', sa.String(100), comment='福利标签名', key='name'),
    sa.Column('c_order', sa.Integer, comment='排序值', default=99, key='order'),

    sa.Column('c_add_by_id', sa.String(32), nullable=False, comment='添加人id', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), nullable=False, comment='修改人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    sa.Index("ix_company_id", 'company_id')
)


# 招聘门户网页海报
tb_recruitment_portal_poster = sa.Table(
    't_recruitment_page_poster_attach', meta,

    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    # sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_recruitment_page_id', sa.String(32), nullable=False, comment='招聘网页id', key='recruitment_page_id'),
    sa.Column('c_position_x', sa.Float, comment='二维码横坐标', default=None, key='position_x'),
    sa.Column('c_position_y', sa.Float, comment='二维码纵坐标', default=None, key='position_y'),
    sa.Column('c_origin_poster', sa.String(500), comment='原始海报地址', key='origin_poster'),
    sa.Column('c_newest_poster', sa.String(500), comment='最新海报地址', key='newest_poster'),
    sa.Column('c_qr_url', sa.String(32), comment='二维码地址', default=None, key='qr_url'),
    sa.Column('c_required_qr', sa.Boolean, comment='是否需要合成二维码', default=False, key='required_qr'),
    sa.Column('c_file_data', sa.Text, comment='文件信息', default='', key='file_data'),

    sa.Column('c_add_by_id', sa.String(32), nullable=False, comment='添加人id', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), nullable=False, comment='修改人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    # 没有索引
)

# 招聘网页关联职位信息
tb_recruit_portal_position = sa.Table(
    't_recruitment_page_job_position', meta,

    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_record_no', sa.Integer, comment='记录编码', autoincrement=True, key='record_no'),
    sa.Column('c_recruitment_page_id', None,
              ForeignKey('models.m_recruit_portal.tb_recruitment_portal_record.c_id'), comment='招聘网页id',
              key='recruitment_page_id'),
    sa.Column('c_job_position_id', None,
              ForeignKey('models.m_job_position.tb_job_position.c_id'), comment='招聘职位id', key='job_position_id'),
    sa.Column('c_first_cate', sa.String(100), comment='职位分类名称(第一级)', key='first_cate'),
    sa.Column('c_secondary_cate', sa.String(100), comment='职位分类名称(二级)', key='secondary_cate'),
    sa.Column('c_category_name', sa.String(100), comment='职位分类名称(三级)', key='category_name'),
    sa.Column('c_work_type', sa.SmallInteger, comment='工作性质', default=WorkType.full_time, key='work_type'),
    sa.Column('c_name', sa.String(100), comment='职位名称', key='name'),
    sa.Column('c_position_total', sa.SmallInteger, comment='招聘人数', default=None, key='position_total'),
    sa.Column('c_work_experience', sa.SmallInteger, comment='工作年限', default=None, key='work_experience'),   # WorkExperience
    sa.Column('c_education', sa.SmallInteger, comment='学历', default=None, key='education'),     # JobPositionEducation
    sa.Column('c_salary_min', sa.Integer, comment='薪资范围(小)', default=0, key='salary_min'),
    sa.Column('c_salary_max', sa.Integer, comment='薪资范围(大)', default=0, key='salary_max'),
    sa.Column('c_salary_unit', sa.SmallInteger, comment='薪资单位', default=SalaryUnit.month, key='salary_unit'),
    sa.Column('c_settlement_way', sa.SmallInteger, comment='结算方式', default=None, key='settlement_way'),  # SettlementWay
    sa.Column('c_age_min', sa.Integer, comment='最小年龄', default=None, key='age_min'),
    sa.Column('c_age_max', sa.Integer, comment='最大年龄', default=None, key='age_max'),
    sa.Column('c_position_description', sa.Text, comment='职位描述', key='position_desc'),
    sa.Column('c_poster_position_desc', sa.Text, comment='海报职位描述', key='poster_position_desc'),
    sa.Column('c_welfare_tag', sa.String(2000), comment='福利标签', key='welfare_tag'),
    sa.Column('c_sort', sa.Integer, comment='职位排序', default=1, key='sort'),
    sa.Column('c_province_id', sa.Integer, comment='省份id', default=None, key='province_id'),
    sa.Column('c_province_name', sa.String(20), comment='省份', default=None, key='province_name'),
    sa.Column('c_city_id', sa.Integer, comment='城市id', default=None, key='city_id'),
    sa.Column('c_city_name', sa.String(32), comment='城市', default=None, key='city_name'),
    sa.Column('c_town_id', sa.Integer, comment='区县id', default=None, key='town_id'),
    sa.Column('c_town_name', sa.String(20), comment='区县', default=None, key='town_name'),
    sa.Column('c_work_address', sa.String(200), comment='工作地址', default=None, key='work_address'),
    sa.Column('c_address_longitude', sa.Float, comment='地址经度', default=None, key='address_longitude'),
    sa.Column('c_address_latitude', sa.Float, comment='地址纬度', default=None, key='address_latitude'),
    sa.Column('c_contacts', sa.String(32), comment='联系人', key='contacts'),
    sa.Column('c_contact_number', sa.String(100), comment='联系电话', key='contact_number'),
    sa.Column('c_contact_email', sa.String(100), comment='联系邮箱', key='contact_email'),
    sa.Column('c_qrcode_url', sa.String(256), comment='关联此职位的小程序码', key='qrcode_url'),

    sa.Column('c_referral_bonus', sa.String(200), nullable=False, default='', comment='内推奖金', key='referral_bonus'),

    sa.Column('c_add_by_id', sa.String(32), nullable=False, comment='添加人id', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), nullable=False, comment='修改人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    # 索引
    sa.Index('ix_position_record_no', 'record_no'),
    sa.Index('ix_company_id', 'company_id')
)

# 投递记录
tb_delivery_record = sa.Table(
    't_candidate_application_record', meta,

    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_company_id', sa.String(32), comment='企业id', key='company_id'),
    sa.Column('c_open_id', sa.String(50), nullable=False, comment='微信openid', default='', key='open_id'),
    sa.Column('c_union_id', sa.String(50), comment='微信union_id', key='union_id'),
    sa.Column('c_candidate_record_id', None,
              ForeignKey('models.m_candidate_record.tb_candidate_record.c_id'),
              key='candidate_record_id', comment="应聘记录ID"),
    sa.Column('c_position_record_id', None,
              ForeignKey('models.m_portals.tb_recruit_portal_position.c_id'),
              key='position_record_id', comment='申请职位id'),
    sa.Column('c_recruitment_page_id', None,
              ForeignKey('models.m_recruit_portal.tb_recruitment_portal_record.c_id'),
              nullable=False, comment='招聘网页', key='recruitment_page_id'),

    sa.Column('c_delivery_scene', sa.SmallInteger, comment='投递场景', default=RecruitPageType.wx_recruit,
              key='delivery_scene'),    # v2.9 add
    sa.Column('c_delivery_type', sa.SmallInteger, comment='投递人类型', default=DeliveryType.candidate, key='delivery_type'),   # v2.9 add
    sa.Column('c_referee_id', sa.String(32), comment='内推人id', default=null_uuid, key='referee_id'),    # v2.9 add
    sa.Column('c_referral_bonus', sa.String(200), nullable=False, default='', comment='内推奖金', key='referral_bonus'),    # v2.9 add
    sa.Column('c_is_payed', sa.Boolean, nullable=False, comment='是否发放奖金', default=False, key='is_payed'),  # v2.9 add
    sa.Column('c_reason', sa.String(500), nullable=False, comment="投递原因", default='', key="reason"),  # v2.9 add

    sa.Column('c_add_by_id', sa.String(32), nullable=False, comment='添加人id', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_by_id', sa.String(32), nullable=False, comment='修改人id', default=null_uuid, key='update_by_id'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_is_delete', sa.Boolean, comment='是否删除', default=False, key='is_delete'),

    # index
    sa.Index('ix_com_record', 'company_id', "candidate_record_id", "referee_id")
)

# 内推人配置信息表  # v2.9 add
tb_referee_config = sa.Table(
    't_recruitment_referee_config', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_company_id', sa.String(32), nullable=False, comment='企业id', key='company_id'),
    sa.Column('c_employee_id', sa.String(32), nullable=False, comment='员工id', key='employee_id'),
    sa.Column(
        'c_qr_code_type', sa.SmallInteger, nullable=False,
        comment='二维码类型(1.微信、2.企业微信)', default=0, key='qrcode_type'
    ),
    sa.Column('c_qr_code_url', sa.String(256), nullable=False, comment='二维码地址', default='', key='qrcode_url'),
    sa.Column('c_add_by_id', sa.String(32), nullable=False, comment='添加人', default=null_uuid, key='add_by_id'),
    sa.Column('c_add_dt', sa.DateTime, comment='添加时间', default=datetime.now, key='add_dt'),
    sa.Column('c_update_dt', sa.DateTime, comment='修改时间', default=datetime.now, onupdate=datetime.now, key='update_dt'),
    sa.Column('c_update_by_id', sa.String(32), nullable=False, comment='修改人', default=null_uuid, key='update_by_id'),
    sa.Column('c_is_delete', sa.Boolean, nullable=False, comment='是否删除', default=False, key='is_delete'),

    # Index
    sa.Index('idx_com_emp', 'company_id', 'employee_id')
)

# 员工内推职位小程序码记录
tb_share_position_qr_code = sa.Table(
    't_share_position_qr_code', meta,
    sa.Column('c_id', sa.String(32), primary_key=True, default=gen_uuid, key='id', comment='ID'),
    sa.Column('c_company_id', sa.String(32), nullable=False, key='company_id', comment="企业ID"),
    sa.Column('c_refer_id', sa.String(32), nullable=False, key='refer_id', comment="相关ID(员工或渠道)"),
    sa.Column(
        'c_position_record_id', sa.String(32), nullable=False, key='position_record_id', comment="网页职位ID"
    ),
    sa.Column('c_qr_code_url', sa.String(200), default='', key='qrcode_url', comment="职位分享小程序码"),
    sa.Column('c_add_by_id', sa.String(32), key='add_by_id', comment='添加人ID'),
    sa.Column('c_add_dt', sa.DateTime, key='add_dt', default=datetime.now, comment='添加时间'),

    # index
    sa.Index('idx_share_refer_position', 'company_id', 'refer_id', 'position_record_id')
)

tb_company_referral_config = sa.Table(
    't_company_referral_config', meta,
    sa.Column('c_id', sa.String(32), primary_key=True,  default=gen_uuid, key='id', comment='ID'),
    sa.Column('c_company_id', sa.String(32), nullable=False, key='company_id', comment="企业ID"),
    sa.Column('c_desc_title', sa.String(100), nullable=False, default='', key='desc_title', comment='说明标题'),
    sa.Column('c_desc', sa.String(1000), nullable=False, default='', key='desc', comment='内推说明'),
    sa.Column('c_add_by_id', sa.String(32), key='add_by_id', comment='添加人ID'),
    sa.Column('c_add_dt', sa.DateTime, key='add_dt', default=datetime.now, comment='添加时间'),
    sa.Column('c_update_by_id', sa.String(32), key='update_by_id', comment='更新人'),
    sa.Column('c_update_dt', sa.DateTime, key='update_dt', default=datetime.now, onupdate=datetime.now, comment='更新时间'),

    # index
    sa.Index('un_com', 'company_id')
)
