import asyncio
from asyncio import TimeoutError

import aiohttp
from aiohttp import (
    ClientHttpProxyError,
    ClientOSError,
    ClientProxyConnectionError,
    ServerDisconnectedError,
)
from loguru import logger

from core.Schemas.Proxy import Proxy
from core.Process.store import RedisClient
from settings import TEST_BATCH, TEST_TIMEOUT, TEST_URL, TEST_VALID_STATUS

EXCEPTIONS=(
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError,
)

class Tester(object):

    def __init__(self) -> None:
        
        self.redis=RedisClient()
        self.loop=asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def test(self,proxy:Proxy):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                logger.debug(f'testing {proxy.string()}')
                async with session.get(TEST_URL, proxy=f'http://{proxy.string()}', timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT), allow_redirects=False) as respone:
                    if respone.status in TEST_VALID_STATUS:
                        await self.redis.max(proxy)
                        logger.debug(f'proxy {proxy.string()} is valid ,set max score')
                    else:
                        await self.redis.decrease(proxy)
                        logger.debug(f'proxy {proxy.string()} is invalid , decreade score')

            except EXCEPTIONS:
                await self.redis.decrease(proxy)
                logger.debug(f'proxy {proxy.string()} is invalid , decrease score')

    @logger.catch
    def run(self):
        logger.info('starting tester..')
        # RedisClient.count is async, run it in the loop to get the integer
        count= self.loop.run_until_complete(self.redis.count())
        logger.debug(f'{count} proxies to test')
        for i in range(0,count,TEST_BATCH):
            start,end=i,min(i+TEST_BATCH,count)
            logger.debug(f'testing proxies fromm {start} to {end} indices')
            # fetch proxies from Redis
            proxies = self.loop.run_until_complete(self.redis.batch(start, end))
            if proxies is None:
                continue
            if isinstance(proxies, Proxy):
                proxies = [proxies]
            # create and run test coroutines concurrently
            tasks = [self.test(proxy) for proxy in proxies]
            self.loop.run_until_complete(asyncio.gather(*tasks))


if __name__=='__main__':
    tester=Tester()
    tester.run()
