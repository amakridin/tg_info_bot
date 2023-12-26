import asyncio
from typing import Any

import aioredis

from get_config import get_key_config


class RedisApi:
    def __init__(self):
        self.redis = aioredis.Redis(
            host=get_key_config("REDIS_HOST"),
            port=int(get_key_config("REDIS_PORT")),
            db=int(get_key_config("REDIS_DB")),
        )

    async def set(self, key: Any, value: Any):
        await self.redis.set(name=str(key), value=str(value))

    async def hash_map_set_key(self, key: Any, item_id: Any, item_value: Any):
        await self.redis.hset(name=str(key), key=str(item_id), value=str(item_value))

    async def hash_map_set_mapping(self, key: Any, mapping: dict[Any, Any]):
        await self.redis.hset(name=key, mapping=mapping)

    async def hash_map_get_item(self, key: Any, item_id: Any):
        res = await self.redis.hget(name=str(key), key=str(item_id))
        if res:
            return res.decode()

    async def get(self, key: Any):
        res = await self.redis.get(name=str(key))
        if res:
            return res.decode()

    async def delete(self, key: Any):
        return await self.redis.delete(str(key))

    async def close(self):
        await self.redis.close()


#
async def run():
    r = RedisApi()
    await r.hash_map_set_key("hello", "key1", "value1")
    print(await r.hash_map_get_item("hello", "key1"))


if __name__ == "__main__":
    asyncio.run(run())
