from wtforms import StringField, IntegerField

from bproxypool.core import BaseForm, ParamRequired


class DeleteProxyForm(BaseForm):
    proxy = StringField(validators=[ParamRequired()])
    source = StringField(validators=[ParamRequired()])


class CoolDownProxyForm(BaseForm):
    proxy = StringField(validators=[ParamRequired()])
    expire = IntegerField(default=1800)
