#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

GEO=$(jq --raw-output '.GEO // empty' $CONFIG_PATH)
LANG=$(jq --raw-output '.LANG // empty' $CONFIG_PATH)

echo $GEO
echo $LANG

cd /config
python3 /app/main.py -g $GEO -l $LANG
#python3 /app/main.py