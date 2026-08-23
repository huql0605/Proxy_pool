import redis
import redis.asyncio as aioredis
from random import choice
from core.Schemas.Proxy import Proxy
import asyncio
from core.utils.Proxy import convent_proxy_or_proxies,is_vaild_proxy
from loguru import logger
from settings import (
    PROXY_SCORE_MAX,
    PROXY_SCORE_MIN,
    REDIS_HOST,
    REDIS_KEY,
    REDIS_PASSWORD,
    REDIS_PORT,
    PROXY_SCORE_INIT,
    REDIS_DB
)
class RedisClient(object):
    def __init__(self,host=REDIS_HOST,password=REDIS_PASSWORD,port=REDIS_PORT,db=REDIS_DB) -> None:
        self.host=host
        self.port=port
        self.password=password
        self.db = aioredis.Redis(
            db=db,
            host=self.host,
            password=self.password,
            decode_responses=True
        )#初始化数据库

    async def exists(self,proxy:Proxy , redis_key=REDIS_KEY)->bool:
        score=await self.db.zscore(redis_key, proxy.string())
        return score is not None

    async def add(self , proxy:Proxy ,score=PROXY_SCORE_INIT):
        if not is_vaild_proxy(f"{proxy.host}:{proxy.port}"): #判断proxy是否合法
            logger.info(f'invalid proxy {proxy}, throw it')
            return
        if not await self.exists(proxy):
            added = await self.db.zadd(REDIS_KEY, {proxy.string(): score})
            return added == 1
        return False

    async def random(self, redis_key=REDIS_KEY) -> Proxy | None: #获取一个随机代理
        # 1. 优先取满分代理
        proxies = await self.db.zrangebyscore(redis_key, PROXY_SCORE_MAX, PROXY_SCORE_MAX)
        if proxies:
            return convent_proxy_or_proxies(choice(proxies))

        # 2. 没有满分代理，则从高分段取前100名
        proxies = await self.db.zrevrange(redis_key, 0, 99)  # 索引0~99为前100名
        if proxies:
            return convent_proxy_or_proxies(choice(proxies))

        return None


    async def decrease(self, proxy: Proxy):
        score = await self.db.zscore(REDIS_KEY, proxy.string())
        if score is not None and score > PROXY_SCORE_MIN:
            logger.info(f'{proxy.string()} current score {score}, decrease 1')
            return await self.db.zincrby(REDIS_KEY, -1, proxy.string())
        else:
            logger.info(f'{proxy.string()} current score {score}, remove')
            return await self.db.zrem(REDIS_KEY, proxy.string())

    async def max(self, proxy: Proxy):
        logger.info(f'{proxy.string()} is valid, set to {PROXY_SCORE_MAX}')
        return await self.db.zadd(REDIS_KEY, {proxy.string(): PROXY_SCORE_MAX})

    async def count(self) -> int:
        return await self.db.zcard(REDIS_KEY)

    async def all(self):
        data = await self.db.zrangebyscore(REDIS_KEY, PROXY_SCORE_MIN, PROXY_SCORE_MAX)
        if isinstance(data, list):
            return [proxy for proxy in (convent_proxy_or_proxies(item) for item in data) if proxy]
        return convent_proxy_or_proxies(data)

    async def batch(self, start, end):
        # 左闭右闭区间 [start, end-1]，与 Python 切片左闭右开一致
        data = await self.db.zrange(REDIS_KEY, start, end - 1)
        if isinstance(data, list):
            return [proxy for proxy in (convent_proxy_or_proxies(item) for item in data) if proxy]
        return convent_proxy_or_proxies(data)

    async def close(self):
        await self.db.close()


# ============= 使用示例（获取真实值） =============
if __name__ == "__main__":
    async def demo():
        client = RedisClient()

        # 构造一个测试代理（请根据你实际 Proxy 类调整）
        # 假设 Proxy 有 host, port 属性，string() 返回 "host:port"
        test_proxy = Proxy(host="192.168.1.1", port=8080)

        # 添加代理
        result = await client.add(test_proxy, score=5)
        print("add result:", result)  # True / False

        # 随机取出一个代理
        proxy_obj = await client.random()
        if proxy_obj:
            print("随机取到的代理:", proxy_obj.string())  # 真实字符串，不是协程
        else:
            print("池子为空")

        # 关闭连接
        await client.close()

    # 在同步代码中运行异步函数，获取真实结果
    asyncio.run(demo())
