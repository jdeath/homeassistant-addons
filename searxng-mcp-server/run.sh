#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

SEARXNG_BASE_URL=$(jq --raw-output '.SEARXNG_BASE_URL' $CONFIG_PATH)
echo "SEARXNG_BASE_URL: ${SEARXNG_BASE_URL}"
export SEARXNG_BASE_URL="${SEARXNG_BASE_URL}"

cd /app
python server.py