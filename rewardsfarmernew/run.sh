#!/bin/bash
set -e

CONFIG_PATH=/data/options.json

cd /app

MODE=$(jq --raw-output '.MODE' $CONFIG_PATH)

if [[ "$MODE" == "signin" ]]; then
    python src/signin.py
else
    python src/main.py
fi