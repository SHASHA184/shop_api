from aioredis import Redis, from_url
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
import json


class RedisService:
    def __init__(self):
        self._redis = None

    async def redis(self):
        if self._redis is None:
            self._redis = await from_url(
                f"redis://{REDIS_HOST}:{REDIS_PORT}", password=REDIS_PASSWORD
            )
        return self._redis

    async def set_json(self, key: str, value: object, path: str = "$"):
        redis = await self.redis()
        if not isinstance(value, str):
            value = json.dumps(value)
        await redis.execute_command("JSON.SET", key, path, value)

    async def get_json(self, key: str, path: str = "$") -> dict:
        redis = await self.redis()
        result = await redis.execute_command("JSON.GET", key, path)
        if result is None:
            return None
        result = json.loads(result)
        if isinstance(result[0], dict):
            print(result)
            return result
        elif isinstance(result[0], list):
            result = result[0]
            return [json.loads(item) for item in result]

    async def close(self):
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()

    async def clear_cache(self):
        redis = await self.redis()
        await redis.flushall()

    async def clear_cache_by_key(self, key: str):
        redis = await self.redis()
        await redis.delete(key)

    async def clear_cache_by_pattern(self, pattern: str):
        redis = await self.redis()
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
