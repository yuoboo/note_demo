# coding: utf-8

class Code(object):
    SUCCESS = (200, 'success')
    UNAUTHORIZED = (401, '未认证')
    FORBIDDEN = (403, '无权限')
    NOT_FOUND = (404, '数据不存在')

    # 全局的业务代码，以 10 开头
    SYSTEM_ERROR = (10001, '服务器开小差了，请稍后重试~')
    PARAM_MISS = (10101, '参数缺失！')
    PARAM_ERROR = (10102, '参数错误！')
    OVER_FLOW = (10103, '超出访问次数限制！')
    NO_AUTH = (10201, '没有权限！')
    NO_USER = (10202, '获取不到用户！')
    NO_COMPANY = (10203, '获取不到该用户的企业！')
