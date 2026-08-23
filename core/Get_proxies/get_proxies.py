import json
from loguru import logger
import requests
import asyncio
from settings import PROXY_NUMBER_MAX
from core.Schemas.Proxy import Proxy
from core.Process.store import RedisClient


class Proxygetter(object):
    #代理获取逻辑
    def __init__(self):
        self.url = 'https://proxy.scdn.io/api/get_proxy.php'#公开代理网站
        self.redis = RedisClient()
        self.payload = {'protocol': 'all', 'count': '60'}

    def getip(self):
        import requests, json
        resp = requests.get(url=self.url, params=self.payload).text
        js_resp = json.loads(resp)
        ip_list = js_resp["data"]["proxies"]
        for i in ip_list:
            host, port = i.split(':')
            yield Proxy(host=host, port=int(port))

    async def is_full(self):
        return await self.redis.count() >= PROXY_NUMBER_MAX

    async def run(self):
        if await self.is_full():         
            logger.info("Pool is full")
            return
        for proxy in self.getip():
            await self.redis.add(proxy=proxy) 
            logger.info(f"Added {proxy.string()}")

if __name__ == '__main__':
    async def main():
        g = Proxygetter()
        await g.run()
    asyncio.run(main())
