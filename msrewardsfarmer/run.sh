#!/bin/sh
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

cd /config
python3 /app/main.py