import asyncio
import functools
import time
from contextlib import contextmanager
from sanic.log import logger


def timeit(func):
    @contextmanager
    def wrapping_logic():
        start_time = time.perf_counter_ns()
        yield
        logger.info(f'方法 {func.__name__} 耗时 {(time.perf_counter_ns() - start_time) / 1000 / 1000} ms')

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic():
                return func(*args, **kwargs)
        else:
            async def tmp():
                with wrapping_logic():
                    return (await func(*args, **kwargs))
            return tmp()
    return wrapper
