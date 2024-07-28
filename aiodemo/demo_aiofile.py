import asyncio
import json
from pprint import pprint

import aioredis
import aiofiles
import aiopath
import aiohttp
import jsonlines

"""
https://segmentfault.com/q/1010000040062125
"""



jsonl_list = [
    {"_id": 10000, "input": "你谁是0"},
    {"_id": 10001, "input": "我是谁1"},
    {"_id": 10002, "input": "他是谁2"},
    {"_id": 10003, "input": "他是谁3"},
    {"_id": 10004, "input": "他是谁4"},
    {"_id": 10005, "input": "他是谁5"},
]

file_name = './files/1.jsonl'


def write_jsonl():
    with jsonlines.open('./files/1.jsonl', 'w') as f_jsonl:
        for line in jsonl_list:
            f_jsonl.write(line)
    print('jsonl生成完成')


jsonl_files = [
    'lcc.jsonl', 'lcc_e.jsonl', 'qasper.jsonl', 'qasper_e.jsonl'
]

async def read_lines(path):
    print(f"read_lines: {path}")
    async with aiofiles.open(path, mode='r', encoding='utf8') as f:
        return (
            json.loads(line) for line in await f.readlines()
        )

async def read_line():  #
    async with aiofiles.open(file_name, 'r', encoding='utf8') as f_line:
        async for line in f_line:
            yield json.loads(line)


async def run():
    # read_lines
    lines = await read_lines('./files/1.jsonl')
    print(lines)

    # read_line
    async for line in read_line():
        print(line)

    _redis = await aioredis.from_url("redis://localhost:6379/6")
    # 从缓存读取文件，如果没有就加载文件
    for _file in jsonl_files:
        _name = _file.rsplit('.', 1)[0]
        lcc_datasets = await _redis.hgetall(f'lb:lcc:{_name}')
        if not lcc_datasets:
            lcc_datasets = list(await read_lines(f'./files/{_file}'))
            await _redis.hmset(f'lb:lcc:{_name}', mapping={_["_id"]: json.dumps(_) for _ in lcc_datasets})
        print(_name)

if __name__ == '__main__':
    write_jsonl()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

