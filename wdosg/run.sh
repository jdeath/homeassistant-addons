#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
cat /data/options.json

TWITCH_CLIENT_ID=$(jq --raw-output '.TWITCH_CLIENT_ID' $CONFIG_PATH)
echo "TWITCH_CLIENT_ID: ${TWITCH_CLIENT_ID}"
export TWITCH_CLIENT_ID="${TWITCH_CLIENT_ID}"

TWITCH_CLIENT_SECRET=$(jq --raw-output '.TWITCH_CLIENT_SECRET' $CONFIG_PATH)
echo "TWITCH_CLIENT_SECRET: ${TWITCH_CLIENT_SECRET}"
export TWITCH_CLIENT_SECRET="${TWITCH_CLIENT_SECRET}"


COMMAND="curl -X POST https://id.twitch.tv/oauth2/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'grant_type=client_credentials&client_id=$TWITCH_CLIENT_ID&client_secret=$TWITCH_CLIENT_SECRET' | jq -r '.access_token'"

TWITCH_APP_ACCESS_TOKEN=$(eval "$COMMAND")
echo "TWITCH_APP_ACCESS_TOKEN: ${TWITCH_APP_ACCESS_TOKEN}"
export TWITCH_APP_ACCESS_TOKEN="${TWITCH_APP_ACCESS_TOKEN}"


cd /app
node index