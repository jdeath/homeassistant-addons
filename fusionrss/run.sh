#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

PASSWORD=$(jq --raw-output '.PASSWORD // empty' $CONFIG_PATH)
echo "PASSWORD: ${PASSWORD}"
export PASSWORD="${PASSWORD}"

./fusion
