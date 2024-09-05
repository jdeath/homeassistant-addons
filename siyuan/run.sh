#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

ACCESS_CODE=$(jq --raw-output '.ACCESS_CODE' $CONFIG_PATH)
echo "ACCESS_CODE: ${ACCESS_CODE}"

/opt/siyuan/kernel --workspace=/config/ --accessAuthCode=${ACCESS_CODE}