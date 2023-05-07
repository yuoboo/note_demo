# import cvxpy as cp
#
# dir(cp)
import datetime
import json
from io import BytesIO
import xlsxwriter
from xlsxwriter.format import Format as _Format
import redis


cache = redis.Redis()


class SheetError(Exception):
    pass


class BaseExport(object):
    """
    输入导出数据
    data: 数据行数组
    name: 表名
    """
    header_format = {'bold': True, "font_size": 12, "bg_color": "#E2DFDF"}
    remark = ""

    def __init__(self, export_data: list,
                 sheet_name: str = None, header: list = None,
                 company_name: str = None, is_fill_remark=False,
                 auto_filter: bool = False, column_width: int = 12
                 ):
        self.export_data = export_data or []
        self.sheet_name = sheet_name
        self.header = header or []
        self.company_name = company_name
        self.is_fill_remark = is_fill_remark    # 是否自动使用company_name 填充remark, 当remark为空时才生效
        self.column_width = column_width
        self._auto_filter = auto_filter
        # self.output = BytesIO()
        # self.workbook = xlsxwriter.Workbook(self.output)
        self.workbook = xlsxwriter.Workbook("gzh.xlsx")
        self._stream = None
        self.sheet = None
        self.sheets_map = dict()

    def add_sheet(self, sheet_name: str):
        if sheet_name in self.sheets_map:
            raise SheetError(f"sheet_name:{sheet_name} 不能重复")

        sheet = self.workbook.add_worksheet(sheet_name)
        self.sheet = sheet
        self.sheets_map[sheet_name] = sheet

    def switch_sheet(self, sheet_name: str):
        if sheet_name not in self.sheets_map:
            self.add_sheet(sheet_name)
        else:
            self.sheet = self.sheets_map[sheet_name]

    def add_wb_format(self, format_dict: dict) -> _Format:
        return self.workbook.add_format(format_dict)

    def write(self, sheet_name: str = None, sheet_data: list = None,
              sheet_header: list = None, header_format: dict = None):
        if sheet_name:
            self.switch_sheet(sheet_name)
        elif not self.sheet:
            self.add_sheet(self.sheet_name)

        sheet_header = sheet_header or self.header
        if sheet_data is None:
            sheet_data = sheet_data or self.export_data
        if header_format is None:
            header_format = header_format or self.header_format

        _index = 0
        if self.remark:
            _index += 1

        self.sheet.write_row(_index, 0, sheet_header)
        _index += 1

        for index, row in enumerate(sheet_data):
            index += _index
            self.sheet.write_row(index, 0, row)

        # 设置sheet样式
        self.set_ws_format(self.sheet, len(sheet_header), header_format=header_format)

        # 写备注
        self.write_comment()

    @staticmethod
    def merge_cell(ws, options):
        for i in options:
            ws.merge_range(i["cell"], i["content"], i.get("format", None))

    @staticmethod
    def excel_style(col):
        """ 用行列数量获取excel坐标. """
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = []
        while col:
            col, rem = divmod(col - 1, 26)
            result[:0] = letters[rem]
        return ''.join(result)

    def _merge_remark(self, ws, col: str, col_count: int, content: str):
        title_col = col if col_count <= 13 else "M"

        # merge_format = self.workbook.add_format({"font_color": '#428bca'})
        # merge_format.set_text_wrap(1)
        # merge_format.set_align('vjustify')
        # merge_format.set_font_size(15)
        #
        merge_obj = [
            {"cell": "A1:{}1".format(title_col), "content": content, "format": self.workbook.add_format(
                        {'align': 'center', 'valign': 'vcenter', 'font_size': 15, "font_color": '#428bca'})}
        ]
        self.merge_cell(ws, merge_obj)

    def set_ws_format(self, ws, col_count, header_format: dict = None):
        """设置表格样式"""
        col = self.excel_style(col_count)

        _start_index = 0
        if self.remark:
            # 如果有表格说明则将第一行高度设置为36, 且将表头的行数设置为2
            ws.set_row(0, 36)
            _start_index = 1
            # 合并表格说明
            self._merge_remark(ws, col, col_count, content=self.remark)

        elif self.is_fill_remark and self.company_name:
            _start_index = 1
            ws.set_row(0, 36)
            self._merge_remark(ws, col, col_count, content=self.company_name)

        # 设置表头格式
        header_format = header_format or self.header_format
        ws.set_row(_start_index, None, self.add_wb_format(header_format))

        # 设置表格所有列的宽度
        ws.set_column(f"A:{col}", self.column_width)

        # 设置表头所有列自动过滤
        if self._auto_filter:
            ws.autofilter(f"A{_start_index}:{col}{_start_index}")
        # ws.freeze_panes("D3")   # 冻结列

    def write_comment(self):
        """
        写备注
        :return:
        """
        # self.sheet.write_comment('A1', '可填写：\n男\n女')
        pass

    def sheet_format(self):
        pass

    def save(self):
        # if not self._stream:
        self.write()
        self.sheet_format()
        self.workbook.close()
            # self._stream = self.output.getvalue()
            # self.output.close()
        # return self._stream


