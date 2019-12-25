from flask import request
from wtforms import Form, IntegerField
from wtforms.validators import DataRequired

from .exception import ParameterException


class BaseForm(Form):

    def __init__(self):
        tmp = request.args.to_dict()
        if request.json:
            for key, values in request.json.items():
                tmp[key] = values
        if request.form:
            for key, values in request.form.items():
                tmp[key] = values
        super().__init__(data=tmp)
        self.__validate_for_api()

    def __validate_for_api(self):
        if not super().validate():
            raise ParameterException(msg=self.errors)

    def to_dict(self):
        result = {}
        for name, field in self._fields.items():
            if field is not None and field.data is not None:
                if isinstance(field, IntegerField):
                    field.data = int(field.data)
                result[name] = field.data

        if len(result):
            return result
        raise ParameterException(msg='all arguments is Invalid')


class ParamRequired(DataRequired):
    """修复wtf DataRequired int=0 时识别失败的bug"""
    def __call__(self, form, field):
        if isinstance(field.data, int) and isinstance(field, IntegerField):
            return
        super().__call__(form, field)

