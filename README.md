# 爬虫代理池

## 项目介绍

- 参考《python3网络爬虫开发实战(第二版)》的代理池搭建 ，对此进行一些优化，使其适用于python3.14.5

- 按照本人的思路进行了一些改动，使其易于调试与使用

## 下载依赖

- uv : "uv pip install -r requirements.txt"

- pip : "pip install -r requirements.txt"

## 使用方法

- 在setting.py 设置 redis 的ip,port,password 默认数据库是2

- 在文件目录 \Proxy_pool 下运行 python -m core.Process.scheduler

- 在 "http://127.0.0.1:5555" 进入接口界面 "http://127.0.0.1:5555/random" 获取一个可用的随机代理

- 编写简单爬虫获取该代理

## 注意事项

- 本项目适用于python 3.14.5

- 代理池尽量运行长一点的时间再使用，以获得优质代理

- 默认爬取 "https://proxy.scdn.io/" 的免费代理使用 ，如有需要，请自行对 core/Get_proxies/get_proxies.py 的 Proxygetter.getip 进行修改以获取其他代理