class ListExport(BaseExport):
    """
    一般列表的导出基类
    """
    header = []
    fields = []
    remark = ""

    def __init__(self, export_data: list, sheet_name: str, company_name: str = None):
        _data = self.handle_data(export_data)
        super(ListExport, self).__init__(
            export_data=_data, sheet_name=sheet_name, header=self.header,
            company_name=company_name
        )

    def handle_data(self, export_data, fields: list = None):
        return list(map(lambda row_data: self.get_row_value(row_data, fields=fields), export_data))

    def clean_row_data(self, row_data):
        """处理行数据"""
        return row_data

    def get_row_value(self, row_data, fields: list = None):
        """获取行值 先处理行数据之后返回 fields 中的对应值"""
        fields = fields or self.fields
        _clean_data = self.clean_row_data(row_data)
        return map(lambda x: _clean_data.get(x, ""), fields)


class ManySheetListExport(ListExport):
    # _sheet_maps: dict = {}     # sheet_key: sheet_name 的方式，导出时会根据这个sheet_maps来导出
    # headers: dict = {}  # {sheet_key: [headers], ..} 设置每个sheet的导出表头
    # fields: dict = {}   # {sheet_key: [fields], ..} 每个表头对应的取值字段
    remark = ""     # 目前支持写入统一的remark, # todo 支持每个sheet不同的remark

    def __init__(self, export_data: list, company_name: str = None, is_fill_remark=False,
                 auto_filer: bool = False, column_width: int = 12
                 ):
        """
        支持多个sheet导出
        :param export_data: []
        :param company_name:
        :param is_fill_remark:
        :param auto_filer:
        :param column_width:

        @example:

        class DemoExport(ManySheetListExport):
            # 导出的excel会有三个sheet， 分别为候选人， 招聘职位 和人才
            pass
        demo_data = [{"sheet_name": "", "body": [{}, {}, {}], "header": [{"label": "", "property": ""}, {},...]}]
        demo = DemoExport(export_data=demo_data)
        url = demo.get_url(file_name="demo_export.xlsx")
        """
        super(ListExport, self).__init__(
            export_data, header=self.header, company_name=company_name, auto_filter=auto_filer,
            is_fill_remark=is_fill_remark, column_width=column_width
        )

    def many_write(self):

        for i, sheet_data in enumerate(self.export_data):
            sheet_name = sheet_data.get("sheet_name", f"sheet{i}")
            _data = sheet_data.get("body", [])
            header = sheet_data.get("header", [])
            headers = [h["label"] for h in header]
            fields = [h["property"] for h in header]
            clean_data = self.handle_data(_data, fields=fields)

            self.write(
                sheet_name=sheet_name, sheet_data=clean_data, sheet_header=headers
            )

    def save(self):
        # if not self._stream:
        self.many_write()
        self.sheet_format()
        self.workbook.close()
            # self._stream = self.output.getvalue()
            # self.output.close()
        # return self._stream


# keys = ["wechat_res: spdpd_", "wechat_res: ZY-Official", "wechat_res: camera-man-cn", "wechat_res: iloveCineHello",
#         "wechat_res: mengmawuxian", "wechat_res: spdpd_"
#         ]


def get_data_from_cache(biz_names):
    res = dict.fromkeys(biz_names)

    for _name in biz_names:
        _key = f"wechat_res: {_name}"
        keys = cache.hkeys(_key)
        if b"total" in keys:
            keys.remove(b'total')

        data = cache.hmget(_key, keys)
        res[_name] = sorted([json.loads(d) for d in data], key=lambda x: x["datetime"], reverse=True)
    return res


def save_excel(data=None, file_name="excel.xlsx"):
    """
    保存为excel
    :param file_name: 擦行间文件名
    :param data: 需要保存的数据 {"sheet_name": "", "data": [], "header": []}
    :return:
    """
    header = ("公众号", "标题", "文章链接", "时间", "阅读量", "在看", "点赞", "评论数")
    fields = ("chat_title", "title", "url", "datetime", "read_num", "like_num", "old_like_num", "comment_count")

    def handle_row(row):
        return [row[f] for f in fields]

    workbook = xlsxwriter.Workbook(file_name)
    for _biz_name, sheet_data in data.items():
        sheet_name = sheet_data[0].get("chat_title", _biz_name)
        # sheet_data = _d.get("data")
        _sheet = workbook.add_worksheet(sheet_name)
        _sheet.write_row(0, 0, header)
        for i, row in enumerate(sheet_data):
            i += 1
            row["datetime"] = str(datetime.datetime.fromtimestamp(row["datetime"]))
            _row = handle_row(row)
            _sheet.write_row(i, 0, _row)

        # 设置宽度
        _sheet.set_column("A:H", 15)
        _sheet.set_column("B:C", 60)

    workbook.close()


data = get_data_from_cache(["ZY-Official", "TheMediastorm", "camera-man-cn", "iloveCineHello", "mengmawuxian",
                            "spdpd_", "TheMediastorm"])

# data = [{"sheet_name": "智云稳定器", "data": data}]
save_excel(data=data, file_name="公众号.xlsx")

