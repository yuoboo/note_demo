# -*- coding: utf-8 -*-

from sanic_wtf import SanicForm
from wtforms import FieldList
from wtforms.fields import StringField, Field
from wtforms.validators import DataRequired, Length, ValidationError


class CreateCandidateTagForm(SanicForm):
    name = StringField(validators=[DataRequired(), Length(min=1, max=32)])


class UpdateCandidateTagForm(SanicForm):
    name = StringField(validators=[DataRequired(), Length(min=1, max=32)])


class CandidateTagSortForm(SanicForm):
    sorts = FieldList(Field(), validators=[DataRequired(), Length(min=1)])

    def validate_sorts(self, field):
        sorts = field.data
        for item in sorts:
            if not isinstance(item, dict):
                raise ValidationError(message='sorts格式不合法')
            if not all((
                    'id' in item,
                    isinstance(item['id'], int)
            )) or not all((
                    'index' in item,
                    isinstance(item['id'], int)
            )):
                raise ValidationError(message='sorts格式不合法')
