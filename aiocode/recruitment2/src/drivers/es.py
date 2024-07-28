from __future__ import absolute_import

from aioelasticsearch import Elasticsearch
from cached_property import cached_property

from configs import config


class ES:
    @cached_property
    async def default_es(self) -> Elasticsearch:
        engine = Elasticsearch(config['ELASTICSEARCH_HOSTS'])
        return engine


es = ES()


__all__ = ['es', ]
