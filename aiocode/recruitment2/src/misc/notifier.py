# coding=utf-8
from __future__ import unicode_literals, print_function

import asyncio
import datetime
import inspect
import logging
import traceback
from functools import wraps

import requests

from configs import config
from utils.client import HttpClient


env = config.get('RT_ENV')
project_name = config.get('PROJECT_NAME')


class Notifier(object):
    log_url = config['WECHAT_HOOK_LOG_URL']
    exception_url = config['WECHAT_HOOK_SENTRY_URL']

    @classmethod
    async def notify_async(cls, markdown_content, level='info'):
        # payload = {
        #     'msgtype': 'markdown',
        #     'markdown': {
        #         'content': markdown_content
        #     }
        # }
        # try:
        #     if level == 'info':
        #         await HttpClient.post(cls.log_url, json_body=payload)
        #     else:
        #         await HttpClient.post(cls.exception_url, json_body=payload)
        # except Exception:
        #     logging.error(traceback.format_exc())
        return

    @classmethod
    async def error_async(cls, msg):
        if env != 'local':
            await cls.notify_async(msg, level='error')

    @classmethod
    async def notify_api_error(cls, api_path, method, request_body, ak, exc):
        msg = f'❌❌❌{project_name}[{env}]API异常\nFULL_URL:{api_path}\nMETHOD:{method}\nREQUEST_BODY:{request_body}\nACCESSTOKEN:{ak}\n{exc}'
        await cls.error_async(msg)

    @classmethod
    async def notify_sanic_api_error(cls, request):
        try:
            exc = traceback.format_exc()
            logging.error(exc)
            try:
                body = request.body.decode('utf-8')
            except Exception:
                body = request.body

            ak = request.headers.get('accesstoken')
            method = request.method
            await cls.notify_api_error(request.url, method, body, ak, exc)
        except Exception as e:
            logging.exception(e)

    @classmethod
    def notify_markdown(cls, markdown_content, url):
        payload = {
            'msgtype': 'markdown',
            'markdown': {
                'content': markdown_content
            }
        }
        requests.post(url, json=payload)

    @classmethod
    def exception(cls, msg):
        if env == 'local':
            return
        try:
            msg = '❌❌❌异常信息`{}-{}`\n{}'.format(project_name, env, msg)
            cls.notify_markdown(msg, cls.exception_url)
        except Exception:
            pass

    @classmethod
    def error(cls, msg):
        logging.error(msg)
        if env == 'local':
            return
        try:
            msg = f'❌❌❌错误信息`{project_name}-{env}`{datetime.datetime.now()}\n{msg}， 请查看错误日志'
            cls.notify_markdown(msg, cls.exception_url)
        except Exception:
            pass

    @classmethod
    def log(cls, msg, *envs):
        if not envs:
            envs = ('dev', 'test')
        if env not in envs:
            return
        try:
            info = inspect.getframeinfo(inspect.stack()[1][0])
            msg = '👉`{}-{}`\n{}\n{}'.format(project_name, env,
                '{}第{}行'.format(info.filename, info.lineno), msg)
            cls.notify_markdown(msg, cls.log_url)
        except Exception:
            logging.exception(traceback.format_exc())
            pass

    @classmethod
    def build_push_commits_markdown(cls, body):
        """
        body是从Gitlab Hook Message里面提取出来的有用的信息
        """
        content = '''
        `{push_user}` pushed {total_commits_count} new commits to [{project_name}({ref})]({project_url})
        '''.format(
            push_user=body['push_user_name'],
            total_commits_count=body['total_commits_count'],
            project_name=body['project_name'],
            project_url=body['project_homepage'],
            ref=body['ref']
        ).strip()
        comments_buff = []
        for commit in body['commits']:
            commit_markdown = '>[{}]({}) {} {}'.format(
                commit['id'][:8], commit['url'], commit['author_name'],
                commit['message']
            )
            comments_buff.append(commit_markdown)
        content += '\n'
        content = content + ''.join(comments_buff)
        return content

    @classmethod
    def _extract_hook_message_for_push(cls, body):
        raw_commits = body['commits']
        commits = []
        for commit in raw_commits:
            commits.append({
                'id': commit['id'],
                'message': commit['message'],
                'url': commit['url'],
                'author_name': commit['author']['name'],
                'timestamp': commit['timestamp']
            })

        return dict(
            ref=body['ref'],
            total_commits_count=body['total_commits_count'],
            push_user_name='{}[{}]'.format(body['user_username'], body['user_email']),
            project_name=body['project']['name'],
            project_homepage=body['project']['homepage'],
            commits=commits
        )

    @classmethod
    def send_api_exc(cls, api_path, method, request_body, ak, exc):
        msg = f'❌❌❌{project_name}[{env}]API异常\nFULL_URL:{api_path}\nMETHOD:{method}\nREQUEST_BODY:{request_body}\nACCESSTOKEN:{ak}\n{exc}'
        logging.exception(msg)
        # cls.exception(msg)


def error_report(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            exc = traceback.format_exc()
            exc = f'❌❌❌{project_name}[{env}]异步任务执行出错!!!\n任务名: {func.__name__}, args: {args}\nkwargs:{kwargs}\n{exc}'
            logging.exception(exc)
            if env != 'local':
                # TODO 发给SENTRY
                try:
                    Notifier.exception(exc)
                except Exception:
                    pass

    return wrapper


if __name__ == '__main__':
    async def _helper():
        await Notifier.notify_async('test async')


    asyncio.get_event_loop().run_until_complete(_helper())
