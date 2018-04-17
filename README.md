#### 项目目录结构
```shell
zhxfei@HP-ENVY:~/PycharmProjects/EaseMonitorBak$ ls -l
总用量 64
drwxrwxr-x 7 zhxfei zhxfei 4096 4月  17 12:44 agent      # agent 源码目录
-rw-rw-r-- 1 zhxfei zhxfei 1002 4月   8 13:30 agentd_run.py  # agent 启动入口
-rwxrwxr-x 1 zhxfei zhxfei 3765 3月  31 19:13 agent_run.sh   # agent 起停脚本
drwxrwxr-x 5 zhxfei zhxfei 4096 3月  30 03:17 api            # api 源码目录
-rw-rw-r-- 1 zhxfei zhxfei 1575 4月   8 14:16 api_run.py     # api 启动入口
drwxrwxr-x 7 zhxfei zhxfei 4096 4月   2 23:21 common         # 项目组件复用的模块
-rw-rw-r-- 1 zhxfei zhxfei  291 3月  30 03:17 Dockerfile     # dockerfile文件
drwxrwxr-x 6 zhxfei zhxfei 4096 3月  30 03:17 env
-rw-rw-r-- 1 zhxfei zhxfei 5365 4月   1 00:35 README.md
-rw-rw-r-- 1 zhxfei zhxfei  368 3月  30 03:17 requirments.txt     # 项目的依赖文件
-rwxrwxr-x 1 zhxfei zhxfei  424 3月  31 22:40 run.sh          # dockerfile依赖的 run
drwxrwxr-x 6 zhxfei zhxfei 4096 4月   8 14:02 storage         # storage 源码目录
-rw-rw-r-- 1 zhxfei zhxfei 1052 4月   8 14:16 storage_run.py     # storage 启动入口
drwxrwxr-x 8 zhxfei zhxfei 4096 4月   4 01:57 transfer           # transfer 源码目录
-rw-rw-r-- 1 zhxfei zhxfei 1032 4月   4 01:47 transfer_run.py      # transfer 启动入口

```
##### Agent
```shell
zhxfei@HP-ENVY:~/PycharmProjects/EaseMonitorBak$ tree -L 2 -I "*.pyc|__pycache__"  agent
agent
├── agent_config.json        # agent 配置文件
├── agentd
│   ├── agentd.py            # 主程序和主要的逻辑
│   └── __init__.py
├── collect
│   ├── collector.py        # 数据收集模块
│   ├── __init__.py
│   └── sys_status_collect.py   # 数据收集的方法
├── config
│   ├── config_parser.py       # agent的配置parse
│   ├── default_config.py       # agent的默认配置
│   └── __init__.py
├── __init__.py
└── sender                  # 数据发送模块
    ├── base_sender.py
    ├── __init__.py
    └── rpc_client_sender.py

4 directories, 13 files

```

`Agent` 启动停止
```shell
usage()
{
    echo "Usage: agent_run.sh start|stop|restart|check|install|status"
}
```

**Agent图示**

![Alt text](http://occwxjjdz.bkt.clouddn.com/agent_design%283%29.png "agent")

##### transfer
```shell
zhxfei@HP-ENVY:~/PycharmProjects/EaseMonitorBak$ tree -L 2 -I "*.pyc|__pycache__"  transfer
transfer
├── config
│   ├── config_parser.py         # 配置文件的parse
│   ├── default_config.py        # 默认配置
│   └── __init__.py
├── __init__.py
├── receiver        # 数据接收组件
│   ├── data_process.py
│   ├── __init__.py
│   ├── recv_http_server.py     # common API ,用于处理http request
│   └── recv_rpc_server.py      #  agent上报的rpc server,用于处理agent request
├── routing
│   ├── __init__.py
│   └── router.py       # 主要的逻辑:数据的路由, 定义了数据转发的逻辑
├── sender          # 数据发送模块
│   ├── __init__.py
│   ├── redis_sender.py
│   └── send_rpc_client.py
├── transfer_config.json    # 配置文件
└── utils        # 一些工具, 主要被用到的是对入口数据的规整
    ├── data_formater.py
    └── __init__.py

5 directories, 16 files


```
##### storage
```shell
zhxfei@HP-ENVY:~/PycharmProjects/EaseMonitorBak$ tree -L 2 -I "*.pyc|__pycache__"  storage
storage
├── config
│   ├── config_parser.py
│   ├── default_config.py
│   └── __init__.py
├── __init__.py
├── puller              # 从redis中取数据
│   ├── data_puller.py
│   └── __init__.py
├── storage_config.json # 配置文件
└── storager
    ├── __init__.py
    └── storager.py     # 主要的逻辑

3 directories, 9 files

```

##### API
```shell
zhxfei@HP-ENVY:~/PycharmProjects/EaseMonitorBak$ tree -L 2 -I "*.pyc|__pycache__"  api
api
├── common
│   ├── __init__.py
│   ├── mongo_clt.py         # 创建mongo的连接
│   └── mongo_setting.py     # mongodb 的配置
├── __init__.py
└── resources
    ├── host_list.py        # 主机维度的资源, ip and hostname
    ├── __init__.py
    ├── metric_list.py       # 指标的资源, 指标的种类
    └── monitor_data.py     # 具体监控指标的数据资源

2 directories, 8 files

```
