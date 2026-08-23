import redis
from typing import Optional, overload
from core.Schemas.Proxy import Proxy

def is_vaild_proxy(data):
    #判断proxy格式是否正确
    if not data:
        return False
    # 认证代理格式：user:pass@ip:port，先去掉认证部分
    if is_auth_proxy(data):
        data = data.split("@")[1]
    parts = data.split(":")
    if len(parts) < 2:
        return False
    ip, port = parts[0], parts[1]
    return is_ip_valid(ip) and is_port_valid(port)

def is_ip_valid(ip):
    if is_auth_proxy(ip):
        ip=ip.split("@")[1]
    a=ip.split(".")
    if len(a)!=4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i<0 or i>225:
            return False
    return True

def is_port_valid(port):
    return port.isdigit()

def is_auth_proxy(data:str)->bool:
    return "@" in data

@overload
def convent_proxy_or_proxies(data: str) -> Optional[Proxy]: ...
@overload
def convent_proxy_or_proxies(data: list) -> list[Proxy]: ...
def convent_proxy_or_proxies(data):
    if not data:
        return None
    # 单个字符串：转换成一个 Proxy
    if isinstance(data, str):
        data = data.strip()
        if not is_vaild_proxy(data):
            return None
        if is_auth_proxy(data):
            host, port = extract_auth_proxy(data)
        else:
            host, port, *_ = data.split(":")
        return Proxy(host=host, port=int(port))
    # 列表：转换成一个 Proxy 列表
    if isinstance(data, list):
        result: list[Proxy] = []
        for item in data:
            item = item.strip()
            if not is_vaild_proxy(item):
                continue
            if is_auth_proxy(item):
                host, port = extract_auth_proxy(item)
            else:
                host, port, *_ = item.split(":")
            result.append(Proxy(host=host, port=int(port)))
        return result
    return None

def extract_auth_proxy(data:str):
    auth=data.split('@')[0]
    ip_port=data.split('@')[1]
    ip=ip_port.split(':')[0]
    port=ip_port.split(':')[1]
    host=auth+"@"+ip
    return host,port

if __name__ == '__main__':
    proxy = 'test1234:test5678.@117.68.216.212:32425'
    print(extract_auth_proxy(proxy))
