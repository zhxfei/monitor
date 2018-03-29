#!/bin/bash

if [ ! $# -eq 1 ]; then
    exit 2
fi

case $1 in
    "agent")
        python3 agentd_run.py -c agent/agent_config.json
        ;;
    "transfer")
        python3 transfer_run.py -c transfer/transfer_config.json
        ;;
    "storage")
        python3 storage_run.py -c storage/storage_config.json
        ;;
    "api")
        python3 api_run.py -a ${API_HOST} -p ${API_PORT}
        ;;
    *)
        exit 1
        ;;
esac

exit 0
