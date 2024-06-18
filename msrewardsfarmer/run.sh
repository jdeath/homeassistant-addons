#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

cp -ru /app/src /config/
cp -u /app/main.py /config/
cp -n /app/config.yaml /config/

cd /config
python3 /config/main.py
