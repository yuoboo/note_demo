from sanic_wtf import SanicForm
from wtforms.fields import StringField, IntegerField
from wtforms.validators import DataRequired, Length


class CreateOrUpdateInformationForm(SanicForm):
    linkman = StringField(validators=[DataRequired(), Length(min=1, max=35)])
    linkman_mobile = StringField(validators=[DataRequired(), Length(min=1, max=20)])
    address = StringField(validators=[Length(min=0, max=200)])
    province_id = IntegerField(default=0)
    city_id = IntegerField(default=0)
    town_id = IntegerField(default=0)
