# coding: utf_8
from sanic_wtf import SanicForm
from wtforms import StringField, IntegerField, FieldList


class StatsBaseForm(SanicForm):
    """
    统计分析基本校验
    """
    dep_id = StringField(label="用人部门")
    city_ids = FieldList(IntegerField(), label="工作城市")
    participant_ids = FieldList(StringField(), label="招聘HR")
