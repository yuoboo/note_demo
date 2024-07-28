
import datetime
import sqlalchemy as sa

from constants import EventScene, EventStatus
from models import meta

# 大数据上报记录表
from utils.strutils import gen_uuid

tb_data_report = sa.Table(
    "t_data_report_history", meta,
    sa.Column('c_id', sa.CHAR(32),  primary_key=True, default=gen_uuid, comment="id", key="id"),
    sa.Column('c_company_id', sa.CHAR(32), nullable=False, comment="企业id", key='company_id'),
    sa.Column('c_ev_scene', sa.SmallInteger, nullable=False, default=EventScene.UNKNOWN, comment="事件类型", key='ev_scene'),
    sa.Column('c_ev_code', sa.VARCHAR(10), nullable=False, default='', comment="事件编码", key='ev_code'),
    sa.Column('c_ev_data', sa.JSON, nullable=False, default='', comment="事件数据", key='ev_data'),
    sa.Column('c_status', sa.SmallInteger, nullable=False, default=EventStatus.DEFAULT, comment="上报状态", key="status"),
    sa.Column('c_exec_msg', sa.VARCHAR(500), nullable=False, default='', comment="错误信息", key="exec_msg"),
    sa.Column('c_add_dt', sa.DateTime, default=datetime.datetime.now, comment="创建时间", key="add_dt"),
    sa.Column('c_add_by_id', sa.CHAR(32), nullable=False, default='', comment="创建人", key="add_by_id")
)
