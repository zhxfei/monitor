def register_url(api_rest):
    from api.monitor.resources.host_list import HostList, IpList
    from api.monitor.resources.metric_list import MetricList
    from api.monitor.resources.data import MonitorData
    from api.monitor.resources.user import User, UserList
    from api.monitor.resources.strategies import StrategyList, Strategy
    from api.monitor.resources.alerter import Alert, Alerts
    from api.monitor.resources.policy import Policy, PolicyList
    from api.monitor.resources.alarm import Alarm, AlarmList
    from api.monitor.resources.judge_item import JudgeItemList

    api_rest.add_resource(MonitorData, '/monitor/v1/items')
    api_rest.add_resource(HostList, '/monitor/v1/hosts')
    api_rest.add_resource(MetricList, '/monitor/v1/metrics')
    api_rest.add_resource(IpList, '/monitor/v1/ips')
    api_rest.add_resource(User, '/monitor/v1/user/<string:user_id>')
    api_rest.add_resource(UserList, '/monitor/v1/users')
    api_rest.add_resource(StrategyList, '/monitor/v1/strategies')
    api_rest.add_resource(Strategy, '/monitor/v1/strategy/<string:strategy_id>')
    api_rest.add_resource(Alert, '/monitor/v1/alert/<string:alert_id>')
    api_rest.add_resource(Alerts, '/monitor/v1/alerts')
    api_rest.add_resource(Policy, '/monitor/v1/policy/<string:monitor_id>')
    api_rest.add_resource(PolicyList, '/monitor/v1/policies')
    api_rest.add_resource(Alarm, '/monitor/v1/alarm/<string:alarm_id>')
    api_rest.add_resource(AlarmList, '/monitor/v1/alarms')
    api_rest.add_resource(JudgeItemList, '/monitor/v1/judge_items')
