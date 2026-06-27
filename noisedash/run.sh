#!/bin/sh
set -e

NGINX_PORT="${INGRESS_PORT:-8099}"
APP_INTERNAL_PORT=1432

# Stamp the ingress port into the nginx config
sed -i "s/%%port%%/${NGINX_PORT}/" /etc/nginx/nginx.conf

# Start nginx in the background
nginx &

# Prepare app config directory
cd /config
sed -i 's&db/db.sqlite3&./db.sqlite3&g' /var/noisedash/server/db.js || true
mkdir -p /config/config || true
cp -n /var/noisedash/config/default.json /config/config/ || true

# Always ensure the app listens on the internal port (not the external one)
sed -i "s/\"listeningPort\": [0-9]*/\"listeningPort\": ${APP_INTERNAL_PORT}/" /config/config/default.json

# Patch the compiled JS bundle to set axios baseURL dynamically for ingress
/patch-axios.sh

# Start the app in the foreground on the internal port
node /var/noisedash/server/bin/www.js
