
from sqlalchemy import processors
from sqlalchemy.sql.sqltypes import String as sa_String
from sqlalchemy.sql.sqltypes import JSON as sa_JSON
# from aiomysql.sa.engine import MySQLCompiler_pymysql, MySQLDialect_pymysql
from constants.commons import null_uuid
from utils.json_util import json_loads


def _json_deserializer(value):
    """
    自定义JSON反序列化方法
    """
    if value is None:
        return None
    elif not value:
        return ""

    return json_loads(value)

# _dialect = MySQLDialect_pymysql(paramstyle='pyformat', json_deserializer=_json_deserializer)
# _dialect.statement_compiler = MySQLCompiler_pymysql
# _dialect.default_paramstyle = 'pyformat'


# 将JSON 字段中的默认解析器换成自定义
def _result_processor_json(self, dialect, coltype):
    string_process = self._str_impl.result_processor(dialect, coltype, is_json=True)
    # json_deserializer = dialect._json_deserializer or json.loads
    json_deserializer = dialect._json_deserializer or _json_deserializer

    def process(value):
        if value is None:
            return None
        if string_process:
            value = string_process(value)
        return json_deserializer(value)

    return process


sa_JSON.result_processor = _result_processor_json


# 将String 中填充的 null_uuid 默认值换成None
def _result_processor_string(self, dialect, coltype, is_json=False):
    wants_unicode = self._expect_unicode or dialect.convert_unicode
    needs_convert = wants_unicode and (
        dialect.returns_unicode_strings is not True
        or self._expect_unicode in ("force", "force_nocheck")
    )
    needs_isinstance = (
        needs_convert
        and dialect.returns_unicode_strings
        and self._expect_unicode != "force_nocheck"
    )
    if needs_convert:
        if needs_isinstance:
            return processors.to_conditional_unicode_processor_factory(
                dialect.encoding, self._expect_unicode_error
            )
        else:
            return processors.to_unicode_processor_factory(
                dialect.encoding, self._expect_unicode_error
            )
    else:
        # _iml = dialect._type_memos[self]
        # print(_iml)
        def process(value):
            # 将 null_uuid 置换为 None
            if value == null_uuid:
                return None
            return value
        return process


sa_String.result_processor = _result_processor_string
