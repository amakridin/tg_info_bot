import aioredis
from tg_simple_math_bot.settings import Settings

def log_commands(func):
    async def wrapper(*args, **kwargs):
        key = str(kwargs.get("chat_id") or (args[1] if len(args) > 1 else None))
        value = str(kwargs.get("command") or (args[2] if len(args) > 2 else None))
        res = await func(*args, **kwargs)
        await redis_lpush(key, value)
        return res
    return wrapper


async def redis_lpush(key, value):
    redis = aioredis.from_url(Settings.REDIS_DSN)
    await redis.lpush(key, value)
