from typing import Optional

from attr import attr ,attrs

@attrs
class Proxy(object):
    #定义一个代理的正确格式
    host: str = attr(default=None)
    port: Optional[int] = attr(default=None)

    def __str__(self) -> str:
        
        return f'{self.host}:{self.port}'
    
    def string(self):

        return self.__str__()


if __name__=='__main__':
    proxy=Proxy(host='192.168.88.130',port=6379)
    print(proxy)
    print('proxy', proxy.string())
