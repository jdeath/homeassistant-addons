#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

SEARXNG_ENGINE_API_BASE_URL=$(jq --raw-output '.SEARXNG_ENGINE_API_BASE_URL' $CONFIG_PATH)
echo "SEARXNG_ENGINE_API_BASE_URL: ${SEARXNG_ENGINE_API_BASE_URL}"
export SEARXNG_ENGINE_API_BASE_URL="${SEARXNG_ENGINE_API_BASE_URL}"

cd /app
python mcp_server.py --http