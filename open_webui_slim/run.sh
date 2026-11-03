#!/bin/bash
set -e

CONFIG_PATH=/data/options.json

ls

WEBUI_SECRET_KEY=$(jq --raw-output '.WEBUI_SECRET_KEY' $CONFIG_PATH)
echo "WEBUI_SECRET_KEY: ${WEBUI_SECRET_KEY}"
export WEBUI_SECRET_KEY="${WEBUI_SECRET_KEY}"

./start.sh
