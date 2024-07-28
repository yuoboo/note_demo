from celery.utils.log import get_task_logger
from kombu import Queue

from . import config

celery_logger = get_task_logger('recruitment2_worker')

TASK_QUEUES = [
    Queue("eebo.ehr.recruitment2.common.get_ip_task", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.common.subscription_event_task", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.company_request.open_async_task", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.company_request.test_logger", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.portals.wework.update_wework_external_contact", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.talent_activate.sms_notify_candidates", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.talent_activate.fail_talent_activate_status", routing_key="eebo.ehr.recruitment2"),
    Queue("eebo.ehr.recruitment2.portals.portals_export_task_center", routing_key="eebo.ehr.recruitment2"),
]


CELERY_ROUTES = {
    # common
    'apps.tasks.common.get_ip_task': {
        "queue": 'eebo.ehr.recruitment2.common.get_ip_task',
        "routing_key": 'eebo.ehr.recruitment2'
    },
    'apps.tasks.common.subscription_event_task': {
        "queue": 'eebo.ehr.recruitment2.common.subscription_event_task',
        "routing_key": 'eebo.ehr.recruitment2'
    },

    # portals
    'apps.tasks.portals.wework.update_wework_external_contact': {
        "queue": 'eebo.ehr.recruitment2.portals.wework.update_wework_external_contact',
        "routing_key": 'eebo.ehr.recruitment2'
    },

    # configs/company_request
    'apps.tasks.company_request.open_async_task': {
        "queue": 'eebo.ehr.recruitment2.company_request.open_async_task',
        "routing_key": 'eebo.ehr.recruitment2'
    },
    'apps.tasks.company_request.test_logger': {
        "queue": 'eebo.ehr.recruitment2.company_request.test_logger',
        "routing_key": 'eebo.ehr.recruitment2'
    },
    'apps.tasks.talent_activate.sms_notify_candidates': {
        "queue": 'eebo.ehr.recruitment2.talent_activate.sms_notify_candidates',
        "routing_key": 'eebo.ehr.recruitment2'
    },
    'apps.tasks.talent_activate.fail_talent_activate_status': {
        "queue": 'eebo.ehr.recruitment2.talent_activate.fail_talent_activate_status',
        "routing_key": 'eebo.ehr.recruitment2'
    },
    'apps.tasks.portals.portals_export_task_center': {
        "queue": 'eebo.ehr.recruitment2.portals.portals_export_task_center',
        "routing_key": 'eebo.ehr.recruitment2'
    },
}

CELERY_INCLUDE = [
    'apps.tasks.common',
    'apps.tasks.company_request',
    'apps.tasks.portals.wework',
    'apps.tasks.talent_activate',
    'apps.tasks.portals',
]

CELERY_CONFIG = {
    "CELERY_QUEUES": TASK_QUEUES,
    "CELERY_ROUTES": CELERY_ROUTES,
    "CELERY_DEFAULT_QUEUE": 'eebo.ehr.recruitment2.default',
    "CELERY_DEFAULT_EXCHANGE_TYPE": "direct",
    "CELERY_DEFAULT_ROUTING_KEY": 'eebo.ehr.recruitment2',
    "CELERY_BROKER": config.get('CELERY_BROKER'),
}
