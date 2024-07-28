# -*- coding: utf-8 -*-
import base64
import datetime
import json
from functools import wraps

from sanic import request, response
from sanic.response import HTTPResponse
from sanic.views import HTTPMethodView
from configs import config
from utils import client
from utils.client import HttpClient
from utils.logger import app_logger
from error_code import Code
from utils.strutils import uuid2str
from kits.exception import AuthenticationFailed, ServiceError

app_env = config.get("APP_ENV")

proj_name = config.get('PROJECT_NAME', None)


class BasicObject(dict):
    def __getattr__(self, key):
        return self.get(key, None)


AUTH_TOKEN_URL = {
    'local': "http://intranet-dev.2haohr.com/account/v4/token_auth_info/",
    'dev': "http://intranet-dev.2haohr.com/account/v4/token_auth_info/",
    'test': "http://intranet-test.2haohr.com/account/v4/token_auth_info/",
    'production': "http://intranet.2haohr.com/account/v4/token_auth_info/",
}


class AccessTokenInfo:
    """
    https://dianmi.feishu.cn/docs/doccnG6kPMRbrw0yzpCo4VuQmkd
    """

    def __init__(self, request: request.Request, token_key: str = "tokeninfo"):
        self._request = request
        self._token_key = token_key

    def get_request_accesstoken(self):
        accesstoken = self._request.headers.get('accesstoken')
        if not accesstoken:
            raise Code.UNAUTHORIZED
        return accesstoken

    def get_request_tokeninfo(self):
        tokeninfo = self._request.headers.get(self._token_key)
        if tokeninfo:
            token_info = self.decode_tokeninfo(tokeninfo)
            if app_env != 'production':
                app_logger.info("[tokeninfo] {}".format(token_info))
            return token_info

    @staticmethod
    def decode_tokeninfo(tokeninfo):
        tokeninfo_data = base64.standard_b64decode(tokeninfo)
        tokeninfo_data = json.loads(tokeninfo_data)
        return tokeninfo_data

    async def get_token_auth_info(self):
        accesstoken = self.get_request_accesstoken()
        params = {'accesstoken': accesstoken, 'project': proj_name}
        try:
            url = AUTH_TOKEN_URL.get(app_env)
            res = await HttpClient.get(url, params=params)
            if app_env != "production":
                app_logger.info("获取账号中心认证: url-{}, res - {}".format(url, res))

            if not res or res['resultcode'] != 200:
                raise Exception(u'获取账号中心认证失败, 状态码: {}, 参数: {}'.format(res['resultcode'], params))

            if res["data"]:
                return res['data']
        except Exception as e:
            app_logger.error(u'获取账号中心认证失败，原因：{}'.format(e))
            return dict()


async def hr_authentication(request: request.Request):
    """
    用户身份认证middleware
    """
    tokeninfo = request.headers.get("tokeninfo", None)
    auth_info = {}

    if tokeninfo:
        # 经过网关
        auth_info = base64.standard_b64decode(tokeninfo)
        if app_env != 'production':
            app_logger.info("[tokeninfo] {}".format(auth_info))
        auth_info = json.loads(auth_info)
    else:
        # 网关没有获取到信息
        accesstoken = request.headers.get('accesstoken', None)
        if not accesstoken:
            raise AuthenticationFailed
        try:
            url = config.get('AUTH_HR_URL', None)
            if not url:
                app_logger.error("无法找到hr鉴权URL配置")
                raise AuthenticationFailed
            headers = {
                'accesstoken': accesstoken,
                'project': config.get('PROJECT_NAME', None)
            }
            results = await client.http_client(url, headers=headers)

            if results and 'resultcode' in results and results['resultcode'] == 200 and 'data' in results:
                auth_info = results.get('data', {})
        except Exception as e:
            app_logger.error('用户中心token授权错误, err: {}'.format(str(e)))
            raise AuthenticationFailed

    if 'user' in auth_info:
        user = BasicObject(auth_info['user'])
        request.ctx.user = user
        request.ctx.user_id = uuid2str(user.id)
        # TODO 需要在开发的时候， 加上user_id和company_id， 用于access日志
    else:
        raise AuthenticationFailed
    if 'company' in auth_info:
        company = BasicObject(auth_info['company'])
        request.ctx.company = company
        request.ctx.company_id = uuid2str(company.id)
    if 'company_user' in auth_info:
        request.ctx.company_user = BasicObject(auth_info['company_user'])


