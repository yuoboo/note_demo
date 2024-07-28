import sqlalchemy as sa
from models import meta

# 行政区
from utils.strutils import gen_uuid

tb_district = sa.Table(
    "t_district", meta,
    sa.Column('c_id', sa.Integer,  primary_key=True, comment="id", key="id"),
    sa.Column('c_administrative_code', sa.String(12), comment="行政区代码", key='code'),
    sa.Column('c_pid', sa.Integer, comment="上级id", key='upstream'),
    sa.Column('c_name', sa.String(30), comment="名称", key='name'),
    sa.Column('c_full_name', sa.String(60), comment="全名", key='fullname'),
    sa.Column('c_merger_name', sa.String(200), comment="合名", key="mergername"),
    sa.Column('c_pinyin', sa.String(100), comment="拼音", key="pinyin"),
    sa.Column('c_pinyin_lite', sa.String(20), comment="简拼", key="pinyin_lite"),
    sa.Column('c_level', sa.Integer, comment="级别", key="level"),
    sa.Column('c_sort', sa.Integer, comment="排序", key="sort"),
    sa.Column('c_is_county_level_city', sa.Boolean, comment="是否县级市", key="is_county_level_city"),
    sa.Column('c_Population', sa.DECIMAL, comment="人口(万人)", key="population"),
    sa.Column('c_GDP', sa.DECIMAL, comment="GDP(亿元)", key="gdp"),

    sa.Index('ix_name_key', 'name'),
    sa.Index('ix_pinyin_key', 'pinyin'),
)


# 学校信息
tb_school_info = sa.Table(
    "t_school_info", meta,
    sa.Column('c_id', sa.Integer,  primary_key=True, comment="id", key="id"),
    sa.Column('c_name', sa.String(100), comment="学校名称", key='name'),
    sa.Column('c_label', sa.Integer, comment="学校标签", key='label'),
    # sa.Column('c_place', sa.String(100), comment="所属地区", key='place'),
    # sa.Column('c_abstract', sa.Text, comment="内容", key='abstract'),
)


# 分享短链接
tb_share_short_url = sa.Table(
    "t_share_short_url", meta,
    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_key', sa.String(32), comment="md5 key", key='key'),
    sa.Column('c_url', sa.String(256), comment="链接地址", key='url'),
    sa.Column('c_short_url', sa.String(256), comment="分享短连接", key='short_url'),
    sa.Column('c_add_dt', sa.DateTime, key='add_dt', comment='添加时间'),
)


# 分享小程序码
tb_share_miniqrcode = sa.Table(
    "t_share_miniqrcode", meta,
    sa.Column('c_id', sa.String(32), primary_key=True, nullable=False, comment='id', default=gen_uuid, key='id'),
    sa.Column('c_key', sa.String(32), comment="md5 key", key='key'),
    sa.Column('c_url', sa.String(400), comment="链接地址", key='url'),
    sa.Column('c_qr_code', sa.String(256), comment="分享短连接", key='qr_code'),
    sa.Column('c_add_dt', sa.DateTime, key='add_dt', comment='添加时间'),
)
