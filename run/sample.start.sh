#!/bin/bash

# set your Anthropic API key here
export ANTHROPIC_API_KEY=""

# clickhouse is used to store your chat history
# choose a strong password to protect it
export CLICKHOUSE_USER="myuser"
export CLICKHOUSE_PASSWORD="mypassword"
export CLICKHOUSE_TABLE="chat_history"

# For personal wechat user, there're 2 options for WECHATY_PUPPET
# "wechaty-puppet-wechat" uses web login, which is free but unstable and your
#     account has a high risk of being blocked by tencent
# "wechaty-puppet-padlocal" is more stable and according to wechaty team is less
#     likely to get your account blocked
export WECHATY_PUPPET="wechaty-puppet-padlocal"
# padlocal token is required if using "wechaty-puppet-padlocal"
# get token from http://pad-local.com/
export WECHATY_PUPPET_PADLOCAL_TOKEN="puppet_padlocal_"
export WECHATY_PUPPET_SERVER_PORT=8888
# WECHATY_TOKEN should be set to your own secret token
export WECHATY_TOKEN="mywechatytoken"
export WECHATY_PUPPET_SERVICE_ENDPOINT="localhost:$WECHATY_PUPPET_SERVER_PORT"


mkdir -p clickhouse/data
mkdir -p clickhouse/log
mkdir -p clickhouse/users.d

sudo -E docker run -d \
    --name chatsum-clickhouse \
    --ulimit nofile=262144:262144 \
    -v $(pwd)/clickhouse/data:/var/lib/clickhouse/ \
    -v $(pwd)/clickhouse/log:/var/log/clickhouse-server/ \
    -v $(pwd)/clickhouse/users.d:/etc/clickhouse-server/users.d/ \
    -p 18123:8123 -p 19000:9000 \
    -e CLICKHOUSE_USER \
    -e CLICKHOUSE_PASSWORD \
    -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 \
    clickhouse/clickhouse-server

sudo -E docker run -d \
    --name chatsum-wechaty \
    --rm \
    -e WECHATY_LOG="verbose" \
    -e WECHATY_PUPPET \
    -e WECHATY_PUPPET_PADLOCAL_TOKEN \
    -e WECHATY_PUPPET_SERVER_PORT \
    -e WECHATY_TOKEN \
    -p "$WECHATY_PUPPET_SERVER_PORT:$WECHATY_PUPPET_SERVER_PORT" \
    wechaty/wechaty:0.65

python ../src/app.py
