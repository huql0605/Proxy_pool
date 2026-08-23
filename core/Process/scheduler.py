import time
import importlib
import multiprocessing
import asyncio
import pathlib
import sys
from core.Process.api import app
from core.Get_proxies.get_proxies import Proxygetter
from core.Process.tester import Tester
from settings import APP_PROD_METHOD_GEVENT, APP_PROD_METHOD_MEINHELD, APP_PROD_METHOD_TORNADO, CYCLE_GETTER, CYCLE_TESTER, API_HOST, \
    API_THREADED, API_PORT, ENABLE_SERVER, IS_PROD, APP_PROD_METHOD, \
    ENABLE_GETTER, ENABLE_TESTER, IS_WINDOWS
from loguru import logger


if IS_WINDOWS:
    multiprocessing.freeze_support()

tester_process, getter_process, server_process = None, None, None


class Scheduler():
    """
    scheduler
    """

    def run_tester(self, cycle=CYCLE_TESTER):
        """
        run tester
        """
        if not ENABLE_TESTER:
            logger.info('tester not enabled, exit')
            return
        tester = Tester()
        loop = 0
        while True:
            logger.debug(f'tester loop {loop} start...')
            tester.run()
            loop += 1
            time.sleep(cycle)

    async def run_getter(self, cycle=CYCLE_GETTER):
        """
        run getter
        """
        if not ENABLE_GETTER:
            logger.info('getter not enabled, exit')
            return
      
        getter = Proxygetter()
        loop = 0
        while True:
            logger.debug(f'getter loop {loop} start...')
            await getter.run()
            loop += 1
            await asyncio.sleep(cycle)

    def _run_getter_sync(self, cycle):
    #同步包装，负责在子进程中启动事件循环并运行异步 getter
        asyncio.run(self.run_getter(cycle))

    def run_server(self):
        """
        run server for api
        """
        if not ENABLE_SERVER:
            logger.info('server not enabled, exit')
            return
        if IS_PROD:
            if APP_PROD_METHOD == APP_PROD_METHOD_GEVENT:
                try:
                    from gevent.pywsgi import WSGIServer
                except ImportError as e:
                    logger.exception(e)
                else:
                    http_server = WSGIServer((API_HOST, API_PORT), app)
                    http_server.serve_forever()

            elif APP_PROD_METHOD == APP_PROD_METHOD_TORNADO:
                try:
                    wsgi_module = importlib.import_module('tornado.wsgi')
                    httpserver_module = importlib.import_module('tornado.httpserver')
                    ioloop_module = importlib.import_module('tornado.ioloop')
                except ImportError as e:
                    logger.exception(e)
                else:
                    http_server = httpserver_module.HTTPServer(
                        wsgi_module.WSGIContainer(app))
                    http_server.listen(API_PORT)
                    ioloop_module.IOLoop.instance().start()

            

            else:
                logger.error("unsupported APP_PROD_METHOD")
                return
        else:
            app.run(host=API_HOST, port=API_PORT, threaded=API_THREADED, use_reloader=False)

    def run(self):
        global tester_process, getter_process, server_process
        try:
            logger.info('starting proxypool...')
            if ENABLE_TESTER:
                tester_process = multiprocessing.Process(target=self.run_tester)
                tester_process.start()  # 先启动再打印 pid，否则 pid 为 None
                logger.info(f'starting tester, pid {tester_process.pid}...')

            if ENABLE_GETTER:
                getter_process = multiprocessing.Process(target=self._run_getter_sync,args=(CYCLE_GETTER,))
                getter_process.start()
                logger.info(f'starting getter, pid {getter_process.pid}...')

            if ENABLE_SERVER:
                server_process = multiprocessing.Process(target=self.run_server)
                server_process.start()
                logger.info(f'starting server, pid {server_process.pid}...')

            # 等待进程结束
            if tester_process:
                tester_process.join()
            if getter_process:
                getter_process.join()
            if server_process:
                server_process.join()

        except KeyboardInterrupt:
            logger.info('received keyboard interrupt signal')
            # 终止已启动的进程
            if tester_process:
                tester_process.terminate()
            if getter_process:
                getter_process.terminate()
            if server_process:
                server_process.terminate()
        finally:
            # 确保 join 后再判断状态，并处理可能为 None 的情况
            if tester_process:
                tester_process.join()
                logger.info(f'tester is {"alive" if tester_process.is_alive() else "dead"}')
            else:
                logger.info('tester was not started')

            if getter_process:
                getter_process.join()
                logger.info(f'getter is {"alive" if getter_process.is_alive() else "dead"}')
            else:
                logger.info('getter was not started')

            if server_process:
                server_process.join()
                logger.info(f'server is {"alive" if server_process.is_alive() else "dead"}')
            else:
                logger.info('server was not started')

            logger.info('proxy terminated')


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
