#!/bin/bash
# description: this is agent control script for Easemonitor
# __author__ = 'zhxfei'

WORKSPACE=$(cd $(dirname $0) && pwd)
PID_FILE=${WORKSPACE}/agent.pid
AGENT_RUN_PY=${WORKSPACE}/agentd_run.py
CONF_PATH=${WORKSPACE}/agent/agent_config.json
REQUIRMENT_FILE=${WORKSPACE}/requirments.txt
REQUIRMENT_PACKS="zerorpc gevent psutil"

usage()
{
    echo "Usage: agent_run.sh start|stop|restart|check|install|status"
}

check_pidfile()
{
    if [ -f $PID_FILE ];then
        PID=$(cat $PID_FILE)
        if [ -n $PID ]; then
            ps -p $PID &> /dev/null
            return $? 
        fi
    fi
    return 1
}

agent_start()
{
    check_pidfile
    if [ $? -eq 0 ]; then
        echo "[INFO] agent is already running..."
        return 3
    fi
    
    if [ ! -r ${CONF_PATH} ]; then
        echo "[ERROR] config path not exists or not readable"
        return 4
    fi

    echo "[INFO] agent starting..."
    agent_run
    if [ $? -eq 0 ]; then
        echo "[INFO] agent starting succeed"
        return 0
    else
        echo "[INFO] agent starting failed"
        cat ${WORKSPACE}/nohup.out && rm -f nohup.out
        return 5
    fi
}

agent_run()
{
    nohup ${WORKSPACE}/env/bin/python ${AGENT_RUN_PY} -c ${CONF_PATH} &>/dev/null &

    PID=$! && sleep 1
    ps -p $PID &> /dev/null
    if [ $? -eq 0 ];then
        echo $PID > ${PID_FILE} && return 0 
    else
        return 1
    fi
}

agent_stop()
{
    check_pidfile
    if [ $? -eq 1 ];then
        echo "[INFO] agent is not running..."
        return 3
    fi
    kill $PID && sleep 1 && rm -f $PID_FILE
    if [ $? -eq 0 ];then
        echo "[INFO] agent stop succeed"
        return 0
    else
        echo "[INFO] agent stop failed"
        return 6
    fi
}

agent_restart()
{
    agent_stop
    sleep 1
    agent_start
}

agent_status()
{
    if [ -e ${PID_FILE} ];then
        echo "[INFO] agent is running..."
    else
        echo "[INFO] agent is not running..."
    fi

}

agent_check()
{
    if [ ! -d ${WORKSPACE}/env ];then
        echo [ERROR] virtual environment needed
        return 8
    fi
    for REQ in ${REQUIRMENT_PACKS}; do
        ${WORKSPACE}/env/bin/python -c "import ${REQ}" 
        if [ $? -gt 0 ];then
            echo "[INFO] Lack of dependence"
            return 7
        fi
    done
    echo "[INFO] no lack of dependence, you could try run"
    return 0
}

install_package()
{
    echo "[INFO] gcc, python3-dev python3-pip will install"
    check_os
    if [ $? -eq 1 ];then
        echo "[INFO] os release debian or ubuntu"
        sudo apt-get install -y gcc python3-dev python3-pip
    else
        echo "[INFO] os release redhat or centos"
        sudo yum install -y gcc python3-devel python3-pip
    fi
}

check_os()
{
    cat /proc/version | grep -iE 'debian|ubuntu' &> /dev/null && return 1
    cat /proc/version | grep -iE 'redhat|centos' &> /dev/null && return 2
    echo "[ERROR] Unsupport os release"
    exit 8
}

agent_install()
{
    install_package
    if [ $? -eq 0 ];then
        if [ ! -d ${WORKSPACE}/env ];then
            echo [INFO] virtual environment not exists
            virtualenv ${WORKSPACE}/env --python=python3
        fi
 
        ${WORKSPACE}/env/bin/pip install -r ${REQUIRMENT_FILE} -i https://pypi.douban.com/simple 
    fi
}

if [ $# != 1 ];then
    echo "[ERROR] parameter number error"
    usage
    exit 1
fi

case $1 in
    "start")
        agent_start
        ;;
    "stop")
        agent_stop
        ;;
    "restart")
        agent_restart
        ;;
    "check")
        agent_check
        ;;
    "install")
        agent_install
        ;;
    "status")
        agent_status
        ;;
    *)
        echo "[ERROR] unkown parameter"
        usage
        exit 2
esac

STATUS_CODE=$?
exit $STATUS_CODE
