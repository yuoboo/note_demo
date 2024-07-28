from __future__ import absolute_import

import asyncio
import base64
from io import BytesIO
import xlsxwriter
from xlsxwriter.format import Format as _Format
from utils.qiniu import upload_base64


async def upload2qiniu(file_name, stream, dead_time=None):
    """
    上传excel文件至七牛
    :param file_name 文件名
    :param stream binary
    :param dead_time 过期时间
    :return:
    """
    b64_res = base64.b64encode(stream).decode()
    if dead_time is not None:
        res = await upload_base64(3, False, b64_res, file_name=file_name, dead_time=dead_time)
    else:
        res = await upload_base64(3, False, b64_res, file_name=file_name)
    data = res.get('data') or dict()
    return data.get('url') or ''


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
        self.output = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output)
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

    def get_value(self):
        if not self._stream:
            self.write()
            self.sheet_format()
            self.workbook.close()
            self._stream = self.output.getvalue()
            self.output.close()
        return self._stream

    async def get_url(self, file_name, dead_time=None):
        """
        获取导出链接
        :return:
        """
        stream = self.get_value()
        return await upload2qiniu(file_name=file_name, stream=stream, dead_time=dead_time)


class ListExport(BaseExport):
    """
    一般列表的导出基类
    """
    header = []
    fields = []
    remark = ""

    def __init__(self, export_data: list, sheet_name: str = "sheet1", company_name: str = None):
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

    def get_value(self):
        if not self._stream:
            self.many_write()
            self.sheet_format()
            self.workbook.close()
            self._stream = self.output.getvalue()
            self.output.close()
        return self._stream


if __name__ == "__main__":

    class Demo(ListExport):
        remark = """这是测试企业表头"""
        header = ["姓名", "年龄"]
        fields = ["name", "age"]


    async def test_export():
        export_data = [
            {"name": "张杰", "age": 18},
            {"name": "周杰伦", "age": 28},
            {"name": "刘德华", "age": 40}
        ]
        d = Demo(export_data=export_data, sheet_name="测试sheet名称")
        url = await d.get_url("测试的鹅鹅鹅.xlsx")
        print(111, url)

    async def _test_many_export2():
        demo_data = [
            {
                "sheet_name": "部门",
                "body": [
                    {"name": "部门1", "dep_count": 10, "leader": "张三", "sup_dep": ""},
                    {"name": "部门2", "dep_count": 20, "leader": "李四", "sup_dep": ""},
                    {"name": "部门22", "dep_count": 10, "leader": "李四", "sup_dep": "部门2"},
                    {"name": "部门3", "dep_count": 40, "leader": "王五", "sup_dep": ""},
                ],
                "header": [
                    {"label": "部门名称", "property": "name"},
                    {"label": "部门人数", "property": "dep_count"},
                    {"label": "负责人", "property": "leader"},
                    {"label": "上级部门", "property": "sup_dep"},
                ]
            },
            {
                "sheet_name": "职位",
                "body": [
                    {"name": "职位1", "dep": "部门1", "total": 10, "remark": "备注1"},
                    {"name": "职位2", "dep": "部门2", "total": 2, "remark": "备注2"},
                    {"name": "职位3", "dep": "", "total": 3, "remark": "备注3"},
                    {"name": "职位4", "dep": "", "total": 0, "remark": "备注4"},
                ],
                "header": [
                    {"label": "职位名称", "property": "name"},
                    {"label": "所属部门", "property": "dep"},
                    {"label": "招聘人数", "property": "total"},
                    {"label": "备注", "property": "remark"},
                ]
            }
        ]

        demo = ManySheetListExport(export_data=demo_data)
        url = await demo.get_url("stishsihsi.xlsx")
        print(222, url)

    async def _test():
        await asyncio.gather(test_export(), _test_many_export2())

    asyncio.run(_test())
