#!/bin/bash
set -e

CONFIG_PATH=/data/options.json

cd /app

JWT_SECRET=$(jq --raw-output '.JWT_SECRET' $CONFIG_PATH)
echo "JWT_SECRET: ${JWT_SECRET}"
export JWT_SECRET="${JWT_SECRET}"

INSECURE_COOKIES=$(jq --raw-output '.INSECURE_COOKIES' $CONFIG_PATH)
echo "INSECURE_COOKIES: ${INSECURE_COOKIES}"
export INSECURE_COOKIES="${INSECURE_COOKIES}"

node index.js