async def employee_authentication(request: request.Request):
    """
    员工身份认证
    """
    tokeninfo = request.headers.get("tokeninfo-emp", None)
    auth_info = {}

    if tokeninfo:
        # 经过网关
        auth_info = base64.standard_b64decode(tokeninfo)
        if app_env != 'production':
            app_logger.info("[tokeninfo] {}".format(auth_info))
        auth_info = json.loads(auth_info)
    else:
        # 网关没有获取到信息
        accesstoken = request.headers.get('accesstoken', None)
        if not accesstoken:
            raise AuthenticationFailed
        try:
            url = config.get('AUTH_EMPLOYEE_URL', None)
            key = config.get('AUTH_EMPLOYEE_KEY', None)
            if not url:
                app_logger.error("无法找到员工鉴权URL配置")
                raise AuthenticationFailed
            params = {"token": accesstoken, "project": config.get('PROJECT_NAME', None)}
            headers = {"x-authkey": key, 'Accept': 'application/json'}
            results = await HttpClient.get(url, params=params, headers=headers)
            if results and 'resultcode' in results and results['resultcode'] == 200 and 'data' in results:
                auth_info = results['data']['res_data']['person']
        except Exception as e:
            app_logger.error('员工token授权错误, err: {}'.format(str(e)))
            raise AuthenticationFailed

    if auth_info:
        request.ctx.user = BasicObject(auth_info)
        # TODO 需要在开发的时候， 加上user_id和company_id， 用于access日志
    else:
        raise AuthenticationFailed


async def hr_authentication_v4(request: request.Request):
    """
    HR 统一账号之后使用此校验
    """
    _token = AccessTokenInfo(request)
    auth_info = _token.get_request_tokeninfo()
    if not auth_info:
        auth_info = await _token.get_token_auth_info()

    if not auth_info:
        raise Code.UNAUTHORIZED

    if 'eebo_user' in auth_info:
        user = BasicObject(auth_info['eebo_user'])
        request.ctx.user = user
        request.ctx.user_id = uuid2str(user.id)
    else:
        raise Code.UNAUTHORIZED
    if 'company' in auth_info:
        company = BasicObject(auth_info['company'])
        request.ctx.company = company
        request.ctx.company_id = uuid2str(company.id)
    if 'company_user_admin' in auth_info:
        request.ctx.company_user = BasicObject(auth_info['company_user_admin'])


async def app_user_authentication_v4(request: request.Request):
    """
    应用级用户验证  小程序 app ...
    :param request:
    :return:
    """
    _token = AccessTokenInfo(request, "tokeninfo-emp")
    # auth_info = _token.get_request_tokeninfo()
    #
    # if not auth_info:
    auth_info = await _token.get_token_auth_info()

    if not auth_info:
        raise Code.UNAUTHORIZED

    app_user = auth_info.get("app_user", {})
    if not app_user:
        raise Code.UNAUTHORIZED

    eebo_user = auth_info.get('eebo_user', {})
    employee = auth_info.get("company_user_employee", {})

    user_data = {
        "id": app_user.get("id"),
        "wechat_app_id": app_user.get("app_id"),
        "openid": app_user.get("openid"),
        "unionid": app_user.get("unionid", ""),
        "mobile": eebo_user.get("mobile", ""),
        "company_id": employee.get('company_id'),
        "emp_id": employee.get('employee_id'),
    }

    user = BasicObject(**user_data)
    request.ctx.user = user


async def wechat_authentication(request: request.Request):
    """
    微信身份鉴权
    """
    return await app_user_authentication_v4(request)


async def hr_permission(request: request.Request, permission):
    """
    HR权限验证
    """
    return await has_hr_permission(request.ctx.company_id, request.ctx.user_id, permission)


async def has_hr_permission(company_id: str, user_id: str, permission):
    """
    HR权限验证
    """
    try:
        url = config.get('PERMISSION_HR_URL', None)
        if not url:
            app_logger.error("无法找到hr权限验证URL配置")
            raise ServiceError(Code.FORBIDDEN)
        params = {
            "user_id": user_id,
            "company_id": company_id,
            "permission": permission
        }
        headers = {
            'project': config.get('PROJECT_NAME', None)
        }
        results = await client.http_client(url, data=params, headers=headers, method="POST")

        if results and 'resultcode' in results and results['resultcode'] == 200 and 'data' in results:
            return True
        else:
            raise ServiceError(Code.FORBIDDEN)
    except Exception as e:
        app_logger.error('员工token授权错误, err: {}'.format(str(e)))
        raise ServiceError(Code.FORBIDDEN)


