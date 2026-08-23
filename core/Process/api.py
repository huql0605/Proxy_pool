import asyncio
import pathlib
import sys
if __package__ is None:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from core.Schemas import Proxy
from core.Process.store import RedisClient
from flask import Flask,g
from core.Process.store import RedisClient
from settings import API_HOST,API_PORT,API_THREADED

__all__=['app']

app=Flask(__name__)

def get_conn():
    if not hasattr(g,'redis'):
        g.redis=RedisClient()
    return g.redis

@app.route('/')
def index():
    return '<h2>welcome to Proxypool</h2>'

@app.route('/random')
async def get_proxy():
    conn=get_conn()
    result=await conn.random()
    return result.string()

@app.route('/count')
async def get_couont():
    conn=await get_conn().count()
    return str(conn)

if __name__=='__main__':
    app.run(host=API_HOST,port=API_PORT,threaded=API_THREADED)
