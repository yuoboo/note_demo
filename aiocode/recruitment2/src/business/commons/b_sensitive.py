import asyncio

from services.s_https.s_sensitive import SensitiveService


class SensitiveBusiness(object):
    @classmethod
    async def get(cls, text: str, type: list) -> list:
        """
        根据类型和内容判断是否有敏感词
        """
        tasks = []
        for t in type:
            tasks.append(SensitiveService.get(text=text, type_=t))
        sensitive = []
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                sensitive.extend(result)
        return sensitive