async def validate_permission(company_id: str, user_id: str, permission: str):
    """
    校验权限
    """
    try:
        url = config.get('PERMISSION_HR_URL', None)
        if not url:
            app_logger.error("无法找到hr权限验证URL配置")
            raise Exception("权限校验地址参数缺失: PERMISSION_HR_URL")

        params = {
            "user_id": user_id,
            "company_id": company_id,
            "permission": permission
        }
        headers = {
            'project': config.get('PROJECT_NAME', None)
        }
        results = await client.http_client(url, data=params, headers=headers, method="POST")

        if results.get("resultcode") == 200:
            return True
        else:
            return False

    except Exception as e:
        app_logger.error('权限校验失败, err: {}'.format(str(e)))
        # raise Code.FORBIDDEN
        raise Exception(f"用户中心token授权错误，错误原因-{e}")


def hr_authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            await hr_authentication(request)
            response = await f(request, *args, **kwargs)
            return response

        return decorated_function

    return decorator


def employee_authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            await employee_authentication(request)
            response = await f(request, *args, **kwargs)
            return response

        return decorated_function

    return decorator


def wechat_authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            await wechat_authentication(request)
            response = await f(request, *args, **kwargs)
            return response

        return decorated_function

    return decorator


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


class BaseView(HTTPMethodView):
    def _data(self, data, results=True, resultcode=200, msg='ok'):
        return {
            "result": results,
            "resultcode": resultcode,
            "msg": msg if msg else msg,
            "data": data,
            'errormsg': ''
        }

    def data(self, data, results=True, resultcode=200, msg='ok'):
        # return response.json(
        #     self._data(data, results, resultcode, msg)
        # )

        return HTTPResponse(
            json.dumps(self._data(data, results, resultcode, msg), cls=DateEncoder),
            content_type='application/json',
        )

    def js(self, data, callback='callback', results=True, resultcode=200, msg='ok'):
        return HTTPResponse(
            callback + "(" + json.dumps(self._data(data, results, resultcode, msg), cls=DateEncoder) + ")",
            content_type='application/javascript',
        )

    def _build_wtf_errors(self, errors: dict):
        ret = []
        for field, field_errors in errors.items():
            if isinstance(field_errors, str):
                buf = f'{field}: {"".join(field_errors)}'
            else:
                buf = f'{field}: {str(field_errors)}'
            ret.append(buf)
        return ' | '.join(ret)

    def error(self, errormsg, results=False, resultcode=400):
        if isinstance(errormsg, dict):
            errormsg = self._build_wtf_errors(errormsg)
        return response.json({
            'errormsg': errormsg,
            'result': results,
            'resultcode': resultcode,
        })

    def error_js(self, errormsg, callback='callback', results=False, resultcode=400):
        if isinstance(errormsg, dict):
            errormsg = self._build_wtf_errors(errormsg)
        return HTTPResponse(
            callback + '(' + json.dumps({
                'errormsg': errormsg,
                'result': results,
                'resultcode': resultcode,
            }, cls=DateEncoder) + ')',
            content_type='application/javascript',
        )


class HRBaseView(BaseView):
    """
    hr鉴权view
    """
    decorators = [hr_authorized()]
    permissions = {}

    async def permission_valid(self, request, permission):
        for perm in permission.split('|'):
            result = await hr_permission(request, perm)
            if result:
                return True
        return False

    async def dispatch_request(self, request, *args, **kwargs):
        method = request.method.lower()
        if method in self.permissions:
            if not await self.permission_valid(request, self.permissions[method]):
                return self.error('无权限', resultcode=403)

        handler = getattr(self, method, None)
        ret = handler(request, *args, **kwargs)
        if callable(ret):
            return ret
        return await ret


class EmployeeBaseView(BaseView):
    """
    员工鉴权view
    """
    decorators = [employee_authorized()]
    _hr_id = None

    async def get_hr_id(self, request):
        if self._hr_id:
            return self._hr_id

        from business.configs.b_common import CommonBusiness
        self._hr_id = await CommonBusiness.get_hr_by_emp_id(
            request.ctx.user.company_id, request.ctx.user.emp_id
        )
        if not self._hr_id:
            raise ServiceError(Code.FORBIDDEN)
        return self._hr_id

    async def has_hr_permission(self, company_id, user_id, permission):
        return await has_hr_permission(company_id, user_id, permission)


class WeChatBaseView(BaseView):
    """
    微信登陆鉴权
    """
    decorators = [wechat_authorized()]
