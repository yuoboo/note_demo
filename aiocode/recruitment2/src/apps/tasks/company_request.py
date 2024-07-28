import asyncio

from celery_worker import celery_app
from business.configs.b_company_request import CompanyRequestBusiness
import logging

logger = logging.getLogger("celery.worker")
logger1 = logging.getLogger('celery.task')
logger2 = logging.getLogger('sanic.root')


@celery_app.task
def test_logger():
    logger.info("[recruitment2 task test log] this is task worker log")
    logger1.info("[recruitment2 task test log] this is task worker log1")
    logger2.info("[recruitment2 task test log] this is task worker log2")

    async def _worker():
        logger1.info("[recruitment2 task test log] this is task worker log11")
        logger2.info("[recruitment2 task test log] this is task worker log22")

        from business.configs.b_eliminated_reason import EliminatedReasonBusiness
        await EliminatedReasonBusiness.get_list_with_pagination(
            company_id="f79b05ee3cc94514a2f62f5cd6aa8b6e", limit=20, page=1, reason_step=1
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_worker())


@celery_app.task
def open_async_task(company_id: str, user_id: str):
    """
    异步开通招聘
    """
    async def _helper():
        await CompanyRequestBusiness.open_async(company_id, user_id)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_helper())
