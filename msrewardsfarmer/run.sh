#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

cp -rn /app/src /config/
cp -n /app/main.py /config/
cp -n /app/config.yaml /config/

cd /config
python3 main.py