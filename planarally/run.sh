#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

cd /planarally

cp -n  server_config.cfg /config/
cp  /config/server_config.cfg /planarally/

python -u planarally.py
