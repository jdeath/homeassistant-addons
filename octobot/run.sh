#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

ln -s /opt/venv/bin/OctoBot /config/OctoBot || true

cd /config/
#cp -n /octobot/docker-entrypoint.sh .
./OctoBot
