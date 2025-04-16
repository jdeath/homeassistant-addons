#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

GEO=$(jq --raw-output '.GEO // empty' $CONFIG_PATH)
LANG=$(jq --raw-output '.LANG // empty' $CONFIG_PATH)

echo $GEO
echo $LANG

cd /config
#cp -n /app/config.yaml .
#cp -n /app/accounts.json.sample ./accounts.json
#cp -n /app/.template-config-private.yaml ./config-private.yaml

python3 /app/main.py -g $GEO -l $LANG
#python3 /app/main.py