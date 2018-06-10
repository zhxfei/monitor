
#### 项目简介
`Ease-Monitor`是本人大学在毕业前尝试编写的一个分布式监控系统，目的是从开发的角度去了解一个监控系统的方方面面（实际上我只解决的一小部分问题-\_-!），所以还是仅供学习使用

其主要包含了数据采集、数据转发、数据存储、异常判定及告警、数据可视化五个功能模块。其架构图如下：

![Alt text](http://onpkiaecu.bkt.clouddn.com/Easemonitor%289%29.png)

其后端完全使用`Python`实现，前端的数据可视化和平台管理基于`Vue.js`实现

后端项目[地址](https://github.com/zhxfei/monitor)

前端项目[地址](https://github.com/zhxfei/monitor_frontend)
<!-- more -->
##### 数据采集和转发
`Agent`组件是监控系统的数据采集模块，目前其基于`psutil`采集了部分系统基础资源指标。在采集了系统资源之后，使用`ZeroRPC`上报给数据转发模块。目前`Agent`还处在雏形阶段,仅仅是数据采集...

数据转发组件提供了`ZeroRPC`的服务端接口和一个通用的`HTTP`接口，数据转发组件在收到上报的指标后会对数据的格式进行简单的检查。只要上报的数据符合格式，就会按照其配置文件中的配置规则进行转发。数据格式如下：

```json
{
	"value": 0,
	"timestamp": 1528557126,
	"counterType": "GAUGE",
	"step": 60,
	"metrics": "cpu.nice.percent",
	"tags": {          
		"host_ip": "182.254.155.58",
		"hostname": "sh.zhxfei.com"
	}
}
```
当`transfer`收到数据后，会将数据写入一个定长的内存队列，这个队列会被指定数量的`greenlet`监听并消费，`greenlet`会将数据向后端转发， 一般其会将每个指标数据转发到后端的异常判定和数据存储两个模块。

目前数据转发组件为异常判定和数据存储组件各自维护了一份`redis`列表，其会不断得`LPUSH`监控数据到后端去。

数据采集和数据转发的结构图如图所示：

![Alt text](http://onpkiaecu.bkt.clouddn.com/agent_transfer.png)

##### 数据存储
`storage`主要是数据的写入, 其主要是从`redis`队列中`pull`到一定条目的数据然后写入`Mongodb`，其目前只支持`Mongo`一种数据存储形式。

数据采集和数据转发的结构图如图所示：

![Alt text](http://onpkiaecu.bkt.clouddn.com/data_store.png)

##### 异常判定和告警
异常判定Watcher根据管理员配置的异常策略表达式对监控数据进行检查，对于判定出异常数据产生异常事件发送给告警模块，告警模块alert对异常事件进行处理，根据管理员配置的告警策略进行收敛告警。

数据采集和数据转发的结构图如图所示：

![Alt text](http://onpkiaecu.bkt.clouddn.com/data_judge.png)

##### 可视化和平台管理
数据可视化组件使用了较为新颖的MVVM的设计模式，前端使用`Vue.JS`，后端使用了`flask_restful`

其主要是为`Ease-Monitor`提供了监控数据的可视化、策略配置、用户管理、登录验证等功能。可视化组件结构图如下：

![Alt text](http://onpkiaecu.bkt.clouddn.com/data_vistual.png)


##### 部署
目前的想法是基于`docker-compose`,待功能完善再更新....


##### 效果
**机器基础资源预览**
![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_159.png)

![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_160.png)

**机器历史数据查询**
![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_161.png)

**机器指标对比**
![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_162.png)

**Strategy、alert、Policy**
`Strategy`是和`metrics`相关的监控策略描述，其定义监控的`metrics`，`alert`是和告警相关描述，其定义告警对象、告警媒介、告警收敛相关的信息。`Policy`是以机器、机器组为维度对`Strategy`和`alert`进行整合。
![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_164.png )

![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_165.png)

![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_166.png)

**用户管理**
对用户`CURD`，添加的用户才能进行登录。
![Alt text](http://onpkiaecu.bkt.clouddn.com/monitor%20-%20Google%20Chrome_167.png)

**告警**
目前只支持发邮件，支持简单的收敛规则，过滤同一个监控指标下一定时间内的告警。

![Alt text](http://onpkiaecu.bkt.clouddn.com/easemonitor_message.png)
