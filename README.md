#### 项目目录结构
```shell
(env) zhxfei@HP-ENVY:~/workspace/netease/EaseMonitor$ ls -l
总用量 48
drwxrwxr-x  6 zhxfei zhxfei 4096 4月   1 00:08 agent     # agent 源码目录
-rw-rw-r--  1 zhxfei zhxfei  935 4月   1 00:08 agentd_run.py # agent 启动入口
-rwxrwxr-x  1 zhxfei zhxfei 3765 4月   1 00:08 agent_run.sh  # agent 起停脚本
drwxrwxr-x  4 zhxfei zhxfei 4096 4月   1 00:08 api           # api 源码目录
-rw-rw-r--  1 zhxfei zhxfei 1623 4月   1 00:08 api_run.py    # api 启动入口
-rw-rw-r--  1 zhxfei zhxfei  291 4月   1 00:08 Dockerfile    # dockerfile文件
-rw-rw-r--  1 zhxfei zhxfei  368 4月   1 00:08 requirments.txt   # 项目的依赖文件
-rwxrwxr-x  1 zhxfei zhxfei  424 4月   1 00:08 run.sh        # dockerfile依赖的 run
drwxrwxr-x  6 zhxfei zhxfei 4096 4月   1 00:08 storage       # storage 源码目录
-rw-rw-r--  1 zhxfei zhxfei  970 4月   1 00:08 storage_run.py # storage 启动入口
drwxrwxr-x 11 zhxfei zhxfei 4096 4月   1 00:08 transfer      # transfer 源码目录
-rw-rw-r--  1 zhxfei zhxfei  946 4月   1 00:08 transfer_run.py  # transfer 启动入口

```
##### Agent
```shell
(env) zhxfei@HP-ENVY:~/workspace/netease/EaseMonitor$ tree -L 2 agent
agent
├── agent_config.json   # agent 配置文件
├── collector              # 一系列的Agent收集指标的模块
│   ├── conn_status.py      # 网络连接相关
│   ├── cpu_status.py       # cpu指标相关
│   ├── data_collector_func.py  # 对上层暴露出的收集方法, 有了这个文件 增加收集指标只需要将对应的收集方法写到这个文件里面即可,主程序不需要修改
│   ├── file_system.py      # 文件系统相关
│   ├── __init__.py
│   ├── mem_status.py       # 内存指标相关
│   ├── net_dev.py          # 网络接口相关
│   └── system_status.py    # 系统相关,主要是load
├── config                  
│   ├── config_parser.py    # 配置文件的parse,主要是json 文件load到 dict
│   └── __init__.py
├── __init__.py
├── monitor_agentd          
│   ├── agentd.py           # 主要的逻辑
│   └── __init__.py
└── rpc                     # 上报指标的rpc client
    ├── __init__.py
    └── send_rpc_client.py

```

`Agent` 启动停止
```shell
usage()
{
    echo "Usage: agent_run.sh start|stop|restart|check|install|status"
}
```
##### transfer
```shell
(env) zhxfei@HP-ENVY:~/workspace/netease/EaseMonitor$ tree -L 2 transfer
transfer
├── config      # 配置文件的parse,主要是json 文件load到 dict
│   ├── config_parser.py
│   └── __init__.py
├── conn_pool   # 后端的连接,目前就是一个redis连接
│   ├── conn_pools.py
│   └── __init__.py
├── exceptions  # 简单的异常定义, 目前只是一个Queue满的exception
│   ├── __init__.py
│   └── queue_exception.py
├── httpd       # common API ,用于处理http request
│   ├── __init__.py
│   └── recv_http_server.py
├── __init__.py
├── routing      # 主要的逻辑:数据的路由, 定义了数据转发的逻辑
│   ├── __init__.py
│   └── router.py       
├── rpc         # agent上报的rpc server,用于处理agent request
│   ├── data_process.py
│   ├── __init__.py
│   └── recv_rpc_server.py
├── sender      # 发送模块, 目前处于废弃中,在考虑是否可以去掉redis直接讲数据通过rpc的形式转发到storage
│   ├── __init__.py
│   └── send_rpc_client.py
├── transfer_config.json   # 配置文件
├── transfer_queue
│   ├── conn_queue.py   # queue层面的封装
│   └── __init__.py
└── utils       # 一些工具, 主要被用到的是对入口数据的规整,一些不符合格式的指标上报给去掉
    ├── consistant_hash.py
    ├── data_formater.py
    └── __init__.py

9 directories, 22 files
```
##### storage
```shell
(env) zhxfei@HP-ENVY:~/workspace/netease/EaseMonitor$ tree -L 2 storage
storage
├── config      # 配置文件的parse,主要是json 文件load到 dict
│   ├── config_parser.py
│   └── __init__.py
├── db
│   ├── __init__.py
│   └── mongo_clt.py        # 一个mongodb的client, 数据写入的逻辑
├── __init__.py
├── puller                  # puller: 从redis队列中pull数据的逻辑
│   ├── data_puller.py
│   └── __init__.py
├── storage_config.json     # 配置文件
└── storager
    ├── __init__.py
    └── storager.py         # 主要的逻辑, 代码的组织
```

##### API
```shell
(env) zhxfei@HP-ENVY:~/workspace/netease/EaseMonitor$ tree -L 2 api
api
├── common
│   ├── __init__.py
│   └── mongo_clt.py        # 创建mongo的连接
├── __init__.py
└── resources               # 资源
    ├── host_list.py        # 主机维度的资源, ip and hostname
    ├── __init__.py     
    ├── metric_list.py      # 指标的资源, 指标的种类
    └── monitor_data.py     # 具体监控指标的数据资源

2 directories, 7 files

```
