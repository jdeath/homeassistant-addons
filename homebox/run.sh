#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

HBOX_OPTIONS_ALLOW_REGISTRATION=$(jq --raw-output '.HBOX_OPTIONS_ALLOW_REGISTRATION // empty' $CONFIG_PATH)
echo "HBOX_OPTIONS_ALLOW_REGISTRATION: ${HBOX_OPTIONS_ALLOW_REGISTRATION}"
export HBOX_OPTIONS_ALLOW_REGISTRATION="${HBOX_OPTIONS_ALLOW_REGISTRATION}"

HBOX_AUTH_API_KEY_PEPPER=$(jq --raw-output '.HBOX_AUTH_API_KEY_PEPPER // empty' $CONFIG_PATH)
echo "HBOX_AUTH_API_KEY_PEPPER: ${HBOX_AUTH_API_KEY_PEPPER}"
export HBOX_AUTH_API_KEY_PEPPER="${HBOX_AUTH_API_KEY_PEPPER}"

# Start nginx for ingress (listens on 8099, proxies to app on 7745)
NGINX_PORT="${INGRESS_PORT:-8099}"
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf
nginx &

# Start the app on internal port 7745
/app/api
