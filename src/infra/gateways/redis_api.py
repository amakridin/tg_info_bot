import asyncio
import aioredis
from typing import Any
from config import REDIS_HOST, REDIS_PORT


class RedisApi:
    def __init__(self, db: int = 0):
        self.redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=db)

    async def set(self, key: Any, value: Any):
        await self.redis.set(name=str(key), value=str(value))

    async def get(self, key: Any):
        res = await self.redis.get(name=str(key))
        if res:
            return res.decode()

    async def delete(self, key: Any):
        return await self.redis.delete(str(key))

    async def close(self):
        await self.redis.close()

#
# async def run():
#     r = ApiRedis()
#     await r.set("qwe", "asd")
#     res = await r.get("qwe")
#     print(res)
#     await r.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(run())