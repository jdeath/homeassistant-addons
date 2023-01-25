#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

WG_HOST=$(jq --raw-output '.WG_HOST // empty' $CONFIG_PATH)
echo "WG_HOST: ${WG_HOST}"
export WG_HOST="${WG_HOST}"

PASSWORD=$(jq --raw-output '.PASSWORD // empty' $CONFIG_PATH)
echo "PASSWORD: ${PASSWORD}"
export PASSWORD="${PASSWORD}"

WG_PORT=$(jq --raw-output '.WG_PORT // empty' $CONFIG_PATH)
echo "WG_PORT: ${WG_PORT}"
export WG_PORT="${WG_PORT}"

WG_PERSISTENT_KEEPALIVE=$(jq --raw-output '.WG_PERSISTENT_KEEPALIVE // empty' $CONFIG_PATH)
echo "WG_PERSISTENT_KEEPALIVE: ${WG_PERSISTENT_KEEPALIVE}"
export WG_PERSISTENT_KEEPALIVE="${WG_PERSISTENT_KEEPALIVE}"

WG_DEFAULT_ADDRESS=$(jq --raw-output '.WG_DEFAULT_ADDRESS // empty' $CONFIG_PATH)
echo "WG_DEFAULT_ADDRESS: ${WG_DEFAULT_ADDRESS}"
export WG_DEFAULT_ADDRESS="${WG_DEFAULT_ADDRESS}"

WG_DEFAULT_DNS=$(jq --raw-output '.WG_DEFAULT_DNS // empty' $CONFIG_PATH)
echo "WG_DEFAULT_DNS: ${WG_DEFAULT_DNS}"
export WG_DEFAULT_DNS="${WG_DEFAULT_DNS}"

WG_ALLOWED_IPS=$(jq --raw-output '.WG_ALLOWED_IPS // empty' $CONFIG_PATH)
echo "WG_ALLOWED_IPS: ${WG_ALLOWED_IPS}"
export WG_ALLOWED_IPS="${WG_ALLOWED_IPS}"

WG_PATH=$(jq --raw-output '.WG_PATH // empty' $CONFIG_PATH)
echo "WG_PATH: ${WG_PATH}"
export WG_PATH="${WG_PATH}"

WG_POST_UP=$(jq --raw-output '.WG_POST_UP // empty' $CONFIG_PATH)
echo "WG_POST_UP: ${WG_POST_UP}"
export WG_POST_UP="${WG_POST_UP}"

WG_POST_DOWN=$(jq --raw-output '.WG_POST_DOWN // empty' $CONFIG_PATH)
echo "WG_POST_DOWN: ${WG_POST_DOWN}"
export WG_POST_DOWN="${WG_POST_DOWN}"

mkdir -p WG_PATH

/usr/bin/dumb-init node server.js